import { IdentifyResult } from "../types/chat";
import { BACKEND_URL } from "../config";

// Real pill identification using backend API
export async function fakeIdentify(imageUri: string): Promise<IdentifyResult> {
  try {
    const formData = new FormData();
    formData.append("file", {
      uri: imageUri,
      name: "pill.jpg",
      type: "image/jpeg",
    } as any);
    // IMPORTANT: mode must be sent as form data, not URL query parameter
    formData.append("mode", "pill_id");

    const response = await fetch(`${BACKEND_URL}/register-drug-image`, {
      method: "POST",
      body: formData,
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const data = await response.json();
    console.log("📥 [PILL ID] Response:", JSON.stringify(data, null, 2));

    // Parse backend response
    const rawData = data.raw_data || {};
    const detectedFeatures = rawData.detected_features || {};
    const candidates = rawData.candidates || [];

    // Check if Gemini returned medications format (when pill name is very clear)
    const medications = rawData.medications || [];

    let formattedCandidates = [];

    if (medications.length > 0) {
      // Gemini recognized the pill clearly and returned medications format
      formattedCandidates = medications.map((med: any, index: number) => ({
        id: String(index),
        name: med.name || "Unknown",
        score: 100 - (index * 5),
        effect: med.effect || "",
        administer_method: med.administer_method || "",
      }));
    } else if (candidates.length > 0) {
      // Got candidates from 식약처 API or Local DB
      formattedCandidates = candidates.slice(0, 5).map((item: any, index: number) => ({
        id: item.ITEM_SEQ || item.item_seq || String(index),
        name: item.ITEM_NAME || item.item_name || "Unknown",
        score: item.match_score ? (item.match_score * 10) : (100 - (index * 5)), // 로컬 DB 점수 활용
        effect: item.EE_DOC_DATA || item.UD_DOC_DATA || item.chart || "", // chart는 로컬 DB의 모양 설명
        administer_method: item.ENTP_NAME || item.entp_name ? `제조사: ${item.ENTP_NAME || item.entp_name}` : "",
      }));
    }

    return {
      extracted_text: detectedFeatures.print_front || detectedFeatures.print_back || detectedFeatures.item_name || "인식된 텍스트 없음",
      best_match: formattedCandidates[0] || { id: "0", name: "약물을 찾을 수 없습니다", score: 0 },
      candidates: formattedCandidates,
    };
  } catch (error) {
    console.error("Pill identification API Error:", error);
    // Return error state
    return {
      extracted_text: "인식 실패",
      best_match: { id: "0", name: "분석 중 오류가 발생했습니다", score: 0 },
      candidates: [],
    };
  }
}

export async function callConsultationApi(drugName: string, topic: string, userId: string = "test_user"): Promise<string> {
  try {
    const response = await fetch(`${BACKEND_URL}/consult`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        drug_name: drugName,
        topic: topic,
        user_id: userId,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "서버 응답 에러");
    }

    // 백엔드는 { drug_name, selected_topic, advice, full_report } 형태를 반환함
    const data = await response.json();
    return data.advice ?? "응답 형식이 올바르지 않습니다.";
  } catch (e: any) {
    console.error("API 호출 실패:", e);
    return e.message || "서버와 연결할 수 없습니다. 백엔드 서버가 켜져 있는지 확인해주세요.";
  }
}

// callConsultationByName은 이제 callConsultationApi와 사실상 동일하므로 재사용하거나 유지
export async function callConsultationByName(drugName: string, topic: string, userId: string = "test_user"): Promise<string> {
  return callConsultationApi(drugName, topic, userId);
}

// =========================================================
// [기능 A] 사용자 프로필 관리 (신규 추가됨 ✨)
// =========================================================

export interface UserHistoryRequest {
  user_id: string;
  name: string;
  age: number;
  gender: string;
  is_pregnant: boolean;
  chronic_diseases: string[];
  allergies: string[];
}

export interface UserDrug {
  id: number;
  drug_name: string;
  item_seq?: string;
  source_mode?: string;
  reg_date?: string;
}

// ... existing code ...
export async function saveUserProfile(profile: UserHistoryRequest): Promise<boolean> {
  try {
    const response = await fetch(`${BACKEND_URL}/user/profile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(profile),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "프로필 저장 실패");
    }

    console.log("✅ 프로필 저장 성공");
    return true;
  } catch (e) {
    console.error("프로필 저장 에러:", e);
    return false;
  }
}

export async function getUserProfile(userId: string): Promise<UserHistoryRequest | null> {
  try {
    const response = await fetch(`${BACKEND_URL}/user/profile/${userId}`);

    if (!response.ok) {
      throw new Error("프로필 조회 실패");
    }

    const data = await response.json();
    if (data.status === "success" && data.data) {
      return data.data as UserHistoryRequest;
    }
    return null;
  } catch (e) {
    console.error("프로필 조회 에러:", e);
    return null;
  }
}

// =========================================================
// [기능 B] 복약 관리 (약물 영구 저장 ✨)
// =========================================================

export async function getUserDrugs(userId: string): Promise<UserDrug[]> {
  try {
    const response = await fetch(`${BACKEND_URL}/user/drugs/${userId}`);
    if (!response.ok) throw new Error("약물 목록 조회 실패");

    const data = await response.json();
    if (data.status === "success" && Array.isArray(data.data)) {
      return data.data;
    }
    return [];
  } catch (e) {
    console.error(e);
    return [];
  }
}

export async function addUserDrug(userId: string, drugName: string, description: string = ""): Promise<number | null> {
  try {
    const response = await fetch(`${BACKEND_URL}/user/drug`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        drug_name: drugName,
        description: description
      })
    });

    if (!response.ok) throw new Error("약물 등록 실패");

    const data = await response.json();
    if (data.status === "success" && data.data && data.data.id) {
      return data.data.id;
    }
    return null;
  } catch (e) {
    console.error(e);
    return null;
  }
}

export async function clearUserDrugs(userId: string): Promise<number> {
  try {
    const response = await fetch(`${BACKEND_URL}/user/drugs/all/${userId}`, {
      method: "DELETE"
    });

    if (!response.ok) throw new Error("전체 삭제 실패");

    const data = await response.json();
    return data.count !== undefined ? data.count : 0;
  } catch (e) {
    console.error(e);
    return 0;
  }
}

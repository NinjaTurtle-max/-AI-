import { IdentifyResult } from "../types/chat";

export const BACKEND_URL = "http://127.0.0.1:8000";

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
      // Got candidates from 식약처 API
      formattedCandidates = candidates.slice(0, 5).map((item: any, index: number) => ({
        id: String(index),
        name: item.ITEM_NAME || "Unknown",
        score: 100 - (index * 5),
        effect: item.EE_DOC_DATA || item.UD_DOC_DATA || "",
        administer_method: "",
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

export async function callConsultationApi(classId: string, topic: string): Promise<string> {
  try {
    const response = await fetch(`${BACKEND_URL}/consult`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        class_id: parseInt(classId, 10),
        user_profile: {
          symptom: "속이 쓰리고 소화가 잘 안 돼요",
          age: 45,
          condition: "특이사항 없음",
        },
        options: [topic],
      }),
    });

    if (!response.ok) throw new Error("서버 응답 에러");
    const data = await response.json();
    return data.advice ?? "응답 형식이 올바르지 않습니다.";
  } catch (e) {
    console.error("API 호출 실패:", e);
    return "서버와 연결할 수 없습니다. 백엔드 서버가 켜져 있는지 확인해주세요.";
  }
}

export async function callConsultationByName(drugName: string, topic: string): Promise<string> {
  try {
    const response = await fetch(`${BACKEND_URL}/consult-by-name`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        drug_name: drugName,
        topic: topic,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "서버 응답 에러");
    }

    const data = await response.json();
    return data.advice ?? "응답 형식이 올바르지 않습니다.";
  } catch (e: any) {
    console.error("API 호출 실패:", e);
    return e.message || "서버와 연결할 수 없습니다. 백엔드 서버가 켜져 있는지 확인해주세요.";
  }
}

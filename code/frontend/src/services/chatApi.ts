import { IdentifyResult } from "../types/chat";

  export const BACKEND_URL = "http://127.0.0.1:8000";
  
  // 테스트용 (나중에 YOLO 업로드로 교체)
  export async function fakeIdentify(_imageUri: string): Promise<IdentifyResult> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const candidates = [
          { id: "0", name: "타치온정50밀리그램(글루타티온(환원형))", score: 99 },
        ];
        resolve({
          extracted_text: "TACHION",
          best_match: candidates[0],
          candidates,
        });
      }, 700);
    });
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
  
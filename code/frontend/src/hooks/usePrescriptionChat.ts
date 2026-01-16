import { useMemo, useRef, useState } from "react";
import type { Msg } from "@/src/types/chat";
import { analyzePrescriptionApi } from "@/src/services/prescriptionApi";

export function usePrescriptionChat(welcomeText: string) {
  const [messages, setMessages] = useState<Msg[]>([
    { id: "m0", role: "assistant", type: "text", text: welcomeText },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [previewUri, setPreviewUri] = useState<string | null>(null);

  // id 중복 방지(React key 경고 방지)
  const seq = useRef(0);
  const makeId = () => `${Date.now()}-${seq.current++}`;

  const addMsg = (m: Msg) => setMessages((prev) => [...prev, m]);

  const pushUserText = (text: string) =>
    addMsg({ id: makeId(), role: "user", type: "text", text });

  const pushAssistantText = (text: string) =>
    addMsg({ id: makeId(), role: "assistant", type: "text", text });

  const pushUserImage = (uri: string, text?: string) =>
    addMsg({ id: makeId(), role: "user", type: "image", uri, text });

  const pushTyping = () => {
    const id = makeId();
    addMsg({ id, role: "assistant", type: "typing" });
    return id;
  };

  const pushPrescriptionResult = (payload: any) => {
    addMsg({ id: makeId(), role: "assistant", type: "prescription_result", payload });
  };

  const removeById = (id: string) => {
    setMessages((prev) => prev.filter((m) => m.id !== id));
  };

  const sendPrescriptionImage = async (uri: string, mode: "prescription" | "hospital_prescription") => {
    pushUserImage(uri, mode === "prescription" ? "약봉투(약국) 사진을 보냈어요." : "처방전(병원) 사진을 보냈어요.");
    const typingId = pushTyping();

    setLoading(true);
    try {
      const data = await analyzePrescriptionApi(uri, mode); // returns the analysis object directly
      removeById(typingId);

      // If the data has medications or prescribed_drugs, we assume it's a valid result
      if (data && (data.medications || data.prescribed_drugs || data.detected_items)) {
        pushPrescriptionResult(data);
        pushAssistantText("처방전 분석이 완료되었습니다. 복용 스케줄을 확인해주세요.");
      } else {
        pushAssistantText("분석 결과가 명확하지 않습니다.");
      }

    } catch (e) {
      removeById(typingId);
      console.error(e);
      pushAssistantText("처방전 분석에 실패했어요. 잠시 후 다시 시도해주세요.");
    } finally {
      setLoading(false);
    }
  };

  const onSend = async (mode: "prescription" | "hospital_prescription" = "prescription") => {
    if (loading) return;

    // 처방전 채팅은 이미지가 핵심: previewUri가 있으면 이미지 분석 전송
    if (previewUri) {
      const uri = previewUri;
      setPreviewUri(null);
      await sendPrescriptionImage(uri, mode);
      return;
    }

    // 텍스트만 보냈을 때
    const text = input.trim();
    if (!text) return;

    setInput("");
    pushUserText(text);
    pushAssistantText("처방전(또는 약봉투) 사진을 먼저 올려주시면 분석해드릴게요.");
  };

  return {
    messages,
    input,
    setInput,
    loading,
    previewUri,
    setPreviewUri,
    onSend,
    clearPreview: () => setPreviewUri(null),
  };
}

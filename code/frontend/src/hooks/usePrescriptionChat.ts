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

  const removeById = (id: string) => {
    setMessages((prev) => prev.filter((m) => m.id !== id));
  };

  const sendPrescriptionImage = async (uri: string) => {
    pushUserImage(uri, "처방전 사진을 보냈어요.");
    const typingId = pushTyping();

    setLoading(true);
    try {
      const resultText = await analyzePrescriptionApi(uri);
      removeById(typingId);
      pushAssistantText(resultText);
      pushAssistantText("원하시면 ‘복용 스케줄로 정리해줘’ 같이 요청해도 돼요.");
    } catch (e) {
      removeById(typingId);
      pushAssistantText("처방전 분석에 실패했어요. 잠시 후 다시 시도해주세요.");
    } finally {
      setLoading(false);
    }
  };

  const onSend = async () => {
    if (loading) return;

    // 처방전 채팅은 이미지가 핵심: previewUri가 있으면 이미지 분석 전송
    if (previewUri) {
      const uri = previewUri;
      setPreviewUri(null);
      await sendPrescriptionImage(uri);
      return;
    }

    // 텍스트만 보냈을 때(선택): 이미지 먼저 요청
    const text = input.trim();
    if (!text) return;

    setInput("");
    pushUserText(text);
    pushAssistantText("처방전 사진을 먼저 올려주시면 분석해드릴게요.");
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

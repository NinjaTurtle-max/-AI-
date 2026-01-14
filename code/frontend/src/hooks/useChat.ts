import { useMemo, useRef, useState } from "react";
import type { Msg, IdentifyResult } from "../types/chat";
import { callConsultationApi, fakeIdentify } from "../services/chatApi";

export function useChat() {
  const [messages, setMessages] = useState<Msg[]>([
    {
      id: "m0",
      role: "assistant",
      type: "text",
      text: "안녕하세요! 약 사진을 찍어서 보내주면 어떤 약인지 식별하고,\n원하는 정보(금기사항/복용방법/효과)를 알려드릴게요.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [previewUri, setPreviewUri] = useState<string | null>(null);

  // ===== 내부 기억(ref) =====
  const lastIdentifyRef = useRef<IdentifyResult | null>(null);


  const idSeqRef = useRef(0);
  const makeId = () => `${Date.now()}-${idSeqRef.current++}`;

  const topics = useMemo(() => ["금기사항", "복용방법", "효과"], []);

  // ===== 메시지 헬퍼 =====
  const addMsg = (m: Msg) => setMessages((prev) => [...prev, m]);

  const pushUserText = (text: string) =>
    addMsg({ id: makeId(), role: "user", type: "text", text });

  const pushAssistantText = (text: string) =>
    addMsg({ id: makeId(), role: "assistant", type: "text", text });

  const pushUserImage = (uri: string, text?: string) =>
    addMsg({ id: makeId(), role: "user", type: "image", uri, text });

  const pushIdentify = (payload: IdentifyResult) =>
    addMsg({ id: makeId(), role: "assistant", type: "identify", payload });

  const pushTopics = (t: string[]) =>
    addMsg({ id: makeId(), role: "assistant", type: "topic", payload: { topics: t } });

  const pushTyping = () => {
    const id = makeId();
    addMsg({ id, role: "assistant", type: "typing"});
    return id;
  };

  const removeById = (id: string) => {
    setMessages((prev) => prev.filter((m) => m.id !== id));
  }

  // ===== 비즈니스 로직 =====
  const identifyAndRespond = async (uri: string) => {
    const identify = await fakeIdentify(uri);
    lastIdentifyRef.current = identify;

    pushIdentify(identify);

    if (identify.best_match) {
      pushAssistantText(
        `가장 유력한 약은 "${identify.best_match.name}"입니다.\n어떤 정보가 궁금하신가요?`
      );
      pushTopics(topics);
    }
  };

  const sendImage = async (uri: string) => {
    pushUserImage(uri, "약 사진을 보냈어요.");

    const typingId = pushTyping();
    setLoading(true);
    try {
      await identifyAndRespond(uri);
    } finally {
      removeById(typingId)
      setLoading(false);
    }
  };

  const sendText = () => {
    const text = input.trim();
    if (!text) return;

    setInput("");
    pushUserText(text);
    pushAssistantText("먼저 약 사진을 찍거나 갤러리에서 선택해주세요!");
  };

  const onSend = async () => {
    if (loading) return;

    if (previewUri) {
      const uri = previewUri;
      setPreviewUri(null);
      await sendImage(uri);
      return;
    }

    sendText();
  };

  const onPickTopic = async (topic: string) => {
    const identify = lastIdentifyRef.current;
    if (!identify?.best_match) return;

    pushUserText(topic);

    const typingId = pushTyping();
    setLoading(true);
    try {
      const answer = await callConsultationApi(identify.best_match.id, topic);
      removeById(typingId)
      pushAssistantText(answer);
    } finally {
      setLoading(false);
    }
  };

  return {
    // state
    messages,
    input,
    setInput,
    loading,
    previewUri,
    setPreviewUri,
    topics, // 필요하면

    // actions
    onSend,
    onPickTopic,
    clearPreview: () => setPreviewUri(null),
  };
}

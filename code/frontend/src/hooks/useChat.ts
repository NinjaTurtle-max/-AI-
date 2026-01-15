import { useRef, useState } from "react";
import type { Msg, IdentifyResult } from "../types/chat";
import { fakeIdentify } from "../services/chatApi";

export function useChat(welcomeText?: string) {
  const [messages, setMessages] = useState<Msg[]>([
    {
      id: "m0",
      role: "assistant",
      type: "text",
      text:
        welcomeText ??
        "안녕하세요! 약 사진을 찍어서 보내주면 어떤 약인지 식별해드릴게요.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [previewUri, setPreviewUri] = useState<string | null>(null);

  const lastIdentifyRef = useRef<IdentifyResult | null>(null);

  const idSeqRef = useRef(0);
  const makeId = () => `${Date.now()}-${idSeqRef.current++}`;

  const addMsg = (m: Msg) => setMessages((prev) => [...prev, m]);

  const pushUserText = (text: string) =>
    addMsg({ id: makeId(), role: "user", type: "text", text });

  const pushAssistantText = (text: string) =>
    addMsg({ id: makeId(), role: "assistant", type: "text", text });

  const pushUserImage = (uri: string, text?: string) =>
    addMsg({ id: makeId(), role: "user", type: "image", uri, text });

  const pushIdentify = (payload: IdentifyResult) =>
    addMsg({ id: makeId(), role: "assistant", type: "identify", payload });

  const pushTyping = () => {
    const id = makeId();
    addMsg({ id, role: "assistant", type: "typing" });
    return id;
  };

  const removeById = (id: string) => {
    setMessages((prev) => prev.filter((m) => m.id !== id));
  };

  // ===== 비즈니스 로직 =====
  const identifyAndRespond = async (uri: string) => {
    const identify = await fakeIdentify(uri);
    lastIdentifyRef.current = identify;

    pushIdentify(identify);
  };

  const sendImage = async (uri: string) => {
    pushUserImage(uri, "약 사진을 보냈어요.");

    const typingId = pushTyping();
    setLoading(true);
    try {
      await identifyAndRespond(uri);
    } finally {
      removeById(typingId);
      setLoading(false);
    }
  };

  const sendText = () => {
    const text = input.trim();
    if (!text) return;

    setInput("");
    pushUserText(text);
    pushAssistantText("사진을 먼저 보내주면 무슨 약인지 알려드릴게요!");
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

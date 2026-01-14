import React, { useMemo, useRef, useState } from "react";
import { Ionicons } from "@expo/vector-icons";
import {
  SafeAreaView,
  View,
  Text,
  FlatList,
  TextInput,
  Pressable,
  ActivityIndicator,
  StyleSheet,
  Image,
} from "react-native";
import * as ImagePicker from "expo-image-picker";

import { Msg, IdentifyResult } from "@/src/types/chat";
import { ChatItem } from "@/src/components/ChatItem";
import { InputBar } from "@/src/components/InputBar";
// 1. 백엔드 주소 설정 (전달받은 IP 활용)
const BACKEND_URL = "http://127.0.0.1:8000";


// 2. 이미지 식별 함수 (YOLO 연동 전까지는 테스트용 타치온 데이터 반환)
async function fakeIdentify(_imageUri: string): Promise<IdentifyResult> {
  // 실제 앱에서는 여기서 사진 파일을 서버로 업로드하여 YOLO 분석 결과를 받아와야 합니다.
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
    }, 1000);
  });
}

// 3. 실제 백엔드 LLM(Gemini) 호출 함수 수정
async function callConsultationApi(classId: string, topic: string): Promise<string> {
  try {
    const response = await fetch(`${BACKEND_URL}/consult`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        class_id: parseInt(classId), // "0" -> 0 변환
        user_profile: {
          symptom: "속이 쓰리고 소화가 잘 안 돼요", // 임시 증상
          age: 45,
          condition: "특이사항 없음"
        },
        options: [topic] // 사용자가 클릭한 토픽(금기사항 등)
      }),
    });

    if (!response.ok) {
      throw new Error("서버 응답 에러");
    }

    const data = await response.json();
    return data.advice; // 백엔드에서 생성한 Gemini 상담 결과 반환

  } catch (error) {
    console.error("API 호출 실패:", error);
    return "서버와 연결할 수 없습니다. 백엔드 서버가 켜져 있는지 확인해주세요.";
  }
}

export default function ChatScreen() {
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

  const lastIdentifyRef = useRef<IdentifyResult | null>(null);
  const topics = useMemo(() => ["금기사항", "복용방법", "효과"], []);

  // ✅ key 중복 방지
  const idSeqRef = useRef(0);
  const makeId = () => `${Date.now()}-${idSeqRef.current++}`;

  const addMsg = (m: Msg) => setMessages((prev) => [...prev, m]);

  // 헬퍼들(네가 만든 것) 여기 유지 + makeId 적용
  const pushUserText = (text: string) => addMsg({ id: makeId(), role: "user", type: "text", text });
  const pushAssistantText = (text: string) => addMsg({ id: makeId(), role: "assistant", type: "text", text });
  const pushUserImage = (uri: string, text?: string) =>
    addMsg({ id: makeId(), role: "user", type: "image", uri, text });
  const pushIdentify = (payload: IdentifyResult) =>
    addMsg({ id: makeId(), role: "assistant", type: "identify", payload });
  const pushTopics = (topics: string[]) =>
    addMsg({ id: makeId(), role: "assistant", type: "topic", payload: { topics } });

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

  const sendImageMessage = async (uri: string) => {
    pushUserImage(uri, "약 사진을 보냈어요.");
    setLoading(true);
    try {
      await identifyAndRespond(uri);
    } finally {
      setLoading(false);
    }
  };

  const onSend = async () => {
    if (loading) return;

    if (previewUri) {
      const uri = previewUri;
      setPreviewUri(null);
      await sendImageMessage(uri);
      return;
    }

    const text = input.trim();
    if (!text) return;

    setInput("");
    pushUserText(text);
    pushAssistantText("먼저 약 사진을 찍거나 갤러리에서 선택해주세요!");
  };

  const pickFromCamera = async () => {
    const perm = await ImagePicker.requestCameraPermissionsAsync();
    if (!perm.granted) return alert("카메라 권한이 필요합니다.");
    const res = await ImagePicker.launchCameraAsync({ quality: 0.8 });
    if (!res.canceled) setPreviewUri(res.assets[0].uri);
  };

  const pickFromGallery = async () => {
    const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!perm.granted) return alert("사진첩 권한이 필요합니다.");
    const res = await ImagePicker.launchImageLibraryAsync({ quality: 0.8 });
    if (!res.canceled) setPreviewUri(res.assets[0].uri);
  };

  const onPickTopic = async (topic: string) => {
    const identify = lastIdentifyRef.current;
    if (!identify?.best_match) return;

    pushUserText(topic);
    setLoading(true);
    try {
      const answer = await callConsultationApi(identify.best_match.id, topic);
      pushAssistantText(answer);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <FlatList
        data={messages}
        keyExtractor={(m) => m.id}
        renderItem={({ item }) => (
          <ChatItem item={item} loading={loading} onPickTopic={onPickTopic} styles={styles} />
        )}
        contentContainerStyle={styles.list}
      />

      <InputBar
        input={input}
        setInput={setInput}
        loading={loading}
        previewUri={previewUri}
        onClearPreview={() => setPreviewUri(null)}
        onPickCamera={pickFromCamera}
        onPickGallery={pickFromGallery}
        onSend={() => void onSend()}
        styles={styles}
      />
    </SafeAreaView>
  );
}
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#fff" },
  list: { padding: 16, gap: 10 },
  bubble: { maxWidth: "85%", padding: 12, borderRadius: 14, marginBottom: 4 },
  userBubble: { alignSelf: "flex-end", backgroundColor: "#e8f0ff" },
  assistantBubble: { alignSelf: "flex-start", backgroundColor: "#f2f2f2" },
  msgText: { fontSize: 15, lineHeight: 20 },
  title: { fontWeight: "700", marginBottom: 6 },
  small: { fontSize: 12, opacity: 0.8, marginTop: 2 },
  chipContainer: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginVertical: 6 },
  chip: { paddingVertical: 8, paddingHorizontal: 12, borderRadius: 20, backgroundColor: "#333" },
  chipText: { color: "#fff", fontWeight: "700", fontSize: 13 },
  inputBar: { flexDirection: "row", alignItems: "center", padding: 10, borderTopWidth: 1, borderTopColor: "#eee" },
  photoBtn: { padding: 10, borderRadius: 10, backgroundColor: "#f2f2f2", marginRight: 8 },
  input: { flex: 1, paddingVertical: 10, paddingHorizontal: 12, backgroundColor: "#fafafa", borderRadius: 12 },
  sendBtn: { marginLeft: 8, paddingVertical: 10, paddingHorizontal: 14, borderRadius: 12, backgroundColor: "#111" },
  sendBtnText: { color: "#fff", fontWeight: "700" },
  chatImage: { width: 220, height: 220, borderRadius: 12, backgroundColor: "#ddd" },
  previewWrap: { width: 44, height: 44, marginRight: 8, position: "relative" },
  previewThumb: { width: 44, height: 44, borderRadius: 10, backgroundColor: "#ddd" },
  previewX: {
    position: "absolute",
    top: -6,
    right: -6,
    width: 18,
    height: 18,
    borderRadius: 9,
    backgroundColor: "#111",
    alignItems: "center",
    justifyContent: "center",
  },
  photoBtnPressed: {
    transform: [{ scale: 0.92 }],
    backgroundColor: "#e0e0e0",
  },
  
});
import React, { useRef, useEffect } from "react";
import { FlatList, SafeAreaView, StyleSheet } from "react-native";
import * as ImagePicker from "expo-image-picker";

import { useChat } from "../src/hooks/useChat";
import { ChatItem } from "../src/components/ChatItem";
import { InputBar } from "../src/components/InputBar";

export default function ChatScreen() {
  const {
    messages,
    input,
    setInput,
    loading,
    previewUri,
    setPreviewUri,
    onSend,
    onPickTopic,
    clearPreview,
  } = useChat();

  const flatListRef = useRef<FlatList>(null);
  useEffect(() => {
    flatListRef.current?.scrollToEnd({ animated: true });
  }, [messages]);
  
  const pickFromCamera = async () => {
    if (loading) return;

    const perm = await ImagePicker.requestCameraPermissionsAsync();
    if (!perm.granted) return alert("카메라 권한이 필요합니다.");

    const res = await ImagePicker.launchCameraAsync({ quality: 0.8 });
    if (!res.canceled) setPreviewUri(res.assets[0].uri);
  };

  const pickFromGallery = async () => {
    if (loading) return;

    const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!perm.granted) return alert("사진첩 권한이 필요합니다.");

    const res = await ImagePicker.launchImageLibraryAsync({ quality: 0.8 });
    if (!res.canceled) setPreviewUri(res.assets[0].uri);
  };

  return (
    <SafeAreaView style={styles.container}>
      <FlatList
        ref = {flatListRef}
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
        onClearPreview={clearPreview}
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
  photoBtnPressed: { transform: [{ scale: 0.92 }], backgroundColor: "#e0e0e0" },
});

import React from "react";
import { ActivityIndicator, Pressable, Text, TextInput, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { ImagePreview } from "./ImagePreview";

export function InputBar({
  input,
  setInput,
  loading,
  previewUri,
  onClearPreview,
  onPickCamera,
  onPickGallery,
  onSend,
  styles,
}: {
  input: string;
  setInput: (v: string) => void;
  loading: boolean;
  previewUri: string | null;
  onClearPreview: () => void;
  onPickCamera: () => void;
  onPickGallery: () => void;
  onSend: () => void;
  styles: any;
}) {
  return (
    <View style={styles.inputBar}>
      <Pressable
        onPress={onPickCamera}
        disabled={loading}
        style={({ pressed }) => [styles.photoBtn, pressed && styles.photoBtnPressed, loading && { opacity: 0.3 }]}
      >
        <Ionicons name="camera" size={22} color="#000" />
      </Pressable>

      <Pressable
        onPress={onPickGallery}
        disabled={loading}
        style={({ pressed }) => [styles.photoBtn, pressed && styles.photoBtnPressed, loading && { opacity: 0.3 }]}
      >
        <Ionicons name="image" size={22} color="#000" />
      </Pressable>

      {previewUri && (
        <ImagePreview uri={previewUri} onClear={onClearPreview} disabled={loading} styles={styles} />
      )}

      <TextInput
        value={input}
        onChangeText={setInput}
        placeholder="질문을 입력하세요..."
        style={styles.input}
        editable={!loading}
      />

      <Pressable
        style={({ pressed }) => [styles.sendBtn, pressed && { transform: [{ scale: 0.96 }] }, loading && { opacity: 0.6 }]}
        onPress={onSend}
        disabled={loading}
      >
        <Text style={styles.sendBtnText}>전송</Text>
      </Pressable>

      {loading && <ActivityIndicator style={{ marginLeft: 8 }} />}
    </View>
  );
}

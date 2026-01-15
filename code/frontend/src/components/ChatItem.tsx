import React from "react";
import { Image, Text, View, Pressable } from "react-native";
import { Msg } from "../types/chat";
import { TypingBubble } from "./TypingBubble";
import { Ionicons } from "@expo/vector-icons";

export function ChatItem({
  item,
  loading,
  styles,
  onAddPill, 
}: {
  item: Msg;
  loading: boolean;
  styles: any;
  onAddPill?: (pill: { id: string; name: string }) => void;
}) {
  if (item.type === "image") {
    return (
      <View style={[styles.bubble, styles.userBubble]}>
        <Image source={{ uri: item.uri }} style={styles.chatImage} />
        {!!item.text && (
          <Text style={[styles.msgText, { marginTop: 8 }]}>{item.text}</Text>
        )}
      </View>
    );
  }

  if (item.type === "identify") {
    const p = item.payload;

    const bestId = p.best_match?.id;
    const bestName = p.best_match?.name;

    return (
      <View style={[styles.bubble, styles.assistantBubble]}>
        <Text style={styles.title}>🔎 약 식별 결과</Text>
        <Text style={styles.small}>텍스트: {p.extracted_text}</Text>

        {p.candidates.map((c) => (
          <Text key={c.id} style={styles.small}>
            • {c.name}
          </Text>
        ))}
        {!!bestId && (
        <Pressable
          onPress={() => onAddPill?.({ id: bestId, name: bestName })}
          disabled={loading}
          hitSlop={10}
          style={({ pressed }) => [
            styles.plusBtn,
            (pressed || loading) && { transform: [{ scale: 0.92 }], opacity: 0.85 },
            loading && { opacity: 0.4 },
          ]}
        >
          <Ionicons name="add" size={18} color="#111" />
        </Pressable>
      )}

      </View>
    );
  }

  if (item.type === "typing") {
    return <TypingBubble styles={styles} />;
  }

  if (item.type === "pill_result") {
    return (
      <View style={[styles.bubble, styles.assistantBubble, styles.pillResultBubble]}>
        <Text style={styles.msgText}>이 약은 "{item.payload.name}"로 보여요.</Text>

        <Pressable
          onPress={() => onAddPill?.(item.payload)}
          disabled={loading}
          hitSlop={10}
          style={({ pressed }) => [
            styles.plusBtn,
            (pressed || loading) && { transform: [{ scale: 0.92 }], opacity: 0.85 },
            loading && { opacity: 0.4 },
          ]}
        >
          <Ionicons name="add" size={18} color="#111" />
        </Pressable>
      </View>
    );
  }

  const isUser = item.role === "user";
  return (
    <View style={[styles.bubble, isUser ? styles.userBubble : styles.assistantBubble]}>
      <Text style={styles.msgText}>{item.text}</Text>
    </View>
  );
}

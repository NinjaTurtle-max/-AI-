import React from "react";
import { Image, Text, View } from "react-native";
import { Msg } from "../types/chat";
import { TopicChips } from "./TopicChips";

export function ChatItem({
  item,
  loading,
  onPickTopic,
  styles,
}: {
  item: Msg;
  loading: boolean;
  onPickTopic: (topic: string) => void;
  styles: any;
}) {
  if (item.type === "image") {
    return (
      <View style={[styles.bubble, styles.userBubble]}>
        <Image source={{ uri: item.uri }} style={styles.chatImage} />
        {!!item.text && <Text style={[styles.msgText, { marginTop: 8 }]}>{item.text}</Text>}
      </View>
    );
  }

  if (item.type === "identify") {
    const p = item.payload;
    return (
      <View style={[styles.bubble, styles.assistantBubble]}>
        <Text style={styles.title}>🔎 약 식별 결과</Text>
        <Text style={styles.small}>텍스트: {p.extracted_text}</Text>
        {p.candidates.map((c) => (
          <Text key={c.id} style={styles.small}>
            • {c.name}
          </Text>
        ))}
      </View>
    );
  }

  if (item.type === "topic") {
    return (
      <TopicChips topics={item.payload.topics} onPick={onPickTopic} disabled={loading} styles={styles} />
    );
  }

  const isUser = item.role === "user";
  return (
    <View style={[styles.bubble, isUser ? styles.userBubble : styles.assistantBubble]}>
      <Text style={styles.msgText}>{item.text}</Text>
    </View>
  );
}

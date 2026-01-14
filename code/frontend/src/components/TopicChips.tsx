import React from "react";
import { Pressable, Text, View } from "react-native";

export function TopicChips({
  topics,
  onPick,
  disabled,
  styles,
}: {
  topics: string[];
  onPick: (topic: string) => void;
  disabled?: boolean;
  styles: any; // App styles 재사용
}) {
  return (
    <View style={styles.chipContainer}>
      {topics.map((t) => (
        <Pressable key={t} style={styles.chip} onPress={() => onPick(t)} disabled={disabled}>
          <Text style={styles.chipText}>{t}</Text>
        </Pressable>
      ))}
    </View>
  );
}

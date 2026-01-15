import React from "react";
import { FlatList, Pressable, StyleSheet, Text, View } from "react-native";

export type AlarmPreset = {
  key: string;               // p1" ~ "p10
  enabled?: boolean;         // 설정됐는지
  timeText?: string | null;  // 설정된 시간 
};

type Props = {
  presets: AlarmPreset[];
  selectedKey?: string | null;
  onPressPreset: (preset: AlarmPreset) => void;
};

export default function AlarmPresetBar({ presets, selectedKey, onPressPreset }: Props) {
  return (
    <View style={styles.wrap}>
      <FlatList
        data={presets}
        keyExtractor={(item) => item.key}
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.listContent}
        renderItem={({ item }) => {
          const isSelected = item.key === selectedKey;
          const isEnabled = !!item.enabled;

          return (
            <Pressable
              onPress={() => onPressPreset(item)}
              style={[styles.card, isSelected && styles.cardSelected]}
            >
              {/* 설정 안됨: + */}
              {!isEnabled ? (
                <Text style={[styles.plus, isSelected && styles.plusSelected]}>+</Text>
              ) : (
                //  설정 됨: 💊 + 시간
                <View style={styles.enabledBox}>
                  <Text style={[styles.pill, isSelected && styles.pillSelected]}>💊</Text>
                  <Text style={[styles.time, isSelected && styles.timeSelected]}>
                    {item.timeText ?? "--:--"}
                  </Text>
                </View>
              )}
            </Pressable>
          );
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { paddingTop: 10, paddingBottom: 6 },
  listContent: { paddingHorizontal: 16, gap: 10 },

  card: {
    width: 86,
    height: 86,
    borderRadius: 18,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#f5f5f5",
    borderWidth: 1,
    borderColor: "#eaeaea",
  },
  cardSelected: { backgroundColor: "#111", borderColor: "#111" },

  plus: { fontSize: 34, fontWeight: "900", color: "#111", lineHeight: 34 },
  plusSelected: { color: "#fff" },

  enabledBox: { alignItems: "center", justifyContent: "center" },
  pill: { fontSize: 30 },
  pillSelected: { /* 이모지는 색이 안 바뀌어서 비워둬도 됨 */ },

  time: { marginTop: 6, fontSize: 13, fontWeight: "900", color: "#111" },
  timeSelected: { color: "#fff" },
});

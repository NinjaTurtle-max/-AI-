import React from "react";
import { Pressable, StyleSheet, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";

type Props = {
  onPress?: () => void;
};

export default function BackButton({ onPress }: Props) {
  const router = useRouter();

  const handlePress = () => {
    if (onPress) onPress();
    else router.back();
  };

  return (
    <Pressable
      onPress={handlePress}
      style={({ pressed }) => [
        styles.wrap,
        pressed && styles.pressed,
      ]}
      hitSlop={12}
    >
      <Ionicons name="chevron-back" size={28} color="#111" />
    </Pressable>
  );
}

const styles = StyleSheet.create({
  wrap: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: "center",
    justifyContent: "center",
  },
  pressed: {
    backgroundColor: "#f0f0f0",
  },
});

import React from "react";
import { Image, Pressable, Text, View } from "react-native";

export function ImagePreview({
  uri,
  onClear,
  disabled,
  styles,
}: {
  uri: string;
  onClear: () => void;
  disabled?: boolean;
  styles: any;
}) {
  return (
    <View style={styles.previewWrap}>
      <Image source={{ uri }} style={styles.previewThumb} />
      <Pressable onPress={onClear} style={styles.previewX} disabled={disabled}>
        <Text style={{ color: "#fff", fontSize: 11 }}>✕</Text>
      </Pressable>
    </View>
  );
}

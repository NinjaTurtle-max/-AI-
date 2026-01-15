import React, { useEffect, useMemo, useRef } from "react";
import {
  Animated,
  Dimensions,
  Modal,
  Pressable,
  StyleSheet,
  View,
} from "react-native";

type Props = {
  visible: boolean;
  onClose: () => void;
  children: React.ReactNode;
};

export default function SlideUpSheet({ visible, onClose, children }: Props) {
  const screenH = Dimensions.get("window").height;
  const sheetH = Math.min(520, Math.round(screenH * 0.62)); // 높이 적당히

  const translateY = useRef(new Animated.Value(sheetH)).current;
  const backdropOpacity = useRef(new Animated.Value(0)).current;

  const openAnim = useMemo(
    () =>
      Animated.parallel([
        Animated.timing(translateY, {
          toValue: 0,
          duration: 220,
          useNativeDriver: true,
        }),
        Animated.timing(backdropOpacity, {
          toValue: 1,
          duration: 220,
          useNativeDriver: true,
        }),
      ]),
    [backdropOpacity, translateY]
  );

  const closeAnim = useMemo(
    () =>
      Animated.parallel([
        Animated.timing(translateY, {
          toValue: sheetH,
          duration: 180,
          useNativeDriver: true,
        }),
        Animated.timing(backdropOpacity, {
          toValue: 0,
          duration: 180,
          useNativeDriver: true,
        }),
      ]),
    [backdropOpacity, translateY, sheetH]
  );

  useEffect(() => {
    if (visible) {
      translateY.setValue(sheetH);
      backdropOpacity.setValue(0);
      openAnim.start();
    }
  }, [visible, openAnim, sheetH, translateY, backdropOpacity]);

  const requestClose = () => {
    closeAnim.start(({ finished }) => {
      if (finished) onClose();
    });
  };

  return (
    <Modal visible={visible} transparent animationType="none" onRequestClose={requestClose}>
      <View style={styles.root}>
        {/* Backdrop */}
        <Pressable style={StyleSheet.absoluteFill} onPress={requestClose}>
          <Animated.View
            style={[
              styles.backdrop,
              { opacity: backdropOpacity },
            ]}
          />
        </Pressable>

        {/* Sheet */}
        <Animated.View
          style={[
            styles.sheet,
            { height: sheetH, transform: [{ translateY }] },
          ]}
        >
          <View style={styles.handle} />
          {children}
        </Animated.View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, justifyContent: "flex-end" },
  backdrop: { flex: 1, backgroundColor: "rgba(0,0,0,0.35)" },
  sheet: {
    backgroundColor: "#fff",
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 16,
  },
  handle: {
    alignSelf: "center",
    width: 44,
    height: 5,
    borderRadius: 999,
    backgroundColor: "#ddd",
    marginBottom: 12,
  },
});

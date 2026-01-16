import React from "react";
import { SafeAreaView, View, Text, Pressable, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import Fontisto from '@expo/vector-icons/Fontisto';

export default function HomeScreen() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.h1}>홈</Text>
        <Text style={styles.p}>채팅방을 선택하세요</Text>
      </View>

      <View style={styles.cardsContainer}>
        {/* 약 사진 채팅방 */}
        <Pressable
          style={({ pressed }) => [styles.card, pressed && styles.pressed]}
          onPress={() => router.push("/chat")}
        >
          <Fontisto name="pills" size={24} color="#111" />
          <View style={styles.textWrap}>
            <Text style={styles.title}>알약</Text>
            <Text style={styles.desc}>약 사진을 찍어 정보 확인</Text>
          </View>
        </Pressable>

        {/* 처방전 채팅방 */}
        <Pressable
          style={({ pressed }) => [styles.card, pressed && styles.pressed]}
          onPress={() => router.push("/prescription")}
        >
          <Fontisto name="prescription" size={24} color="#111" />
          <View style={styles.textWrap}>
            <Text style={styles.title}>처방전</Text>
            <Text style={styles.desc}>처방전 사진 분석</Text>
          </View>
        </Pressable>

        {/* 약봉투 채팅방 */}
        <Pressable
          style={({ pressed }) => [styles.card, pressed && styles.pressed]}
          onPress={() => router.push("/medicine_bag")} 
        >
          <Fontisto name="shopping-bag" size={26} color="#111" />
          <Text style={styles.title}>약봉투</Text>
          <Text style={styles.desc}>약 봉투/약 봉지 정보 확인</Text>
        </Pressable>

        {/* 음식 채팅방 */}
        <Pressable
          style={({ pressed }) => [styles.card, pressed && styles.pressed]}
          onPress={() => router.push("/food")} 
        >
          <Ionicons name="fast-food" size={26} color="#111" />
          <Text style={styles.title}>음식</Text>
          <Text style={styles.desc}>음식 사진 분석</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#fff" },
  header: { padding: 20 },
  h1: { fontSize: 22, fontWeight: "800" },
  p: { marginTop: 6, color: "#666" },

  list: { padding: 20, gap: 14 },

  cardsContainer: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
    padding: 16,
  },
  card: {
    width: "48%",          // 화면 절반 정도
    aspectRatio: 1,        // ✅ 정사각형
    alignItems: "center",
    justifyContent: "center",
    padding: 16,
    borderRadius: 16,
    backgroundColor: "#f5f5f5",
    borderWidth: 1,
    borderColor: "#eee",
    marginBottom: 12,      // 아래 줄 카드랑 간격
  },
  
  pressed: {
    transform: [{ scale: 0.98 }],
    opacity: 0.9,
  },
  textWrap: { flex: 1 },
  title: { fontSize: 20, fontWeight: "800", color: "#111", textAlign: "center",marginVertical: 24,  },
  desc: { marginTop: 4, fontSize: 13, color: "#666" },
});


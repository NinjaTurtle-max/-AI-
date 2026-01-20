import React, { useMemo, useState, useEffect } from "react";
import {
  SafeAreaView,
  View,
  Text,
  TouchableOpacity,
  ActivityIndicator,
  ScrollView,
  StyleSheet,
  Dimensions,
} from "react-native";
import { useLocalSearchParams } from "expo-router";
import { LinearGradient } from "expo-linear-gradient";
import Animated, { FadeInDown, FadeInUp } from "react-native-reanimated";
import { Ionicons } from "@expo/vector-icons";

import BackButton from "@/src/components/BackButton";
import { callConsultationApi, callConsultationByName } from "@/src/services/chatApi";
import { useProfile } from "@/src/store/ProfileContext";

const { width } = Dimensions.get("window");

export default function PillDetailScreen() {
  // name is optional in params but we mostly rely on it now
  const { id, name } = useLocalSearchParams<{ id: string; name?: string }>();

  // Topics with icons for better UX
  const topics = useMemo(() => [
    { label: "금기사항", icon: "warning-outline", color: "#FF6B6B" },
    { label: "복용방법", icon: "time-outline", color: "#4ECDC4" },
    { label: "효능", icon: "flask-outline", color: "#1A535C" },
  ], []);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState("");
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null);

  const displayName = name || "약 상세 정보";
  const { profile } = useProfile(); // user_id 가져오기

  const onPickTopic = async (topic: string) => {
    if (!id || loading) return;
    setLoading(true);
    setResult("");
    setSelectedTopic(topic);

    try {
      let text: string;
      const userId = profile?.user_id || "test_user";

      // 처방전/약봉투에서 추가한 약인지 확인 (ID가 "med-"로 시작)
      if (String(id).startsWith("med-")) {
        if (!name) {
          setResult("약 이름 정보가 없습니다.");
          return;
        }
        text = await callConsultationByName(String(name), topic, userId);
      } else {
        // 기존 로직 유지
        text = await callConsultationApi(name ? String(name) : String(id), topic, userId);
      }

      setResult(text);
    } catch (e) {
      console.error(e);
      setResult("조회 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      {/* 1. Gradient Header Background */}
      <LinearGradient
        colors={["#E0F7FA", "#fff"]}
        style={styles.headerGradient}
      />

      <SafeAreaView style={styles.safeArea}>
        {/* Header Content */}
        <View style={styles.header}>
          <BackButton />
          <Text style={styles.headerTitle} numberOfLines={1}>
            {displayName}
          </Text>
        </View>

        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Title Section */}
          <Animated.View entering={FadeInDown.delay(100).duration(500)}>
            <Text style={styles.mainTitle}>{displayName}</Text>
            <Text style={styles.subTitle}>궁금한 정보를 선택해보세요.</Text>
          </Animated.View>

          {/* Topics Grid */}
          <Animated.View
            style={styles.gridContainer}
            entering={FadeInDown.delay(200).duration(500)}
          >
            {topics.map((t, index) => {
              const isActive = selectedTopic === t.label;
              return (
                <TouchableOpacity
                  key={t.label}
                  activeOpacity={0.8}
                  onPress={() => onPickTopic(t.label)}
                  disabled={loading}
                  style={[
                    styles.topicCard,
                    isActive && styles.activeCard,
                    { borderColor: isActive ? t.color : "transparent" }
                  ]}
                >
                  <View style={[styles.iconCircle, { backgroundColor: t.color + "20" }]}>
                    <Ionicons name={t.icon as any} size={24} color={t.color} />
                  </View>
                  <Text style={[styles.topicLabel, isActive && { color: t.color }]}>
                    {t.label}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </Animated.View>

          {/* Loading State */}
          {loading && (
            <Animated.View
              entering={FadeInUp.duration(300)}
              style={styles.loadingContainer}
            >
              <ActivityIndicator size="large" color="#4ECDC4" />
              <Text style={styles.loadingText}>AI 약사가 분석 중입니다...</Text>
            </Animated.View>
          )}

          {/* Result Card */}
          {!!result && !loading && (
            <Animated.View
              entering={FadeInDown.duration(500)}
              style={styles.resultCard}
            >
              <View style={styles.resultHeader}>
                <Ionicons name="information-circle" size={20} color="#333" />
                <Text style={styles.resultTitle}>{selectedTopic} 분석 결과</Text>
              </View>
              <View style={styles.divider} />
              <Text style={styles.resultText}>{result}</Text>
            </Animated.View>
          )}
        </ScrollView>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
  },
  headerGradient: {
    position: "absolute",
    left: 0,
    right: 0,
    top: 0,
    height: 150, // Covers status bar + header area
  },
  safeArea: {
    flex: 1,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#333",
    marginLeft: 10,
    flex: 1,
  },
  scrollContent: {
    padding: 24,
    paddingBottom: 50,
  },
  mainTitle: {
    fontSize: 24,
    fontWeight: "800",
    color: "#2c3e50",
    marginBottom: 8,
  },
  subTitle: {
    fontSize: 16,
    color: "#7f8c8d",
    marginBottom: 30,
  },
  gridContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 30,
  },
  topicCard: {
    width: (width - 48 - 20) / 3, // (Screen - Padding - Gap) / 3
    aspectRatio: 1,
    backgroundColor: "#fff",
    borderRadius: 16,
    justifyContent: "center",
    alignItems: "center",
    // Shadow
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 3,
    borderWidth: 2,
    borderColor: "transparent",
  },
  activeCard: {
    backgroundColor: "#fff",
    transform: [{ scale: 1.05 }],
  },
  iconCircle: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 8,
  },
  topicLabel: {
    fontSize: 14,
    fontWeight: "600",
    color: "#555",
  },
  loadingContainer: {
    alignItems: "center",
    marginTop: 20,
  },
  loadingText: {
    marginTop: 10,
    color: "#7f8c8d",
    fontSize: 15,
  },
  resultCard: {
    backgroundColor: "#fff",
    borderRadius: 20,
    padding: 24,
    // Shadow
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.08,
    shadowRadius: 16,
    elevation: 5,
    borderWidth: 1,
    borderColor: "#f0f0f0",
  },
  resultHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 12,
    gap: 6,
  },
  resultTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: "#333",
  },
  divider: {
    height: 1,
    backgroundColor: "#eee",
    marginBottom: 16,
  },
  resultText: {
    fontSize: 16,
    lineHeight: 26,
    color: "#444",
  },
});


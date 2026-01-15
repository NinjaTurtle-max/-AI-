import React, { useMemo, useState } from "react";
import {
  SafeAreaView,
  View,
  Text,
  Pressable,
  ActivityIndicator,
  ScrollView,
} from "react-native";
import { useLocalSearchParams } from "expo-router";
import BackButton from "@/src/components/BackButton";
import { callConsultationApi } from "@/src/services/chatApi";

export default function PillDetailScreen() {
  const { id, name } = useLocalSearchParams<{ id: string; name?: string }>();
  const topics = useMemo(() => ["금기사항", "복용방법", "효능"], []);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState("");

  const onPickTopic = async (topic: string) => {
    if (!id || loading) return;
    setLoading(true);
    setResult("");
    try {
      const text = await callConsultationApi(String(id), topic);
      setResult(text);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#fff" }}>
      {/* 헤더 */}
      <View
        style={{
          flexDirection: "row",
          alignItems: "center",
          paddingHorizontal: 8,
          paddingVertical: 6,
          borderBottomWidth: 1,
          borderBottomColor: "#eee",
          backgroundColor: "#fff",
        }}
      >
        <BackButton />
        <Text style={{ fontSize: 16, fontWeight: "800", marginLeft: 6 }} numberOfLines={1}>
          {name ?? "약 상세"}
        </Text>
      </View>

      {/* 내용 전체 스크롤 */}
      <ScrollView contentContainerStyle={{ padding: 16, paddingBottom: 40 }}>
        <Text style={{ fontSize: 18, fontWeight: "900" }}>{name ?? "선택한 약"}</Text>
        <Text style={{ marginTop: 6, color: "#666" }}>보고 싶은 항목을 선택하세요.</Text>

        {/* 토픽 버튼 */}
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 10, marginTop: 14 }}>
          {topics.map((t) => (
            <Pressable
              key={t}
              onPress={() => onPickTopic(t)}
              disabled={loading}
              style={({ pressed }) => ({
                paddingVertical: 10,
                paddingHorizontal: 14,
                borderRadius: 999,
                backgroundColor: "#111",
                opacity: loading ? 0.4 : pressed ? 0.85 : 1,
              })}
            >
              <Text style={{ color: "#fff", fontWeight: "800" }}>{t}</Text>
            </Pressable>
          ))}
        </View>

        {/* 로딩 */}
        {loading && (
          <View style={{ marginTop: 18, flexDirection: "row", alignItems: "center", gap: 10 }}>
            <ActivityIndicator />
            <Text style={{ color: "#666" }}>불러오는 중...</Text>
          </View>
        )}

        {/* 결과(길어도 스크롤로 내려감) */}
        {!!result && (
          <View style={{ marginTop: 16, padding: 14, borderRadius: 14, backgroundColor: "#f2f2f2" }}>
            <Text style={{ lineHeight: 22 }}>{result}</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

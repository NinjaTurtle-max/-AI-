import React from "react";
import { SafeAreaView, Text, View, FlatList, Pressable } from "react-native";
import { usePills, type Pill } from "@/src/store/PillsContext";
import { useRouter } from "expo-router";

export default function PillsManagementScreen() {
  const { pills, removePill, clearPills } = usePills();
  const router = useRouter();

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#fff" }}>
      <View
        style={{
          padding: 20,
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <Text style={{ fontSize: 22, fontWeight: "800" }}>복약 관리</Text>

        {pills.length > 0 && (
          <Pressable
            onPress={clearPills}
            style={{
              paddingVertical: 6,
              paddingHorizontal: 10,
              borderRadius: 10,
              backgroundColor: "#111",
            }}
          >
            <Text style={{ color: "#fff", fontWeight: "800" }}>전체삭제</Text>
          </Pressable>
        )}
      </View>

      {pills.length === 0 ? (
        <View style={{ padding: 20 }}>
          <Text style={{ color: "#666" }}>
            아직 추가된 약이 없어요. 채팅에서 +를 눌러 추가해보세요.
          </Text>
        </View>
      ) : (
        <FlatList<Pill>
          data={pills}
          keyExtractor={(p) => p.id}
          contentContainerStyle={{ padding: 20, gap: 10 }}
          renderItem={({ item }) => (
            <Pressable
              onPress={() =>
                router.push({
                  pathname: "/pill_detail",
                  params: { id: item.id, name: item.name },
                })
              }
              style={({ pressed }) => [
                {
                  padding: 14,
                  borderRadius: 14,
                  backgroundColor: "#f2f2f2",
                  flexDirection: "row",
                  justifyContent: "space-between",
                  alignItems: "center",
                },
                pressed && { opacity: 0.85, transform: [{ scale: 0.99 }] },
              ]}
            >
              <Text style={{ flex: 1, fontWeight: "700" }}>{item.name}</Text>

              {/* 삭제 버튼은 누르면 상세로 이동하면 안 되니까 stop 느낌으로 분리 */}
              <Pressable
                onPress={(e) => {
                  e.stopPropagation?.(); // RN에서 환경에 따라 없을 수 있음(그래도 안전)
                  removePill(item.id);
                }}
                style={{
                  marginLeft: 12,
                  paddingVertical: 6,
                  paddingHorizontal: 10,
                  borderRadius: 10,
                  backgroundColor: "#fff",
                }}
              >
                <Text style={{ fontWeight: "800" }}>삭제</Text>
              </Pressable>
            </Pressable>
          )}
        />
      )}
    </SafeAreaView>
  );
}

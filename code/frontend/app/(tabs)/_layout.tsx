import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: "#111",
        tabBarInactiveTintColor: "#999",
        tabBarStyle: {
          height: 64,
          paddingTop: 8,
          paddingBottom: 10,
          borderTopWidth: 1,
          borderTopColor: "#eee",
          backgroundColor: "#fff",
        },
        tabBarLabelStyle: { fontSize: 12, fontWeight: "700" },
      }}
    >
      {/* 홈 */}
      <Tabs.Screen
        name="index"
        options={{
          title: "홈",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="home" color={color} size={size} />
          ),
        }}
      />

      {/* 복약 관리 */}
      <Tabs.Screen
        name="pills_management"
        options={{
          title: "복약관리",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="medical" color={color} size={size} />
          ),
        }}
      />

      {/* 약국 검색 */}
      <Tabs.Screen
        name="pharmacy_search"
        options={{
          title: "약국검색",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="location" color={color} size={size} />
          ),
        }}
      />
    </Tabs>
  );
}

import { SafeAreaView, Text, View } from "react-native";

export default function PharmacySearchScreen() {
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#fff" }}>
      <View style={{ padding: 20 }}>
        <Text style={{ fontSize: 22, fontWeight: "800" }}>약국 검색</Text>
        <Text style={{ marginTop: 8, color: "#666" }}>
          주변 약국을 검색하는 화면
        </Text>
      </View>
    </SafeAreaView>
  );
}

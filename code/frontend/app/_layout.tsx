import { Stack } from "expo-router";
import { PillsProvider } from "@/src/store/PillsContext";

export default function RootLayout() {
  return (
    <PillsProvider>
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="chat" />
        <Stack.Screen name="prescription" />
        <Stack.Screen name="pill_detail" />
      </Stack>
    </PillsProvider>
  );
}

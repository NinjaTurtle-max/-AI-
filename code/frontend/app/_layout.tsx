import { Stack } from "expo-router";
import { PillsProvider } from "@/src/store/PillsContext";
import { ProfileProvider } from "@/src/store/ProfileContext";

export default function RootLayout() {
  return (
    <ProfileProvider>
      <PillsProvider>
        <Stack screenOptions={{ headerShown: false }}>
          <Stack.Screen name="(tabs)" />
          <Stack.Screen name="chat" />
          <Stack.Screen name="prescription" />
          <Stack.Screen name="pill_detail" />
        </Stack>
      </PillsProvider>
    </ProfileProvider>
  );
}

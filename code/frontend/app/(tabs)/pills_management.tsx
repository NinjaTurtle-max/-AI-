import React, { useMemo, useState, useEffect } from "react";
import {
  SafeAreaView,
  Text,
  View,
  FlatList,
  Pressable,
  Alert,
  TextInput,
  Platform,
} from "react-native";
import { usePills, type Pill } from "@/src/store/PillsContext";
import { useRouter } from "expo-router";

import AlarmPresetBar, { type AlarmPreset } from "@/src/components/AlarmPresetBar";
import SlideUpSheet from "@/src/components/SlideUpSheet";
import * as Notifications from "expo-notifications";

// ✅ 포그라운드에서도 알림 보이게
Notifications.setNotificationHandler({
  handleNotification: async (_notification) => {
    return {
      shouldShowAlert: true,
      shouldPlaySound: true,
      shouldSetBadge: false,

      // (타입 요구하는 경우)
      shouldShowBanner: true,
      shouldShowList: true,
    };
  },
});

// 프리셋별 설정 저장용
type PresetConfig = {
  time: string;              // "09:00"
  selectedPillIds: string[]; // 선택된 약 ids
  notificationId?: string;   // 스케줄된 알림 id
};

const DEFAULT_TIME = "09:00";

export default function PillsManagementScreen() {
  const { pills, removePill, clearPills } = usePills();
  const router = useRouter();

  // ---------- 프리셋 바 ----------
  const basePresets = useMemo<AlarmPreset[]>(
    () => Array.from({ length: 10 }, (_, i) => ({ key: `p${i + 1}` })),
    []
  );

  // 프리셋별 저장소 (key -> config)
  const [presetMap, setPresetMap] = useState<Record<string, PresetConfig>>({});

  // ---------- 슬라이드바 상태 ----------
  const [sheetOpen, setSheetOpen] = useState(false);
  const [activeKey, setActiveKey] = useState<string | null>(null);

  // 슬라이드바에서 편집 중인 값(임시)
  const [editTime, setEditTime] = useState(DEFAULT_TIME);
  const [editSelected, setEditSelected] = useState<Set<string>>(new Set());

  // 알림 권한/채널 1회 세팅
  useEffect(() => {
    (async () => {
      const { status } = await Notifications.requestPermissionsAsync();
      if (status !== "granted") {
        Alert.alert("알림 권한 필요", "복약 알람을 받으려면 알림 권한을 허용해주세요.");
      }

      if (Platform.OS === "android") {
        await Notifications.setNotificationChannelAsync("pill-alarm", {
          name: "복약 알람",
          importance: Notifications.AndroidImportance.HIGH,
        });
      }
    })();
  }, []);

  // presetMap을 바탕으로 표시
  const presets = useMemo(() => {
    return basePresets.map((p) => {
      const cfg = presetMap[p.key];
      return {
        ...p,
        enabled: !!presetMap[p.key]?.notificationId,
        timeText: cfg?.time ?? null,
      };
  });
}, [basePresets, presetMap]);

  // "HH:MM" 검증
  const parseHHMM = (value: string) => {
    const m = /^([01]\d|2[0-3]):([0-5]\d)$/.exec(value.trim());
    if (!m) return null;
    return { hour: Number(m[1]), minute: Number(m[2]) };
  };

  // 프리셋 클릭 → 슬라이드바 오픈 + 기존 설정 로드
  const openPresetSheet = (key: string) => {
    setActiveKey(key);

    const cfg = presetMap[key];
    setEditTime(cfg?.time ?? DEFAULT_TIME);
    setEditSelected(new Set(cfg?.selectedPillIds ?? []));

    setSheetOpen(true);
  };

  // 약 선택 토글
  const togglePill = (pillId: string) => {
    setEditSelected((prev) => {
      const next = new Set(prev);
      if (next.has(pillId)) next.delete(pillId);
      else next.add(pillId);
      return next;
    });
  };

  // 완료 → 알람 스케줄
  const saveAlarmForPreset = async () => {
    if (!activeKey) return;

    const t = parseHHMM(editTime);
    if (!t) {
      Alert.alert("형식 오류", "시간은 HH:MM 형태로 입력해주세요. 예) 09:00");
      return;
    }

    if (pills.length === 0) {
      Alert.alert("약이 없어요", "먼저 약을 등록한 뒤 알람을 설정해줘!");
      return;
    }

    const selectedIds = Array.from(editSelected);
    if (selectedIds.length === 0) {
      Alert.alert("선택 필요", "알람을 받을 약을 1개 이상 선택해줘!");
      return;
    }

    // 선택한 약 이름(너무 길면 잘라서)
    const selectedNames = pills
      .filter((p) => editSelected.has(p.id))
      .map((p) => p.name);

    const body = (() => {
      const maxShow = 3;
      const shown = selectedNames.slice(0, maxShow);
      const more = selectedNames.length > maxShow ? ` 외 ${selectedNames.length - maxShow}개` : "";
      return `복약 시간이에요: ${shown.join(", ")}${more}`;
    })();

    // 기존 알람 있으면 취소 후 덮어쓰기
    const prevId = presetMap[activeKey]?.notificationId;
    if (prevId) {
      await Notifications.cancelScheduledNotificationAsync(prevId);
    }

    const id = await Notifications.scheduleNotificationAsync({
      content: {
        title: "복약 알람 💊",
        body,
        sound: true,
        ...(Platform.OS === "android" ? { channelId: "pill-alarm" } : {}),
      },
      trigger: {
        type: "daily",
        hour: t.hour,
        minute: t.minute,
      } as Notifications.NotificationTriggerInput,
    });

    setPresetMap((prev) => ({
      ...prev,
      [activeKey]: {
        time: editTime.trim(),
        selectedPillIds: selectedIds,
        notificationId: id,
      },
    }));

    setSheetOpen(false);
    Alert.alert("설정 완료", `프리셋 ${activeKey} - 매일 ${editTime} 알람이 설정됐어요.`);
  };

  // (선택) 프리셋 알람 해제 버튼
  const cancelAlarmForPreset = async () => {
    if (!activeKey) return;
    const prevId = presetMap[activeKey]?.notificationId;
    if (!prevId) {
      Alert.alert("알람 없음", "이 프리셋엔 설정된 알람이 없어요.");
      return;
    }

    await Notifications.cancelScheduledNotificationAsync(prevId);

    setPresetMap((prev) => ({
      ...prev,
      [activeKey]: {
        time: prev[activeKey]?.time ?? DEFAULT_TIME,
        selectedPillIds: prev[activeKey]?.selectedPillIds ?? [],
        notificationId: undefined,
      },
    }));

    Alert.alert("해제 완료", `프리셋 ${activeKey} 알람을 해제했어요.`);
  };

  const activeCfg = activeKey ? presetMap[activeKey] : undefined;

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#fff" }}>
      {/* 헤더 */}
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
            style={({ pressed }) => [
              {
                paddingVertical: 8,
                paddingHorizontal: 12,
                borderRadius: 12,
                backgroundColor: "#f2f2f2",
              },
              pressed && { opacity: 0.85, transform: [{ scale: 0.98 }] },
            ]}
          >
            <Text style={{ color: "#111", fontWeight: "800" }}>전체삭제</Text>
          </Pressable>
        )}
      </View>

      {/* 상단 프리셋 바 */}
      <AlarmPresetBar
        presets={presets}
        selectedKey={activeKey}
        onPressPreset={(preset) => openPresetSheet(preset.key)}
      />

      {/* 리스트 */}
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

              <Pressable
                onPress={(e) => {
                  // @ts-ignore
                  e.stopPropagation?.();
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

      {/* ✅ 슬라이드바(바텀시트): 시간 + 약 선택 + 완료 */}
      <SlideUpSheet visible={sheetOpen} onClose={() => setSheetOpen(false)}>
        {/* 타이틀 */}
        <Text style={{ fontSize: 18, fontWeight: "900" }}>
          프리셋 {activeKey ?? ""}
        </Text>

        {/* 시간 선택 */}
        <View style={{ marginTop: 12 }}>
          <Text style={{ fontWeight: "800", marginBottom: 6 }}>시간 (HH:MM)</Text>
          <TextInput
            value={editTime}
            onChangeText={setEditTime}
            placeholder="예) 09:00"
            keyboardType="numbers-and-punctuation"
            style={{
              borderWidth: 1,
              borderColor: "#eee",
              borderRadius: 12,
              paddingVertical: 10,
              paddingHorizontal: 12,
              backgroundColor: "#fafafa",
            }}
          />
          {activeCfg?.notificationId ? (
            <Text style={{ marginTop: 8, color: "#666" }}>
              현재 설정됨: 매일 {activeCfg.time}
            </Text>
          ) : null}
        </View>

        {/* 약 선택 */}
        <View style={{ marginTop: 16, flex: 1 }}>
          <Text style={{ fontWeight: "800", marginBottom: 8 }}>
            알람 받을 약 선택 ({editSelected.size}개)
          </Text>

          {pills.length === 0 ? (
            <Text style={{ color: "#666" }}>등록된 약이 없어요.</Text>
          ) : (
            <FlatList
              data={pills}
              keyExtractor={(p) => p.id}
              style={{ maxHeight: 260 }}
              contentContainerStyle={{ gap: 10, paddingBottom: 10 }}
              renderItem={({ item }) => {
                const checked = editSelected.has(item.id);
                return (
                  <Pressable
                    onPress={() => togglePill(item.id)}
                    style={({ pressed }) => [
                      {
                        padding: 12,
                        borderRadius: 14,
                        borderWidth: 1,
                        borderColor: checked ? "#111" : "#eee",
                        backgroundColor: checked ? "#111" : "#fff",
                        flexDirection: "row",
                        alignItems: "center",
                        justifyContent: "space-between",
                      },
                      pressed && { opacity: 0.9 },
                    ]}
                  >
                    <Text style={{ fontWeight: "800", color: checked ? "#fff" : "#111" }}>
                      {item.name}
                    </Text>
                    <Text style={{ fontWeight: "900", color: checked ? "#fff" : "#111" }}>
                      {checked ? "✓" : "+"}
                    </Text>
                  </Pressable>
                );
              }}
            />
          )}
        </View>

        {/* 버튼들 */}
        <View style={{ flexDirection: "row", gap: 10, marginTop: 6 }}>
          <Pressable
            onPress={() => setSheetOpen(false)}
            style={({ pressed }) => [
              {
                flex: 1,
                paddingVertical: 12,
                borderRadius: 12,
                backgroundColor: "#f2f2f2",
                alignItems: "center",
              },
              pressed && { opacity: 0.85 },
            ]}
          >
            <Text style={{ fontWeight: "800" }}>닫기</Text>
          </Pressable>

          <Pressable
            onPress={saveAlarmForPreset}
            style={({ pressed }) => [
              {
                flex: 1,
                paddingVertical: 12,
                borderRadius: 12,
                backgroundColor: "#111",
                alignItems: "center",
              },
              pressed && { opacity: 0.85 },
            ]}
          >
            <Text style={{ color: "#fff", fontWeight: "900" }}>완료</Text>
          </Pressable>
        </View>

        {/* (선택) 알람 해제 */}
        {activeCfg?.notificationId ? (
          <Pressable
            onPress={cancelAlarmForPreset}
            style={({ pressed }) => [
              {
                marginTop: 10,
                paddingVertical: 12,
                borderRadius: 12,
                backgroundColor: "#fff",
                alignItems: "center",
                borderWidth: 1,
                borderColor: "#eee",
              },
              pressed && { opacity: 0.85 },
            ]}
          >
            <Text style={{ fontWeight: "900" }}>이 프리셋 알람 해제</Text>
          </Pressable>
        ) : null}
      </SlideUpSheet>
    </SafeAreaView>
  );
}

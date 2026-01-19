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
  ScrollView,
} from "react-native";
import { usePills, type Pill } from "@/src/store/PillsContext";
import { useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from 'expo-linear-gradient';

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
      shouldShowBanner: true,
      shouldShowList: true,
    };
  },
});

type PresetConfig = {
  time: string;
  selectedPillIds: string[];
  notificationId?: string;
};

const DEFAULT_TIME = "09:00";

export default function PillsManagementScreen() {
  const { pills, removePill, clearPills } = usePills();
  const router = useRouter();

  const basePresets = useMemo<AlarmPreset[]>(
    () => Array.from({ length: 10 }, (_, i) => ({ key: `p${i + 1}` })),
    []
  );

  const [presetMap, setPresetMap] = useState<Record<string, PresetConfig>>({});
  const [sheetOpen, setSheetOpen] = useState(false);
  const [activeKey, setActiveKey] = useState<string | null>(null);
  const [editTime, setEditTime] = useState(DEFAULT_TIME);
  const [editSelected, setEditSelected] = useState<Set<string>>(new Set());

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

  const parseHHMM = (value: string) => {
    const m = /^([01]\d|2[0-3]):([0-5]\d)$/.exec(value.trim());
    if (!m) return null;
    return { hour: Number(m[1]), minute: Number(m[2]) };
  };

  const openPresetSheet = (key: string) => {
    setActiveKey(key);
    const cfg = presetMap[key];
    setEditTime(cfg?.time ?? DEFAULT_TIME);
    setEditSelected(new Set(cfg?.selectedPillIds ?? []));
    setSheetOpen(true);
  };

  const togglePill = (pillId: string) => {
    setEditSelected((prev) => {
      const next = new Set(prev);
      if (next.has(pillId)) next.delete(pillId);
      else next.add(pillId);
      return next;
    });
  };

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

    const selectedNames = pills
      .filter((p) => editSelected.has(p.id))
      .map((p) => p.name);

    const body = (() => {
      const maxShow = 3;
      const shown = selectedNames.slice(0, maxShow);
      const more = selectedNames.length > maxShow ? ` 외 ${selectedNames.length - maxShow}개` : "";
      return `복약 시간이에요: ${shown.join(", ")}${more}`;
    })();

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
    <SafeAreaView style={{ flex: 1, backgroundColor: "#f8f9fa" }}>
      <ScrollView>
        {/* Header with Gradient */}
        <LinearGradient
          colors={['#667eea', '#764ba2']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={{
            padding: 24,
            paddingTop: 16,
            borderBottomLeftRadius: 24,
            borderBottomRightRadius: 24,
          }}
        >
          <View style={{
            flexDirection: "row",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: 16,
          }}>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
              <View style={{
                width: 48,
                height: 48,
                borderRadius: 24,
                backgroundColor: 'rgba(255,255,255,0.3)',
                alignItems: 'center',
                justifyContent: 'center',
              }}>
                <Ionicons name="medical" size={28} color="#fff" />
              </View>
              <View>
                <Text style={{ fontSize: 24, fontWeight: "bold", color: '#fff' }}>복약 관리</Text>
                <Text style={{ fontSize: 13, color: 'rgba(255,255,255,0.9)', marginTop: 2 }}>
                  {pills.length}개의 약 등록됨
                </Text>
              </View>
            </View>

            {pills.length > 0 && (
              <Pressable
                onPress={clearPills}
                style={({ pressed }) => [
                  {
                    paddingVertical: 8,
                    paddingHorizontal: 16,
                    borderRadius: 20,
                    backgroundColor: pressed ? "rgba(255,255,255,0.3)" : "rgba(255,255,255,0.2)",
                    borderWidth: 1,
                    borderColor: 'rgba(255,255,255,0.4)',
                  },
                ]}
              >
                <Text style={{ color: "#fff", fontWeight: "700", fontSize: 13 }}>전체삭제</Text>
              </Pressable>
            )}
          </View>

          {/* Alarm Preset Bar */}
          <AlarmPresetBar
            presets={presets}
            selectedKey={activeKey}
            onPressPreset={(preset) => openPresetSheet(preset.key)}
          />
        </LinearGradient>

        {/* Pills List */}
        <View style={{ padding: 20 }}>
          {pills.length === 0 ? (
            <View style={{
              alignItems: 'center',
              justifyContent: 'center',
              paddingVertical: 60,
            }}>
              <View style={{
                width: 80,
                height: 80,
                borderRadius: 40,
                backgroundColor: '#e3f2fd',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: 16,
              }}>
                <Ionicons name="medical-outline" size={40} color="#3498db" />
              </View>
              <Text style={{ fontSize: 18, fontWeight: '700', color: '#2c3e50', marginBottom: 8 }}>
                등록된 약이 없습니다
              </Text>
              <Text style={{ fontSize: 14, color: "#7f8c8d", textAlign: 'center' }}>
                처방전이나 약봉투를 분석해서{'\n'}약을 추가해보세요
              </Text>
            </View>
          ) : (
            <View style={{ gap: 12 }}>
              {pills.map((item) => (
                <Pressable
                  key={item.id}
                  onPress={() =>
                    router.push({
                      pathname: "/pill_detail",
                      params: { id: item.id, name: item.name },
                    })
                  }
                  style={({ pressed }) => [
                    {
                      padding: 16,
                      borderRadius: 16,
                      backgroundColor: "#fff",
                      flexDirection: "row",
                      justifyContent: "space-between",
                      alignItems: "center",
                      shadowColor: "#000",
                      shadowOffset: { width: 0, height: 2 },
                      shadowOpacity: 0.08,
                      shadowRadius: 8,
                      elevation: 3,
                      borderWidth: 1,
                      borderColor: '#f0f0f0',
                    },
                    pressed && { opacity: 0.8, transform: [{ scale: 0.98 }] },
                  ]}
                >
                  <View style={{ flexDirection: 'row', alignItems: 'center', flex: 1 }}>
                    <View style={{
                      width: 44,
                      height: 44,
                      borderRadius: 22,
                      backgroundColor: '#e3f2fd',
                      alignItems: 'center',
                      justifyContent: 'center',
                      marginRight: 12,
                    }}>
                      <Ionicons name="medical" size={22} color="#3498db" />
                    </View>
                    <View style={{ flex: 1 }}>
                      <Text style={{ fontWeight: "700", fontSize: 15, color: '#2c3e50' }}>
                        {item.name}
                      </Text>
                      {item.description && (
                        <Text style={{ fontSize: 12, color: "#7f8c8d", marginTop: 4 }}>
                          {item.description}
                        </Text>
                      )}
                    </View>
                  </View>

                  <Pressable
                    onPress={(e) => {
                      // @ts-ignore
                      e.stopPropagation?.();
                      removePill(item.id);
                    }}
                    style={({ pressed }) => [
                      {
                        marginLeft: 12,
                        paddingVertical: 8,
                        paddingHorizontal: 12,
                        borderRadius: 12,
                        backgroundColor: pressed ? "#ffebee" : "#fff5f5",
                        borderWidth: 1,
                        borderColor: pressed ? "#e74c3c" : "#ffcdd2",
                      },
                    ]}
                  >
                    <Text style={{ fontWeight: "700", color: "#e74c3c", fontSize: 12 }}>삭제</Text>
                  </Pressable>
                </Pressable>
              ))}
            </View>
          )}
        </View>
      </ScrollView>

      {/* Slide Up Sheet */}
      <SlideUpSheet visible={sheetOpen} onClose={() => setSheetOpen(false)}>
        <Text style={{ fontSize: 18, fontWeight: "900", color: '#2c3e50' }}>
          프리셋 {activeKey ?? ""}
        </Text>

        <View style={{ marginTop: 12 }}>
          <Text style={{ fontWeight: "800", marginBottom: 6, color: '#34495e' }}>시간 (HH:MM)</Text>
          <TextInput
            value={editTime}
            onChangeText={setEditTime}
            placeholder="예) 09:00"
            keyboardType="numbers-and-punctuation"
            style={{
              borderWidth: 1,
              borderColor: "#e0e0e0",
              borderRadius: 12,
              paddingVertical: 12,
              paddingHorizontal: 16,
              backgroundColor: "#fafafa",
              fontSize: 15,
            }}
          />
          {activeCfg?.notificationId ? (
            <Text style={{ marginTop: 8, color: "#7f8c8d", fontSize: 13 }}>
              현재 설정됨: 매일 {activeCfg.time}
            </Text>
          ) : null}
        </View>

        <View style={{ marginTop: 16, flex: 1 }}>
          <Text style={{ fontWeight: "800", marginBottom: 8, color: '#34495e' }}>
            알람 받을 약 선택 ({editSelected.size}개)
          </Text>

          {pills.length === 0 ? (
            <Text style={{ color: "#999" }}>등록된 약이 없어요.</Text>
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
                        borderWidth: 2,
                        borderColor: checked ? "#667eea" : "#e0e0e0",
                        backgroundColor: checked ? "#f0f4ff" : "#fff",
                        flexDirection: "row",
                        alignItems: "center",
                        justifyContent: "space-between",
                      },
                      pressed && { opacity: 0.9 },
                    ]}
                  >
                    <Text style={{ fontWeight: "700", color: checked ? "#667eea" : "#2c3e50", flex: 1 }}>
                      {item.name}
                    </Text>
                    <View style={{
                      width: 24,
                      height: 24,
                      borderRadius: 12,
                      backgroundColor: checked ? "#667eea" : "transparent",
                      borderWidth: 2,
                      borderColor: checked ? "#667eea" : "#bdc3c7",
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}>
                      {checked && <Ionicons name="checkmark" size={16} color="#fff" />}
                    </View>
                  </Pressable>
                );
              }}
            />
          )}
        </View>

        <View style={{ flexDirection: "row", gap: 10, marginTop: 16 }}>
          <Pressable
            onPress={() => setSheetOpen(false)}
            style={({ pressed }) => [
              {
                flex: 1,
                paddingVertical: 14,
                borderRadius: 12,
                backgroundColor: "#f2f2f2",
                alignItems: "center",
              },
              pressed && { opacity: 0.85 },
            ]}
          >
            <Text style={{ fontWeight: "800", color: '#2c3e50' }}>닫기</Text>
          </Pressable>

          <Pressable
            onPress={saveAlarmForPreset}
            style={({ pressed }) => [
              {
                flex: 1,
                paddingVertical: 14,
                borderRadius: 12,
                backgroundColor: "#667eea",
                alignItems: "center",
              },
              pressed && { opacity: 0.85 },
            ]}
          >
            <Text style={{ color: "#fff", fontWeight: "900" }}>완료</Text>
          </Pressable>
        </View>

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
                borderColor: "#e0e0e0",
              },
              pressed && { opacity: 0.85, backgroundColor: '#f8f9fa' },
            ]}
          >
            <Text style={{ fontWeight: "900", color: '#7f8c8d' }}>이 프리셋 알람 해제</Text>
          </Pressable>
        ) : null}
      </SlideUpSheet>
    </SafeAreaView>
  );
}

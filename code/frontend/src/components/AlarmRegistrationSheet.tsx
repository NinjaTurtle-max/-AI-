import React, { useState } from "react";
import {
    View,
    Text,
    Pressable,
    TextInput,
    FlatList,
    Modal,
    StyleSheet,

    ScrollView,
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";


export type Pill = {
    id: string;
    name: string;
    description?: string;
};

type Props = {
    visible: boolean;
    onClose: () => void;
    presetKey: string;
    currentTime?: string;
    currentPillIds?: string[];
    pills: Pill[];
    onSave: (time: string, pillIds: string[]) => void;
    onCancel?: () => void;
    hasActiveAlarm?: boolean;
};

const QUICK_TIMES = [
    { label: "아침", time: "08:00", icon: "sunny" as const },
    { label: "점심", time: "12:00", icon: "partly-sunny" as const },
    { label: "저녁", time: "18:00", icon: "moon" as const },
    { label: "취침", time: "22:00", icon: "bed" as const },
];

export default function AlarmRegistrationSheet({
    visible,
    onClose,
    presetKey,
    currentTime = "09:00",
    currentPillIds = [],
    pills,
    onSave,
    onCancel,
    hasActiveAlarm = false,
}: Props) {
    const [editTime, setEditTime] = useState(currentTime);
    const [selectedPillIds, setSelectedPillIds] = useState<Set<string>>(
        new Set(currentPillIds)
    );

    React.useEffect(() => {
        setEditTime(currentTime);
        setSelectedPillIds(new Set(currentPillIds));
    }, [currentTime, currentPillIds, visible]);

    const togglePill = (pillId: string) => {
        setSelectedPillIds((prev) => {
            const next = new Set(prev);
            if (next.has(pillId)) {
                next.delete(pillId);
            } else {
                next.add(pillId);
            }
            return next;
        });
    };

    const selectAllPills = () => {
        setSelectedPillIds(new Set(pills.map((p) => p.id)));
    };

    const deselectAllPills = () => {
        setSelectedPillIds(new Set());
    };

    const handleQuickTime = (time: string) => {
        setEditTime(time);
    };

    const handleSave = () => {
        onSave(editTime, Array.from(selectedPillIds));
    };

    const handleCancel = () => {
        if (onCancel) {
            onCancel();
        }
        onClose();
    };

    return (
        <Modal
            visible={visible}
            transparent
            animationType="slide"
            onRequestClose={onClose}
        >
            <View style={styles.overlay}>
                <Pressable style={styles.backdrop} onPress={onClose} />

                <View style={styles.sheetContainer}>
                    {/* Header with Gradient */}
                    <LinearGradient
                        colors={["#667eea", "#764ba2"]}
                        start={{ x: 0, y: 0 }}
                        end={{ x: 1, y: 1 }}
                        style={styles.header}
                    >
                        <View style={styles.headerContent}>
                            <View style={styles.headerLeft}>
                                <View style={styles.iconCircle}>
                                    <Ionicons name="alarm" size={28} color="#fff" />
                                </View>
                                <View>
                                    <Text style={styles.headerTitle}>알람 설정</Text>
                                    <Text style={styles.headerSubtitle}>프리셋 {presetKey}</Text>
                                </View>
                            </View>
                            <Pressable onPress={onClose} style={styles.closeButton}>
                                <Ionicons name="close" size={24} color="#fff" />
                            </Pressable>
                        </View>

                        {hasActiveAlarm && (
                            <View style={styles.activeAlarmBadge}>
                                <Ionicons name="checkmark-circle" size={16} color="#4caf50" />
                                <Text style={styles.activeAlarmText}>활성화됨</Text>
                            </View>
                        )}
                    </LinearGradient>

                    <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
                        {/* Quick Time Selection */}
                        <View style={styles.section}>
                            <Text style={styles.sectionTitle}>빠른 선택</Text>
                            <View style={styles.quickTimeGrid}>
                                {QUICK_TIMES.map((item) => (
                                    <Pressable
                                        key={item.time}
                                        onPress={() => handleQuickTime(item.time)}
                                        style={({ pressed }) => [
                                            styles.quickTimeButton,
                                            editTime === item.time && styles.quickTimeButtonActive,
                                            pressed && styles.quickTimeButtonPressed,
                                        ]}
                                    >
                                        <Ionicons
                                            name={item.icon}
                                            size={24}
                                            color={editTime === item.time ? "#667eea" : "#7f8c8d"}
                                        />
                                        <Text
                                            style={[
                                                styles.quickTimeLabel,
                                                editTime === item.time && styles.quickTimeLabelActive,
                                            ]}
                                        >
                                            {item.label}
                                        </Text>
                                        <Text
                                            style={[
                                                styles.quickTimeTime,
                                                editTime === item.time && styles.quickTimeTimeActive,
                                            ]}
                                        >
                                            {item.time}
                                        </Text>
                                    </Pressable>
                                ))}
                            </View>
                        </View>

                        {/* Custom Time Input */}
                        <View style={styles.section}>
                            <Text style={styles.sectionTitle}>시간 직접 입력</Text>
                            <View style={styles.timeInputContainer}>
                                <Ionicons name="time-outline" size={20} color="#667eea" />
                                <TextInput
                                    value={editTime}
                                    onChangeText={setEditTime}
                                    placeholder="예) 09:00"
                                    placeholderTextColor="#bdc3c7"
                                    keyboardType="numbers-and-punctuation"
                                    style={styles.timeInput}
                                />
                            </View>
                            {hasActiveAlarm && (
                                <Text style={styles.currentAlarmText}>
                                    현재 설정: 매일 {currentTime}
                                </Text>
                            )}
                        </View>

                        {/* Pill Selection */}
                        <View style={styles.section}>
                            <View style={styles.pillHeaderRow}>
                                <Text style={styles.sectionTitle}>
                                    알람 받을 약 ({selectedPillIds.size}개)
                                </Text>
                                <View style={styles.pillActions}>
                                    <Pressable onPress={selectAllPills} style={styles.pillActionButton}>
                                        <Text style={styles.pillActionText}>전체선택</Text>
                                    </Pressable>
                                    <Text style={styles.pillActionDivider}>|</Text>
                                    <Pressable onPress={deselectAllPills} style={styles.pillActionButton}>
                                        <Text style={styles.pillActionText}>선택해제</Text>
                                    </Pressable>
                                </View>
                            </View>

                            {pills.length === 0 ? (
                                <View style={styles.emptyPillsContainer}>
                                    <Ionicons name="medical-outline" size={48} color="#bdc3c7" />
                                    <Text style={styles.emptyPillsText}>등록된 약이 없습니다</Text>
                                </View>
                            ) : (
                                <View style={styles.pillList}>
                                    {pills.map((pill) => {
                                        const isSelected = selectedPillIds.has(pill.id);
                                        return (
                                            <Pressable
                                                key={pill.id}
                                                onPress={() => togglePill(pill.id)}
                                                style={({ pressed }) => [
                                                    styles.pillCard,
                                                    isSelected && styles.pillCardSelected,
                                                    pressed && styles.pillCardPressed,
                                                ]}
                                            >
                                                <View style={styles.pillCardContent}>
                                                    <View
                                                        style={[
                                                            styles.pillIcon,
                                                            isSelected && styles.pillIconSelected,
                                                        ]}
                                                    >
                                                        <Ionicons
                                                            name="medical"
                                                            size={20}
                                                            color={isSelected ? "#667eea" : "#95a5a6"}
                                                        />
                                                    </View>
                                                    <View style={styles.pillInfo}>
                                                        <Text
                                                            style={[
                                                                styles.pillName,
                                                                isSelected && styles.pillNameSelected,
                                                            ]}
                                                        >
                                                            {pill.name}
                                                        </Text>
                                                        {pill.description && (
                                                            <Text style={styles.pillDescription}>
                                                                {pill.description}
                                                            </Text>
                                                        )}
                                                    </View>
                                                </View>
                                                <View
                                                    style={[
                                                        styles.checkbox,
                                                        isSelected && styles.checkboxSelected,
                                                    ]}
                                                >
                                                    {isSelected && (
                                                        <Ionicons name="checkmark" size={18} color="#fff" />
                                                    )}
                                                </View>
                                            </Pressable>
                                        );
                                    })}
                                </View>
                            )}
                        </View>
                    </ScrollView>

                    {/* Footer Actions */}
                    <View style={styles.footer}>
                        <Pressable
                            onPress={handleCancel}
                            style={({ pressed }) => [
                                styles.footerButton,
                                styles.cancelButton,
                                pressed && styles.buttonPressed,
                            ]}
                        >
                            <Text style={styles.cancelButtonText}>취소</Text>
                        </Pressable>
                        <Pressable
                            onPress={handleSave}
                            style={({ pressed }) => [
                                styles.footerButton,
                                styles.saveButton,
                                pressed && styles.buttonPressed,
                            ]}
                        >
                            <LinearGradient
                                colors={["#667eea", "#764ba2"]}
                                start={{ x: 0, y: 0 }}
                                end={{ x: 1, y: 0 }}
                                style={styles.saveButtonGradient}
                            >
                                <Ionicons name="checkmark-circle" size={20} color="#fff" />
                                <Text style={styles.saveButtonText}>저장하기</Text>
                            </LinearGradient>
                        </Pressable>
                    </View>
                </View>
            </View>
        </Modal>
    );
}

const styles = StyleSheet.create({
    overlay: {
        flex: 1,
        justifyContent: "flex-end",
        backgroundColor: "rgba(0, 0, 0, 0.5)",
    },
    backdrop: {
        position: "absolute",
        top: 0,
        bottom: 0,
        left: 0,
        right: 0,
    },
    sheetContainer: {
        backgroundColor: "#fff",
        borderTopLeftRadius: 24,
        borderTopRightRadius: 24,
        maxHeight: "95%",
        minHeight: "80%",
        shadowColor: "#000",
        shadowOffset: { width: 0, height: -4 },
        shadowOpacity: 0.15,
        shadowRadius: 12,
        elevation: 8,
    },
    header: {
        padding: 20,
        paddingTop: 24,
        borderTopLeftRadius: 24,
        borderTopRightRadius: 24,
    },
    headerContent: {
        flexDirection: "row",
        alignItems: "center",
        justifyContent: "space-between",
    },
    headerLeft: {
        flexDirection: "row",
        alignItems: "center",
        gap: 12,
    },
    iconCircle: {
        width: 48,
        height: 48,
        borderRadius: 24,
        backgroundColor: "rgba(255, 255, 255, 0.3)",
        alignItems: "center",
        justifyContent: "center",
    },
    headerTitle: {
        fontSize: 20,
        fontWeight: "900",
        color: "#fff",
    },
    headerSubtitle: {
        fontSize: 13,
        color: "rgba(255, 255, 255, 0.9)",
        marginTop: 2,
    },
    closeButton: {
        width: 36,
        height: 36,
        borderRadius: 18,
        backgroundColor: "rgba(255, 255, 255, 0.2)",
        alignItems: "center",
        justifyContent: "center",
    },
    activeAlarmBadge: {
        flexDirection: "row",
        alignItems: "center",
        gap: 6,
        marginTop: 12,
        backgroundColor: "rgba(255, 255, 255, 0.95)",
        paddingHorizontal: 12,
        paddingVertical: 6,
        borderRadius: 12,
        alignSelf: "flex-start",
    },
    activeAlarmText: {
        fontSize: 12,
        fontWeight: "700",
        color: "#4caf50",
    },
    content: {
        flex: 1,
        padding: 20,
    },
    section: {
        marginBottom: 24,
    },
    sectionTitle: {
        fontSize: 16,
        fontWeight: "800",
        color: "#2c3e50",
        marginBottom: 12,
    },
    quickTimeGrid: {
        flexDirection: "row",
        gap: 10,
        flexWrap: "wrap",
    },
    quickTimeButton: {
        flex: 1,
        minWidth: "47%",
        backgroundColor: "#f8f9fa",
        borderRadius: 16,
        padding: 16,
        alignItems: "center",
        borderWidth: 2,
        borderColor: "#e9ecef",
    },
    quickTimeButtonActive: {
        backgroundColor: "#f0f4ff",
        borderColor: "#667eea",
    },
    quickTimeButtonPressed: {
        opacity: 0.8,
        transform: [{ scale: 0.98 }],
    },
    quickTimeLabel: {
        fontSize: 14,
        fontWeight: "700",
        color: "#7f8c8d",
        marginTop: 8,
    },
    quickTimeLabelActive: {
        color: "#667eea",
    },
    quickTimeTime: {
        fontSize: 16,
        fontWeight: "900",
        color: "#2c3e50",
        marginTop: 4,
    },
    quickTimeTimeActive: {
        color: "#667eea",
    },
    timeInputContainer: {
        flexDirection: "row",
        alignItems: "center",
        backgroundColor: "#f8f9fa",
        borderRadius: 16,
        paddingHorizontal: 16,
        paddingVertical: 14,
        borderWidth: 2,
        borderColor: "#e9ecef",
        gap: 12,
    },
    timeInput: {
        flex: 1,
        fontSize: 16,
        fontWeight: "700",
        color: "#2c3e50",
    },
    currentAlarmText: {
        fontSize: 13,
        color: "#7f8c8d",
        marginTop: 8,
        marginLeft: 4,
    },
    pillHeaderRow: {
        flexDirection: "row",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: 12,
    },
    pillActions: {
        flexDirection: "row",
        alignItems: "center",
        gap: 8,
    },
    pillActionButton: {
        paddingVertical: 4,
        paddingHorizontal: 8,
    },
    pillActionText: {
        fontSize: 13,
        fontWeight: "600",
        color: "#667eea",
    },
    pillActionDivider: {
        fontSize: 13,
        color: "#bdc3c7",
    },
    emptyPillsContainer: {
        alignItems: "center",
        justifyContent: "center",
        paddingVertical: 40,
    },
    emptyPillsText: {
        fontSize: 14,
        color: "#95a5a6",
        marginTop: 12,
    },
    pillList: {
        gap: 10,
    },
    pillCard: {
        flexDirection: "row",
        alignItems: "center",
        justifyContent: "space-between",
        padding: 14,
        borderRadius: 14,
        backgroundColor: "#f8f9fa",
        borderWidth: 2,
        borderColor: "#e9ecef",
    },
    pillCardSelected: {
        backgroundColor: "#f0f4ff",
        borderColor: "#667eea",
    },
    pillCardPressed: {
        opacity: 0.9,
        transform: [{ scale: 0.98 }],
    },
    pillCardContent: {
        flexDirection: "row",
        alignItems: "center",
        flex: 1,
        gap: 12,
    },
    pillIcon: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: "#e9ecef",
        alignItems: "center",
        justifyContent: "center",
    },
    pillIconSelected: {
        backgroundColor: "#d4dfff",
    },
    pillInfo: {
        flex: 1,
    },
    pillName: {
        fontSize: 15,
        fontWeight: "700",
        color: "#2c3e50",
    },
    pillNameSelected: {
        color: "#667eea",
    },
    pillDescription: {
        fontSize: 12,
        color: "#7f8c8d",
        marginTop: 2,
    },
    checkbox: {
        width: 26,
        height: 26,
        borderRadius: 13,
        borderWidth: 2,
        borderColor: "#bdc3c7",
        backgroundColor: "transparent",
        alignItems: "center",
        justifyContent: "center",
    },
    checkboxSelected: {
        backgroundColor: "#667eea",
        borderColor: "#667eea",
    },
    footer: {
        flexDirection: "row",
        padding: 20,
        paddingTop: 16,
        gap: 12,
        borderTopWidth: 1,
        borderTopColor: "#f0f0f0",
    },
    footerButton: {
        flex: 1,
        borderRadius: 14,
        overflow: "hidden",
    },
    cancelButton: {
        backgroundColor: "#f8f9fa",
        borderWidth: 2,
        borderColor: "#e9ecef",
        paddingVertical: 16,
        alignItems: "center",
        justifyContent: "center",
    },
    cancelButtonText: {
        fontSize: 16,
        fontWeight: "800",
        color: "#7f8c8d",
    },
    saveButton: {
        flex: 1,
    },
    saveButtonGradient: {
        flexDirection: "row",
        alignItems: "center",
        justifyContent: "center",
        paddingVertical: 16,
        gap: 8,
    },
    saveButtonText: {
        fontSize: 16,
        fontWeight: "900",
        color: "#fff",
    },
    buttonPressed: {
        opacity: 0.85,
        transform: [{ scale: 0.98 }],
    },
});

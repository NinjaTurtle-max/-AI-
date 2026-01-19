import React, { useState } from "react";
import {
    SafeAreaView,
    View,
    Text,
    TextInput,
    Pressable,
    StyleSheet,
    ScrollView,
    Alert
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { useProfile } from "../../src/store/ProfileContext";

export default function ProfileScreen() {
    const { profile, updateProfile, saveProfile, isLoading } = useProfile();

    const [height, setHeight] = useState(profile.height > 0 ? profile.height.toString() : "");
    const [weight, setWeight] = useState(profile.weight > 0 ? profile.weight.toString() : "");
    const [gender, setGender] = useState<"남성" | "여성" | "기타" | "">(profile.gender);

    const getBMIStatus = (bmi: number) => {
        if (bmi === 0) return { label: "-", color: "#95a5a6", gradient: ["#bdc3c7", "#95a5a6"] };
        if (bmi < 18.5) return { label: "저체중", color: "#3498db", gradient: ["#3498db", "#2980b9"] };
        if (bmi < 25) return { label: "정상", color: "#27ae60", gradient: ["#2ecc71", "#27ae60"] };
        if (bmi < 30) return { label: "과체중", color: "#f39c12", gradient: ["#f39c12", "#e67e22"] };
        return { label: "비만", color: "#e74c3c", gradient: ["#e74c3c", "#c0392b"] };
    };

    const handleSave = async () => {
        const heightNum = parseFloat(height);
        const weightNum = parseFloat(weight);

        // Validation
        if (!height || !weight || !gender) {
            Alert.alert("입력 오류", "모든 필드를 입력해주세요.");
            return;
        }

        if (heightNum < 100 || heightNum > 250) {
            Alert.alert("입력 오류", "키는 100~250cm 사이로 입력해주세요.");
            return;
        }

        if (weightNum < 20 || weightNum > 300) {
            Alert.alert("입력 오류", "몸무게는 20~300kg 사이로 입력해주세요.");
            return;
        }

        // Update profile
        updateProfile({
            height: heightNum,
            weight: weightNum,
            gender: gender,
        });

        // Save to AsyncStorage
        try {
            await saveProfile();
            Alert.alert("저장 완료", "프로필이 저장되었습니다.");
        } catch (error) {
            Alert.alert("저장 실패", "프로필 저장에 실패했습니다.");
        }
    };

    const bmiStatus = getBMIStatus(profile.bmi);

    if (isLoading) {
        return (
            <SafeAreaView style={styles.container}>
                <View style={styles.loadingContainer}>
                    <Text style={styles.loadingText}>로딩 중...</Text>
                </View>
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView style={styles.container}>
            <ScrollView contentContainerStyle={styles.scrollContent}>
                {/* Header */}
                <View style={styles.header}>
                    <View>
                        <Text style={styles.greeting}>내 정보</Text>
                        <Text style={styles.title}>프로필</Text>
                    </View>
                    <View style={styles.badge}>
                        <Ionicons name="person" size={20} color="#667eea" />
                    </View>
                </View>

                {/* BMI Card */}
                <LinearGradient
                    colors={bmiStatus.gradient as any}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 1 }}
                    style={styles.bmiCard}
                >
                    <View style={styles.bmiHeader}>
                        <Text style={styles.bmiLabel}>BMI 지수</Text>
                        <View style={styles.bmiStatusBadge}>
                            <Text style={styles.bmiStatusText}>{bmiStatus.label}</Text>
                        </View>
                    </View>
                    <Text style={styles.bmiValue}>
                        {profile.bmi > 0 ? profile.bmi.toFixed(1) : "-"}
                    </Text>
                    <Text style={styles.bmiDesc}>
                        {profile.bmi > 0
                            ? "정기적인 건강 관리를 추천합니다"
                            : "키와 몸무게를 입력하세요"}
                    </Text>
                </LinearGradient>

                {/* Input Section */}
                <Text style={styles.sectionTitle}>기본 정보</Text>

                {/* Height Input */}
                <View style={styles.inputGroup}>
                    <Text style={styles.inputLabel}>키 (cm)</Text>
                    <View style={styles.inputContainer}>
                        <Ionicons name="resize" size={20} color="#7f8c8d" style={styles.inputIcon} />
                        <TextInput
                            style={styles.input}
                            value={height}
                            onChangeText={setHeight}
                            placeholder="예: 170"
                            keyboardType="numeric"
                            placeholderTextColor="#bdc3c7"
                        />
                        <Text style={styles.inputUnit}>cm</Text>
                    </View>
                </View>

                {/* Weight Input */}
                <View style={styles.inputGroup}>
                    <Text style={styles.inputLabel}>몸무게 (kg)</Text>
                    <View style={styles.inputContainer}>
                        <Ionicons name="fitness" size={20} color="#7f8c8d" style={styles.inputIcon} />
                        <TextInput
                            style={styles.input}
                            value={weight}
                            onChangeText={setWeight}
                            placeholder="예: 65"
                            keyboardType="numeric"
                            placeholderTextColor="#bdc3c7"
                        />
                        <Text style={styles.inputUnit}>kg</Text>
                    </View>
                </View>

                {/* Gender Selector */}
                <View style={styles.inputGroup}>
                    <Text style={styles.inputLabel}>성별</Text>
                    <View style={styles.genderContainer}>
                        {(["남성", "여성", "기타"] as const).map((g) => (
                            <Pressable
                                key={g}
                                style={[
                                    styles.genderButton,
                                    gender === g && styles.genderButtonActive,
                                ]}
                                onPress={() => setGender(g)}
                            >
                                <Text
                                    style={[
                                        styles.genderButtonText,
                                        gender === g && styles.genderButtonTextActive,
                                    ]}
                                >
                                    {g}
                                </Text>
                            </Pressable>
                        ))}
                    </View>
                </View>

                {/* Save Button */}
                <Pressable
                    style={({ pressed }) => [
                        styles.saveButton,
                        pressed && styles.saveButtonPressed,
                    ]}
                    onPress={handleSave}
                >
                    <LinearGradient
                        colors={["#667eea", "#764ba2"]}
                        start={{ x: 0, y: 0 }}
                        end={{ x: 1, y: 1 }}
                        style={styles.saveButtonGradient}
                    >
                        <Ionicons name="save" size={20} color="#fff" style={styles.saveButtonIcon} />
                        <Text style={styles.saveButtonText}>저장하기</Text>
                    </LinearGradient>
                </Pressable>

                {/* Info Footer */}
                <View style={styles.infoFooter}>
                    <Ionicons name="information-circle-outline" size={16} color="#95a5a6" />
                    <Text style={styles.infoFooterText}>
                        입력한 정보는 기기에 안전하게 저장됩니다
                    </Text>
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: "#f8f9fa",
    },
    loadingContainer: {
        flex: 1,
        alignItems: "center",
        justifyContent: "center",
    },
    loadingText: {
        fontSize: 16,
        color: "#7f8c8d",
    },
    scrollContent: {
        padding: 20,
        paddingBottom: 40,
    },
    header: {
        flexDirection: "row",
        justifyContent: "space-between",
        alignItems: "flex-start",
        marginBottom: 24,
    },
    greeting: {
        fontSize: 16,
        color: "#7f8c8d",
        marginBottom: 4,
        fontWeight: "500",
    },
    title: {
        fontSize: 28,
        fontWeight: "bold",
        color: "#2c3e50",
    },
    badge: {
        width: 44,
        height: 44,
        borderRadius: 22,
        backgroundColor: "#ede7f6",
        alignItems: "center",
        justifyContent: "center",
    },
    bmiCard: {
        borderRadius: 20,
        padding: 24,
        marginBottom: 28,
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.15,
        shadowRadius: 12,
        elevation: 6,
    },
    bmiHeader: {
        flexDirection: "row",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: 12,
    },
    bmiLabel: {
        fontSize: 16,
        color: "rgba(255,255,255,0.9)",
        fontWeight: "600",
    },
    bmiStatusBadge: {
        backgroundColor: "rgba(255,255,255,0.3)",
        paddingHorizontal: 12,
        paddingVertical: 4,
        borderRadius: 12,
    },
    bmiStatusText: {
        color: "#fff",
        fontSize: 13,
        fontWeight: "700",
    },
    bmiValue: {
        fontSize: 48,
        fontWeight: "bold",
        color: "#fff",
        marginBottom: 8,
    },
    bmiDesc: {
        fontSize: 14,
        color: "rgba(255,255,255,0.9)",
    },
    sectionTitle: {
        fontSize: 20,
        fontWeight: "bold",
        color: "#2c3e50",
        marginBottom: 16,
    },
    inputGroup: {
        marginBottom: 20,
    },
    inputLabel: {
        fontSize: 15,
        fontWeight: "600",
        color: "#2c3e50",
        marginBottom: 8,
    },
    inputContainer: {
        flexDirection: "row",
        alignItems: "center",
        backgroundColor: "#fff",
        borderRadius: 12,
        paddingHorizontal: 16,
        paddingVertical: 14,
        borderWidth: 1,
        borderColor: "#e0e0e0",
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.05,
        shadowRadius: 4,
        elevation: 2,
    },
    inputIcon: {
        marginRight: 12,
    },
    input: {
        flex: 1,
        fontSize: 16,
        color: "#2c3e50",
    },
    inputUnit: {
        fontSize: 15,
        color: "#7f8c8d",
        fontWeight: "600",
        marginLeft: 8,
    },
    genderContainer: {
        flexDirection: "row",
        gap: 12,
    },
    genderButton: {
        flex: 1,
        paddingVertical: 14,
        borderRadius: 12,
        backgroundColor: "#fff",
        borderWidth: 1,
        borderColor: "#e0e0e0",
        alignItems: "center",
        justifyContent: "center",
    },
    genderButtonActive: {
        backgroundColor: "#667eea",
        borderColor: "#667eea",
    },
    genderButtonText: {
        fontSize: 15,
        fontWeight: "600",
        color: "#7f8c8d",
    },
    genderButtonTextActive: {
        color: "#fff",
    },
    saveButton: {
        marginTop: 12,
        marginBottom: 20,
        borderRadius: 16,
        overflow: "hidden",
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.2,
        shadowRadius: 8,
        elevation: 6,
    },
    saveButtonPressed: {
        opacity: 0.9,
        transform: [{ scale: 0.98 }],
    },
    saveButtonGradient: {
        flexDirection: "row",
        alignItems: "center",
        justifyContent: "center",
        paddingVertical: 16,
    },
    saveButtonIcon: {
        marginRight: 8,
    },
    saveButtonText: {
        fontSize: 17,
        fontWeight: "bold",
        color: "#fff",
    },
    infoFooter: {
        flexDirection: "row",
        alignItems: "center",
        justifyContent: "center",
        gap: 8,
    },
    infoFooterText: {
        fontSize: 13,
        color: "#95a5a6",
    },
});

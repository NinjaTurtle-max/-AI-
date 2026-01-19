import React, { useState } from "react";
import { SafeAreaView, StyleSheet, View, Text, Alert, TouchableOpacity, ActivityIndicator, Image } from "react-native";
import * as ImagePicker from "expo-image-picker";
import { Ionicons } from '@expo/vector-icons';

import BackButton from "@/src/components/BackButton";
import AnalysisResultView from "@/src/components/AnalysisResultView";
import { usePills } from "@/src/store/PillsContext";
import { analyzePrescriptionApi } from "@/src/services/prescriptionApi";

export default function MedicineBagAnalysisScreen() {
    const [status, setStatus] = useState<"initial" | "loading" | "success" | "error">("initial");
    const [analysisResult, setAnalysisResult] = useState<any>(null);
    const [previewUri, setPreviewUri] = useState<string | null>(null);

    const { addPill } = usePills();

    const handleAnalysis = async (uri: string) => {
        setPreviewUri(uri);
        setStatus("loading");

        try {
            const result = await analyzePrescriptionApi(uri, "prescription"); // mode: prescription (약봉투)
            if (result && (result.prescribed_drugs || result.medications || result.detected_items)) {
                setAnalysisResult(result);
                setStatus("success");
            } else {
                Alert.alert("분석 실패", "약물 정보를 찾을 수 없습니다.");
                setStatus("error");
            }
        } catch (e) {
            console.error(e);
            Alert.alert("오류", "분석 중 문제가 발생했습니다.");
            setStatus("error");
        }
    };

    const pickFromCamera = async () => {
        const perm = await ImagePicker.requestCameraPermissionsAsync();
        if (!perm.granted) return alert("카메라 권한이 필요합니다.");

        const res = await ImagePicker.launchCameraAsync({ quality: 0.8 });
        if (!res.canceled) {
            handleAnalysis(res.assets[0].uri);
        }
    };

    const pickFromGallery = async () => {
        const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
        if (!perm.granted) return alert("사진첩 권한이 필요합니다.");

        const res = await ImagePicker.launchImageLibraryAsync({ quality: 0.8 });
        if (!res.canceled) {
            handleAnalysis(res.assets[0].uri);
        }
    };

    const handleAddPill = (pill: { id: string; name: string }) => {
        addPill(pill);
        Alert.alert("추가 완료", `"${pill.name}"(이)가 복약 관리에 추가되었습니다.`);
    };

    const handleReset = () => {
        setStatus("initial");
        setAnalysisResult(null);
        setPreviewUri(null);
    };

    return (
        <SafeAreaView style={styles.container}>
            {/* Header - Only show in initial or loading/error states */}
            {status !== "success" && (
                <View style={styles.header}>
                    <BackButton />
                    <Text style={styles.headerTitle}>약봉투 분석</Text>
                </View>
            )}

            {/* 1. Initial State */}
            {status === "initial" && (
                <View style={styles.centerContainer}>
                    <Ionicons name="medkit-outline" size={80} color="#bdc3c7" />
                    <Text style={styles.instructionText}>약봉투 사진을 찍거나 올려주세요</Text>
                    <Text style={styles.subInstructionText}>
                        약봉투에 적힌 약물 정보를{"\n"}자동으로 분석하여 저장합니다.
                    </Text>

                    <View style={styles.buttonRow}>
                        <TouchableOpacity style={styles.actionButton} onPress={pickFromCamera}>
                            <Ionicons name="camera" size={24} color="#fff" />
                            <Text style={styles.buttonText}>카메라</Text>
                        </TouchableOpacity>
                        <TouchableOpacity style={[styles.actionButton, styles.galleryButton]} onPress={pickFromGallery}>
                            <Ionicons name="images" size={24} color="#fff" />
                            <Text style={styles.buttonText}>앨범</Text>
                        </TouchableOpacity>
                    </View>
                </View>
            )}

            {/* 2. Loading State */}
            {status === "loading" && (
                <View style={styles.centerContainer}>
                    {previewUri && <Image source={{ uri: previewUri }} style={styles.previewImage} />}
                    <ActivityIndicator size="large" color="#3498db" />
                    <Text style={styles.loadingText}>약봉투를 분석하고 있습니다...</Text>
                </View>
            )}

            {/* 3. Success State */}
            {status === "success" && analysisResult && (
                <View style={{ flex: 1 }}>
                    {/* Custom Header with Reset (Back) */}
                    <View style={styles.header}>
                        <BackButton onPress={handleReset} />
                        <Text style={styles.headerTitle}>분석 결과</Text>
                    </View>
                    <AnalysisResultView
                        result={analysisResult}
                        onAddPill={handleAddPill}
                        onReset={handleReset}
                    />
                </View>
            )}

            {/* 4. Error State */}
            {status === "error" && (
                <View style={styles.centerContainer}>
                    <Ionicons name="alert-circle-outline" size={60} color="#e74c3c" />
                    <Text style={styles.errorText}>분석에 실패했습니다.</Text>
                    <TouchableOpacity style={styles.retryButton} onPress={handleReset}>
                        <Text style={styles.retryButtonText}>다시 시도하기</Text>
                    </TouchableOpacity>
                </View>
            )}

        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: "#fff" },
    header: {
        flexDirection: "row",
        alignItems: "center",
        paddingHorizontal: 8,
        paddingVertical: 6,
        borderBottomWidth: 1,
        borderBottomColor: "#eee",
        backgroundColor: "#fff",
    },
    headerTitle: {
        fontSize: 16,
        fontWeight: "800",
        marginLeft: 4,
    },
    centerContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20,
    },
    instructionText: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#34495e',
        marginTop: 20,
        marginBottom: 10,
    },
    subInstructionText: {
        fontSize: 15,
        color: '#7f8c8d',
        textAlign: 'center',
        marginBottom: 30,
        lineHeight: 22,
    },
    buttonRow: {
        flexDirection: 'row',
        gap: 15,
    },
    actionButton: {
        flexDirection: 'row',
        backgroundColor: '#3498db',
        paddingVertical: 12,
        paddingHorizontal: 20,
        borderRadius: 30,
        alignItems: 'center',
        gap: 8,
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.2,
        shadowRadius: 3,
        elevation: 4,
    },
    galleryButton: {
        backgroundColor: '#9b59b6',
    },
    buttonText: {
        color: '#fff',
        fontWeight: '600',
        fontSize: 16,
    },
    previewImage: {
        width: 200,
        height: 200,
        borderRadius: 12,
        marginBottom: 20,
        resizeMode: 'cover',
    },
    loadingText: {
        marginTop: 20,
        fontSize: 16,
        color: '#34495e',
        fontWeight: '600',
    },
    errorText: {
        fontSize: 18,
        color: '#34495e',
        marginTop: 20,
        marginBottom: 20,
    },
    retryButton: {
        backgroundColor: '#95a5a6',
        paddingVertical: 10,
        paddingHorizontal: 20,
        borderRadius: 20,
    },
    retryButtonText: {
        color: '#fff',
        fontWeight: '600',
    },
});

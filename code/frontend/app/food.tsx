import React from 'react';
import { View, Text, StyleSheet, ScrollView, SafeAreaView, TouchableOpacity, Image, ActivityIndicator, StatusBar } from 'react-native';
import { Stack } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useFoodAnalysis } from '@/src/hooks/useFoodAnalysis';

const FoodAnalysisScreen = () => {
    const {
        imageUri,
        loading,
        result,
        error,
        pickFromCamera,
        pickFromGallery,
        resetAnalysis
    } = useFoodAnalysis();

    const renderContent = () => {
        // 1. Initial State: No Image selected
        if (!imageUri && !loading) {
            return (
                <View style={styles.centerContainer}>
                    <Ionicons name="fast-food-outline" size={80} color="#bdc3c7" />
                    <Text style={styles.instructionText}>음식 사진을 찍거나 올려주세요</Text>
                    <Text style={styles.subInstructionText}>
                        현재 복용 중인 약과 상호작용할 위험이 있는 성분을 분석해드립니다.
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
            );
        }

        // 2. Loading State
        if (loading) {
            return (
                <View style={styles.centerContainer}>
                    <Image source={{ uri: imageUri! }} style={styles.previewImage} />
                    <View style={styles.loadingOverlay}>
                        <ActivityIndicator size="large" color="#ffffff" />
                        <Text style={styles.loadingText}>음식 성분 분석 중...</Text>
                    </View>
                </View>
            );
        }

        // 3. Error State
        if (error) {
            return (
                <View style={styles.centerContainer}>
                    <Ionicons name="alert-circle" size={60} color="#e74c3c" />
                    <Text style={styles.errorText}>{error}</Text>
                    <TouchableOpacity style={styles.retryButton} onPress={resetAnalysis}>
                        <Text style={styles.retryButtonText}>다시 시도하기</Text>
                    </TouchableOpacity>
                </View>
            );
        }

        // 4. Result State (Envelope UI)
        if (result) {
            return (
                <ScrollView contentContainerStyle={styles.scrollContent}>
                    <View style={styles.envelope}>
                        {/* Header Section */}
                        <View style={styles.header}>
                            <Text style={styles.hospitalName}>약물-음식 상호작용 분석실</Text>
                            <View style={styles.stampBox}>
                                <Text style={styles.stampText}>분석 완료</Text>
                            </View>
                        </View>

                        {/* Patient Info-like Section */}
                        <View style={styles.infoRow}>
                            <Text style={styles.label}>구분:</Text>
                            <Text style={styles.value}>식이요법 지도</Text>
                            <Text style={[styles.label, { marginLeft: 20 }]}>일자:</Text>
                            <Text style={styles.value}>{new Date().toLocaleDateString()}</Text>
                        </View>

                        <View style={styles.divider} />

                        {/* Analysis Content */}
                        <View style={styles.section}>
                            <Text style={styles.sectionTitle}>[ 처방 대상 (음식) ]</Text>

                            {/* Selected Image Thumbnail */}
                            {imageUri && (
                                <Image source={{ uri: imageUri }} style={styles.resultThumbnail} />
                            )}

                            <View style={styles.pillContainer}>
                                {result.detected_items?.map((item, index) => (
                                    <View key={index} style={styles.pillBadge}>
                                        <Text style={styles.pillText}>{item}</Text>
                                    </View>
                                )) || <Text style={styles.placeholderText}>음식이 감지되지 않았습니다.</Text>}
                            </View>
                        </View>

                        <View style={styles.dashedDivider} />

                        <View style={styles.section}>
                            <Text style={styles.sectionTitle}>[ 주요 성분 분석 ]</Text>
                            <Text style={styles.bodyText}>
                                {result.main_ingredients?.join(', ') || '성분 정보 없음'}
                            </Text>
                        </View>

                        <View style={styles.dashedDivider} />

                        {/* Warning / Advice Section */}
                        <View style={styles.section}>
                            <Text style={[styles.sectionTitle, { color: '#e74c3c' }]}>[ 복약 지도 및 주의사항 ]</Text>
                            <View style={styles.warningBox}>
                                <Text style={styles.warningText}>
                                    {result.warning_message || '특이사항 없습니다.'}
                                </Text>
                            </View>
                        </View>

                        <TouchableOpacity style={styles.newAnalysisButton} onPress={resetAnalysis}>
                            <Text style={styles.newAnalysisButtonText}>다른 음식 분석하기</Text>
                        </TouchableOpacity>

                        <View style={styles.footer}>
                            <Text style={styles.footerText}>※ 본 분석 결과는 AI에 의한 것으로 의학적 조언을 대체할 수 없습니다.</Text>
                            <Text style={styles.pharmacyName}>Health Care AI Solution</Text>
                        </View>
                    </View>
                </ScrollView>
            );
        }

        return null;
    };

    return (
        <SafeAreaView style={styles.container}>
            <Stack.Screen options={{ title: "음식 분석", headerShadowVisible: false, headerStyle: { backgroundColor: '#f5f5f5' } }} />
            <StatusBar barStyle="dark-content" />
            {renderContent()}
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    centerContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20,
    },
    scrollContent: {
        padding: 20,
        alignItems: 'center',
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
        width: 250,
        height: 250,
        borderRadius: 15,
        marginBottom: 20,
    },
    loadingOverlay: {
        position: 'absolute',
        backgroundColor: 'rgba(0,0,0,0.6)',
        width: 250,
        height: 250,
        borderRadius: 15,
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 20, // Match previewImage margin
    },
    loadingText: {
        color: '#fff',
        marginTop: 10,
        fontWeight: '600',
    },
    errorText: {
        color: '#7f8c8d',
        fontSize: 16,
        marginVertical: 15,
        textAlign: 'center',
    },
    retryButton: {
        paddingVertical: 10,
        paddingHorizontal: 20,
        backgroundColor: '#ecf0f1',
        borderRadius: 20,
    },
    retryButtonText: {
        color: '#2c3e50',
        fontWeight: '600',
    },
    // Envelope Styles (Similar to previous)
    envelope: {
        width: '100%',
        backgroundColor: '#ffffff',
        borderRadius: 8,
        padding: 25,
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 3.84,
        elevation: 5,
        borderWidth: 1,
        borderColor: '#e0e0e0',
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 20,
        borderBottomWidth: 2,
        borderBottomColor: '#2c3e50',
        paddingBottom: 15,
    },
    hospitalName: {
        fontSize: 22,
        fontWeight: 'bold',
        color: '#2c3e50',
    },
    stampBox: {
        borderWidth: 2,
        borderColor: '#c0392b',
        borderRadius: 50,
        paddingVertical: 5,
        paddingHorizontal: 10,
        transform: [{ rotate: '-15deg' }],
    },
    stampText: {
        color: '#c0392b',
        fontWeight: 'bold',
        fontSize: 12,
    },
    infoRow: {
        flexDirection: 'row',
        marginBottom: 15,
    },
    label: {
        fontSize: 14,
        color: '#7f8c8d',
        marginRight: 8,
    },
    value: {
        fontSize: 14,
        fontWeight: '600',
        color: '#34495e',
    },
    divider: {
        height: 1,
        backgroundColor: '#bdc3c7',
        marginVertical: 15,
    },
    dashedDivider: {
        height: 1,
        borderWidth: 1,
        borderColor: '#bdc3c7',
        borderStyle: 'dashed',
        borderRadius: 1,
        marginVertical: 20,
    },
    section: {
        marginVertical: 10,
    },
    sectionTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#2c3e50',
        marginBottom: 10,
    },
    bodyText: {
        fontSize: 15,
        lineHeight: 22,
        color: '#34495e',
    },
    resultThumbnail: {
        width: '100%',
        height: 150,
        borderRadius: 8,
        marginBottom: 10,
        resizeMode: 'cover',
    },
    pillContainer: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 8,
    },
    pillBadge: {
        backgroundColor: '#e3f2fd',
        paddingVertical: 6,
        paddingHorizontal: 12,
        borderRadius: 20,
        borderWidth: 1,
        borderColor: '#90caf9',
    },
    pillText: {
        color: '#1e88e5',
        fontSize: 14,
        fontWeight: '600',
    },
    placeholderText: {
        color: '#bdc3c7',
        fontStyle: 'italic',
    },
    warningBox: {
        backgroundColor: '#ffebee',
        padding: 15,
        borderRadius: 8,
        borderLeftWidth: 4,
        borderLeftColor: '#e57373',
    },
    warningText: {
        color: '#c62828',
        fontSize: 15,
        lineHeight: 22,
        fontWeight: '500',
    },
    newAnalysisButton: {
        marginTop: 20,
        paddingVertical: 12,
        backgroundColor: '#f8f9fa',
        borderWidth: 1,
        borderColor: '#bdc3c7',
        borderRadius: 8,
        alignItems: 'center',
    },
    newAnalysisButtonText: {
        color: '#2c3e50',
        fontWeight: '600',
    },
    footer: {
        marginTop: 40,
        alignItems: 'center',
        borderTopWidth: 1,
        borderTopColor: '#ecf0f1',
        paddingTop: 20,
    },
    footerText: {
        fontSize: 11,
        color: '#95a5a6',
        marginBottom: 5,
        textAlign: 'center',
    },
    pharmacyName: {
        fontSize: 14,
        fontWeight: 'bold',
        color: '#7f8c8d',
    },
});

export default FoodAnalysisScreen;

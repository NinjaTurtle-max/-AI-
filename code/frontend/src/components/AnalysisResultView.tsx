import React from "react";
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Pressable, Alert } from "react-native";
import { Ionicons } from "@expo/vector-icons";

type Props = {
    result: any;
    onAddPill: (pill: { id: string; name: string; description?: string }) => void;
    onReset: () => void;
};

export default function AnalysisResultView({ result, onAddPill, onReset }: Props) {
    // Extract data based on mode (supports both 'medications' and 'prescribed_drugs' structure)
    const drugList = result.medications || result.prescribed_drugs || [];
    const schedule = result.schedule;
    const precautions = result.precautions;
    const institution = result.institution;
    const patient = result.patient;
    const diagnosis = result.diagnosis_codes;

    return (
        <ScrollView contentContainerStyle={styles.container}>
            {/* Header Section */}
            <View style={styles.headerSection}>
                <Text style={styles.headerTitle}>분석 결과</Text>
                <View style={styles.stampBox}>
                    <Text style={styles.stampText}>AI 분석 완료</Text>
                </View>
            </View>

            {/* Hospital / Patient Info */}
            {(institution || patient) && (
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>[ 기본 정보 ]</Text>
                    <View style={styles.infoBox}>
                        {!!institution && (
                            <View style={styles.infoRow}>
                                <Ionicons name="business-outline" size={16} color="#555" />
                                <Text style={styles.infoText}>{institution}</Text>
                            </View>
                        )}
                        {!!patient && (
                            <View style={styles.infoRow}>
                                <Ionicons name="person-outline" size={16} color="#555" />
                                <Text style={styles.infoText}>
                                    {typeof patient === 'string' ? patient : `${patient.name || ''} (${patient.dob || ''})`}
                                </Text>
                            </View>
                        )}
                        {diagnosis && diagnosis.length > 0 && (
                            <View style={styles.infoRow}>
                                <Ionicons name="medkit-outline" size={16} color="#555" />
                                <Text style={styles.infoText}>진단: {diagnosis.join(', ')}</Text>
                            </View>
                        )}
                    </View>
                </View>
            )}

            {/* Drug List */}
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>[ 검출된 약품 ]</Text>
                {drugList && drugList.length > 0 ? (
                    drugList.map((med: any, idx: number) => {
                        const medName = med.name || med.drug_name || "이름 미확인";
                        const medEffect = med.efficacy || med.effect || med.administer_method || "";

                        return (
                            <View key={idx} style={styles.drugItem}>
                                <View style={styles.drugInfo}>
                                    <Text style={styles.drugName}>{medName}</Text>
                                    {!!medEffect && <Text style={styles.drugEffect}>{medEffect}</Text>}
                                </View>
                                <Pressable
                                    onPress={() => onAddPill({
                                        id: `med-${Date.now()}-${idx}`,
                                        name: medName,
                                        description: medEffect || undefined
                                    })}
                                    hitSlop={10}
                                    style={({ pressed }) => [
                                        {
                                            width: 32, height: 32, borderRadius: 16, backgroundColor: '#f0f0f0',
                                            alignItems: 'center', justifyContent: 'center'
                                        },
                                        pressed && { opacity: 0.6 }
                                    ]}
                                >
                                    <Ionicons name="add" size={20} color="#333" />
                                </Pressable>
                            </View>
                        );
                    })
                ) : (
                    <Text style={styles.emptyText}>검출된 약품이 없습니다.</Text>
                )}
            </View>

            <View style={styles.divider} />

            {/* Schedule */}
            {schedule && (
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>[ 복용 스케줄 ]</Text>
                    <Text style={styles.bodyText}>
                        {typeof schedule === 'string' ? schedule : JSON.stringify(schedule, null, 2)}
                    </Text>
                </View>
            )}

            {/* Precautions */}
            {precautions && precautions.length > 0 && (
                <View style={styles.section}>
                    <Text style={[styles.sectionTitle, { color: '#e74c3c' }]}>[ 주의사항 ]</Text>
                    <View style={styles.warningBox}>
                        {Array.isArray(precautions) ? precautions.map((p: string, i: number) => (
                            <Text key={i} style={styles.warningText}>• {p}</Text>
                        )) : <Text style={styles.warningText}>{precautions}</Text>}
                    </View>
                </View>
            )}

            {/* Bottom Action */}
            <TouchableOpacity style={styles.resetButton} onPress={onReset}>
                <Text style={styles.resetButtonText}>다른 사진 분석하기</Text>
            </TouchableOpacity>

        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        padding: 20,
        backgroundColor: '#fff',
    },
    headerSection: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 20,
        borderBottomWidth: 1,
        borderBottomColor: '#eee',
        paddingBottom: 15,
    },
    headerTitle: {
        fontSize: 22,
        fontWeight: 'bold',
        color: '#2c3e50',
    },
    stampBox: {
        borderWidth: 1.5,
        borderColor: '#27ae60',
        borderRadius: 8,
        paddingVertical: 4,
        paddingHorizontal: 10,
    },
    stampText: {
        color: '#27ae60',
        fontWeight: '700',
        fontSize: 12,
    },
    section: {
        marginBottom: 20,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#34495e',
        marginBottom: 10,
    },
    infoBox: {
        backgroundColor: '#f8f9fa',
        padding: 15,
        borderRadius: 10,
    },
    infoRow: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 5,
        gap: 8,
    },
    infoText: {
        fontSize: 15,
        color: '#333',
    },
    drugItem: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: 12,
        backgroundColor: '#fff',
        borderRadius: 12,
        marginBottom: 10,
        borderWidth: 1,
        borderColor: '#e0e0e0',
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.05,
        shadowRadius: 2,
        elevation: 1,
    },
    drugInfo: {
        flex: 1,
        marginRight: 10,
    },
    drugName: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#2c3e50',
    },
    drugEffect: {
        fontSize: 13,
        color: '#7f8c8d',
        marginTop: 4,
    },
    addButton: {
        flexDirection: 'row',
        backgroundColor: '#3498db',
        paddingVertical: 6,
        paddingHorizontal: 12,
        borderRadius: 20,
        alignItems: 'center',
        gap: 4,
    },
    addButtonText: {
        color: '#fff',
        fontSize: 13,
        fontWeight: '600',
    },
    emptyText: {
        color: '#999',
        fontStyle: 'italic',
        textAlign: 'center',
        marginTop: 10,
    },
    divider: {
        height: 1,
        backgroundColor: '#eee',
        marginVertical: 10,
    },
    bodyText: {
        fontSize: 15,
        lineHeight: 22,
        color: '#333',
    },
    warningBox: {
        backgroundColor: '#fff5f5',
        padding: 15,
        borderRadius: 8,
        borderLeftWidth: 3,
        borderLeftColor: '#e74c3c',
    },
    warningText: {
        fontSize: 14,
        color: '#c0392b',
        marginBottom: 4,
        lineHeight: 20,
    },
    resetButton: {
        marginTop: 20,
        backgroundColor: '#2c3e50',
        paddingVertical: 15,
        borderRadius: 10,
        alignItems: 'center',
        marginBottom: 40,
    },
    resetButtonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: 'bold',
    },
});

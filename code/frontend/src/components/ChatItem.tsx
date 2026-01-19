import React from "react";
import { Image, Text, View, Pressable } from "react-native";
import { Msg } from "../types/chat";
import { TypingBubble } from "./TypingBubble";
import { Ionicons } from "@expo/vector-icons";

export function ChatItem({
  item,
  loading,
  styles,
  onAddPill,
}: {
  item: Msg;
  loading: boolean;
  styles: any;
  onAddPill?: (pill: { id: string; name: string }) => void;
}) {
  if (item.type === "image") {
    return (
      <View style={[styles.bubble, styles.userBubble]}>
        <Image source={{ uri: item.uri }} style={styles.chatImage} />
        {!!item.text && (
          <Text style={[styles.msgText, { marginTop: 8 }]}>{item.text}</Text>
        )}
      </View>
    );
  }

  if (item.type === "identify") {
    const p = item.payload;
    const bestId = p.best_match?.id;
    const bestName = p.best_match?.name;
    const bestEffect = p.best_match?.effect;
    const bestMethod = p.best_match?.administer_method;

    return (
      <View style={[styles.bubble, styles.assistantBubble, { width: "90%" }]}>
        <Text style={[styles.title, { fontSize: 16, marginBottom: 12 }]}>🔎 약 식별 결과</Text>
        {p.extracted_text && (
          <Text style={[styles.small, { marginBottom: 12, color: '#888' }]}>
            인식된 텍스트: {p.extracted_text}
          </Text>
        )}

        {/* Display all candidates with enhanced design */}
        {p.candidates.map((c, idx) => (
          <View
            key={c.id}
            style={{
              marginBottom: 10,
              padding: 12,
              backgroundColor: idx === 0 ? '#f8f9ff' : '#fff',
              borderRadius: 12,
              borderWidth: idx === 0 ? 2 : 1,
              borderColor: idx === 0 ? '#667eea' : '#e0e0e0',
              shadowColor: "#000",
              shadowOffset: { width: 0, height: 1 },
              shadowOpacity: 0.05,
              shadowRadius: 2,
              elevation: 1
            }}
          >
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <View style={{ flex: 1, marginRight: 8 }}>
                {/* Pill Name */}
                <Text style={{ fontWeight: '700', fontSize: 15, color: '#333', marginBottom: 6 }}>
                  {idx === 0 && '⭐ '}{c.name}
                </Text>

                {/* Effect */}
                {c.effect && (
                  <View style={{ flexDirection: 'row', alignItems: 'flex-start', marginBottom: 4 }}>
                    <Text style={{ fontSize: 12, color: '#666', marginRight: 4 }}>💊</Text>
                    <Text style={{ fontSize: 12, color: '#666', flex: 1 }} numberOfLines={2}>
                      {c.effect}
                    </Text>
                  </View>
                )}

                {/* Administration Method */}
                {c.administer_method && (
                  <View style={{ flexDirection: 'row', alignItems: 'flex-start' }}>
                    <Text style={{ fontSize: 12, color: '#666', marginRight: 4 }}>📋</Text>
                    <Text style={{ fontSize: 12, color: '#666', flex: 1 }} numberOfLines={3}>
                      {c.administer_method}
                    </Text>
                  </View>
                )}

                {/* Score indicator */}
                {idx === 0 && (
                  <Text style={{ fontSize: 11, color: '#667eea', marginTop: 4, fontWeight: '600' }}>
                    일치도: {c.score}%
                  </Text>
                )}
              </View>

              {/* Add button */}
              {idx === 0 && bestId && (
                <Pressable
                  onPress={() => onAddPill?.({ id: bestId, name: bestName || "" })}
                  disabled={loading}
                  hitSlop={10}
                  style={({ pressed }) => [
                    {
                      width: 36, height: 36, borderRadius: 18,
                      backgroundColor: '#667eea',
                      alignItems: 'center', justifyContent: 'center',
                      shadowColor: "#667eea",
                      shadowOffset: { width: 0, height: 2 },
                      shadowOpacity: 0.3,
                      shadowRadius: 4,
                      elevation: 3
                    },
                    (pressed || loading) && { opacity: 0.7, transform: [{ scale: 0.95 }] },
                  ]}
                >
                  <Ionicons name="add" size={22} color="#fff" />
                </Pressable>
              )}
            </View>
          </View>
        ))}

        {p.candidates.length === 0 && (
          <Text style={[styles.msgText, { color: '#999', marginTop: 8 }]}>
            약물을 찾을 수 없습니다. 다른 각도에서 더 선명한 사진을 찍어주세요.
          </Text>
        )}

      </View>
    );
  }

  if (item.type === "prescription_result") {
    // Merge data from both modes
    // mode="prescription" (Pill Bag): medications, schedule, precautions
    // mode="hospital_prescription" (Hospital): prescribed_drugs, patient, diagnosis_codes, institution
    const p = item.payload;
    const drugList = p.medications || p.prescribed_drugs || [];
    const schedule = p.schedule;
    const precautions = p.precautions;

    // Hospital specific fields
    const institution = p.institution;
    const patient = p.patient;
    const diagnosis = p.diagnosis_codes;

    return (
      <View style={[styles.bubble, styles.assistantBubble, { width: "90%" }]}>
        <Text style={[styles.title, { fontSize: 16, marginBottom: 12 }]}>📋 분석 결과</Text>

        {/* Hospital Info (if exists) */}
        {(institution || patient) && (
          <View style={{ marginBottom: 12, paddingBottom: 8, borderBottomWidth: 1, borderBottomColor: '#eee' }}>
            {!!institution && <Text style={[styles.msgText, { fontWeight: '700' }]}>🏥 {institution}</Text>}
            {!!patient && (
              <Text style={[styles.msgText, { color: '#555' }]}>
                👤 {typeof patient === 'string' ? patient : `${patient.name || ''} (${patient.dob || ''})`}
              </Text>
            )}
            {diagnosis && diagnosis.length > 0 && (
              <Text style={[styles.small, { color: '#888', marginTop: 4 }]}>
                진단코드: {diagnosis.join(', ')}
              </Text>
            )}
          </View>
        )}

        {/* Medications List */}
        <Text style={[styles.title, { marginBottom: 6 }]}>💊 검출된 약품</Text>
        {drugList && Array.isArray(drugList) && drugList.length > 0 ? (
          drugList.map((med: any, idx: number) => {
            const medName = med.name || med.drug_name || med.약이름 || "이름 미확인";
            const medEffect = med.efficacy || med.effect || med.효능 || med.administer_method || ""; // administer_method might be in hospital mode
            return (
              <View key={idx} style={{
                flexDirection: 'row',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: 8,
                padding: 10,
                backgroundColor: '#fff',
                borderRadius: 12,
                shadowColor: "#000",
                shadowOffset: { width: 0, height: 1 },
                shadowOpacity: 0.05,
                shadowRadius: 2,
                elevation: 1
              }}>
                <View style={{ flex: 1, marginRight: 8 }}>
                  <Text style={{ fontWeight: '700', fontSize: 14, color: '#333' }}>{medName}</Text>
                  {!!medEffect && <Text style={{ fontSize: 12, color: '#666', marginTop: 2 }}>{medEffect}</Text>}
                </View>
                <Pressable
                  onPress={() => onAddPill?.({ id: `med-${Date.now()}-${idx}`, name: medName })}
                  disabled={loading}
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
          })) : (
          <Text style={[styles.msgText, { color: '#999', marginBottom: 10 }]}>검출된 약품이 없습니다.</Text>
        )}


        {/* Schedule (if exists) */}
        {schedule && (
          <View style={{ marginTop: 8 }}>
            <Text style={[styles.title, { marginBottom: 4 }]}>🕒 복용 스케줄</Text>
            <Text style={[styles.msgText, { color: '#444' }]}>
              {typeof schedule === 'string' ? schedule : JSON.stringify(schedule, null, 2)}
            </Text>
          </View>
        )}

        {/* Precautions (if exists) */}
        {precautions && precautions.length > 0 && (
          <View style={{ marginTop: 12 }}>
            <Text style={[styles.title, { marginBottom: 4 }]}>⚠️ 주의사항</Text>
            {Array.isArray(precautions) ? precautions.map((p: string, i: number) => (
              <Text key={i} style={[styles.msgText, { color: '#444', marginBottom: 2 }]}>• {p}</Text>
            )) : <Text style={[styles.msgText, { color: '#444' }]}>{precautions}</Text>}
          </View>
        )}
      </View>
    );
  }

  if (item.type === "typing") {
    return <TypingBubble styles={styles} />;
  }

  if (item.type === "pill_result") {
    return (
      <View style={[styles.bubble, styles.assistantBubble, styles.pillResultBubble]}>
        <Text style={styles.msgText}>이 약은 "{item.payload.name}"로 보여요.</Text>

        <Pressable
          onPress={() => onAddPill?.(item.payload)}
          disabled={loading}
          hitSlop={10}
          style={({ pressed }) => [
            styles.plusBtn,
            (pressed || loading) && { transform: [{ scale: 0.92 }], opacity: 0.85 },
            loading && { opacity: 0.4 },
          ]}
        >
          <Ionicons name="add" size={18} color="#111" />
        </Pressable>
      </View>
    );
  }

  const isUser = item.role === "user";
  return (
    <View style={[styles.bubble, isUser ? styles.userBubble : styles.assistantBubble]}>
      <Text style={styles.msgText}>{item.text}</Text>
    </View>
  );
}

import React from "react";
import { SafeAreaView, View, Text, Pressable, StyleSheet, ScrollView } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import { LinearGradient } from 'expo-linear-gradient';

export default function HomeScreen() {
  const router = useRouter();

  const features = [
    {
      id: 'pill',
      title: '알약 식별',
      desc: '약 사진으로 정보 확인',
      icon: 'medical',
      gradient: ['#667eea', '#764ba2'],
      route: '/chat'
    },
    {
      id: 'prescription',
      title: '처방전 분석',
      desc: '병원 처방전 자동 분석',
      icon: 'document-text',
      gradient: ['#f093fb', '#f5576c'],
      route: '/prescription'
    },
    {
      id: 'medicine_bag',
      title: '약봉투 분석',
      desc: '약국 약봉투 정보 추출',
      icon: 'bag-handle',
      gradient: ['#4facfe', '#00f2fe'],
      route: '/medicine_bag'
    },
    {
      id: 'food',
      title: '음식 분석',
      desc: '음식 상호작용 확인',
      icon: 'restaurant',
      gradient: ['#43e97b', '#38f9d7'],
      route: '/food'
    },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Header Section */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>안녕하세요 </Text>
            <Text style={styles.title}>앱 이름</Text>
          </View>
          <View style={styles.badge}>
            <Ionicons name="shield-checkmark" size={20} color="#27ae60" />
          </View>
        </View>

        {/* Info Card */}
        <View style={styles.infoCard}>
          <Ionicons name="information-circle" size={24} color="#3498db" />
          <View style={styles.infoTextContainer}>
            <Text style={styles.infoTitle}>빠르고 정확한 약물 정보</Text>
            <Text style={styles.infoDesc}>사진 한 장으로 모든 정보를 확인하세요</Text>
          </View>
        </View>

        {/* Features Grid */}
        <Text style={styles.sectionTitle}>서비스</Text>
        <View style={styles.gridContainer}>
          {features.map((feature, index) => (
            <Pressable
              key={feature.id}
              style={({ pressed }) => [
                styles.featureCard,
                pressed && styles.pressed
              ]}
              onPress={() => router.push(feature.route as any)}
            >
              <LinearGradient
                colors={feature.gradient}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={styles.gradientCard}
              >
                <View style={styles.iconCircle}>
                  <Ionicons name={feature.icon as any} size={32} color="#fff" />
                </View>
                <Text style={styles.featureTitle}>{feature.title}</Text>
                <Text style={styles.featureDesc}>{feature.desc}</Text>
                <View style={styles.arrowContainer}>
                  <Ionicons name="arrow-forward" size={20} color="rgba(255,255,255,0.8)" />
                </View>
              </LinearGradient>
            </Pressable>
          ))}
        </View>

        {/* Bottom Info */}
        <View style={styles.bottomInfo}>
          <Text style={styles.bottomText}>모든 분석 결과는 AI로 생성됩니다</Text>
          <Text style={styles.bottomSubText}>전문의와 상담을 권장합니다</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f8f9fa"
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 40,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 24,
  },
  greeting: {
    fontSize: 16,
    color: '#7f8c8d',
    marginBottom: 4,
    fontWeight: '500',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2c3e50',
  },
  badge: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#e8f5e9',
    alignItems: 'center',
    justifyContent: 'center',
  },
  infoCard: {
    flexDirection: 'row',
    backgroundColor: '#e3f2fd',
    padding: 16,
    borderRadius: 16,
    marginBottom: 28,
    borderLeftWidth: 4,
    borderLeftColor: '#3498db',
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  infoTextContainer: {
    marginLeft: 12,
    flex: 1,
  },
  infoTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: '#2c3e50',
    marginBottom: 4,
  },
  infoDesc: {
    fontSize: 13,
    color: '#7f8c8d',
    lineHeight: 18,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 16,
  },
  gridContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  featureCard: {
    width: '48%',
    marginBottom: 16,
  },
  gradientCard: {
    borderRadius: 20,
    padding: 20,
    minHeight: 180,
    justifyContent: 'space-between',
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    elevation: 6,
  },
  iconCircle: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: 'rgba(255,255,255,0.3)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  featureTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 6,
  },
  featureDesc: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.9)',
    lineHeight: 18,
    marginBottom: 8,
  },
  arrowContainer: {
    alignSelf: 'flex-end',
  },
  pressed: {
    opacity: 0.9,
    transform: [{ scale: 0.98 }],
  },
  bottomInfo: {
    alignItems: 'center',
    marginTop: 20,
    paddingTop: 20,
    borderTopWidth: 1,
    borderTopColor: '#ecf0f1',
  },
  bottomText: {
    fontSize: 13,
    color: '#95a5a6',
    fontWeight: '600',
    marginBottom: 4,
  },
  bottomSubText: {
    fontSize: 12,
    color: '#bdc3c7',
  },
});

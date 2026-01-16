import React, { useEffect, useRef, useState } from "react";
import { SafeAreaView, View, Text, TextInput, Pressable, Alert, Keyboard } from "react-native";
import * as Location from "expo-location";
import MapView, { Marker, Region } from "react-native-maps";

type Place = {
  place_id: string;
  name: string;
  vicinity?: string;
  formatted_address?: string;
  geometry: { location: { lat: number; lng: number } };
};

const GOOGLE_PLACES_KEY = "AIzaSyAsoaoGNslHXXzF7g2KFkhZCbhjTlZkpXE"; 

export default function PharmacySearchScreen() {
  const mapRef = useRef<MapView | null>(null);

  const [region, setRegion] = useState<Region | null>(null);
  const [places, setPlaces] = useState<Place[]>([]);
  const [q, setQ] = useState("");

  const fetchNearbyPharmacies = async (lat: number, lng: number) => {
    try {
      const url =
        `https://maps.googleapis.com/maps/api/place/nearbysearch/json` +
        `?location=${lat},${lng}` +
        `&radius=2000` +
        `&type=pharmacy` +
        `&key=${GOOGLE_PLACES_KEY}`;

      const res = await fetch(url);
      const json = await res.json();

      if (json.status !== "OK" && json.status !== "ZERO_RESULTS") {
        throw new Error(json.error_message ?? `Places error: ${json.status}`);
      }

      setPlaces(json.results ?? []);
    } catch (e: any) {
      Alert.alert("오류", e?.message ?? "주변 약국 검색 실패");
    }
  };

  const fetchByKeyword = async (keyword: string, lat?: number, lng?: number) => {
    try {
      const query = encodeURIComponent(`${keyword} 약국`);
      const locationBias =
        lat != null && lng != null ? `&location=${lat},${lng}&radius=5000` : "";

      const url =
        `https://maps.googleapis.com/maps/api/place/textsearch/json` +
        `?query=${query}` +
        `${locationBias}` +
        `&key=${GOOGLE_PLACES_KEY}`;

      const res = await fetch(url);
      const json = await res.json();

      if (json.status !== "OK" && json.status !== "ZERO_RESULTS") {
        throw new Error(json.error_message ?? `Places error: ${json.status}`);
      }

      setPlaces(json.results ?? []);

      const first = (json.results ?? [])[0] as Place | undefined;
      if (first) {
        const { lat: fLat, lng: fLng } = first.geometry.location;
        mapRef.current?.animateToRegion(
          { latitude: fLat, longitude: fLng, latitudeDelta: 0.02, longitudeDelta: 0.02 },
          250
        );
      }
    } catch (e: any) {
      Alert.alert("오류", e?.message ?? "검색 실패");
    }
  };

  const init = async () => {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== "granted") {
      Alert.alert("권한 필요", "주변 약국을 찾으려면 위치 권한이 필요해요.");
      return;
    }

    const loc = await Location.getCurrentPositionAsync({
      accuracy: Location.Accuracy.Balanced,
    });

    const lat = loc.coords.latitude;
    const lng = loc.coords.longitude;

    const r: Region = {
      latitude: lat,
      longitude: lng,
      latitudeDelta: 0.01,
      longitudeDelta: 0.01,
    };
    setRegion(r);

    await fetchNearbyPharmacies(lat, lng);
  };

  useEffect(() => {
    init();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onSearch = async () => {
    Keyboard.dismiss();
    const keyword = q.trim();

    if (!region) {
      await init();
      return;
    }

    if (!keyword) {
      await fetchNearbyPharmacies(region.latitude, region.longitude);
      return;
    }

    await fetchByKeyword(keyword, region.latitude, region.longitude);
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#fff" }}>
      {/*  지도 전체 */}
      {region ? (
        <MapView
          ref={mapRef}
          style={{ flex: 1 }}
          initialRegion={region}
          showsUserLocation
          showsMyLocationButton
        >
          {places.map((p) => (
            <Marker
              key={p.place_id}
              coordinate={{
                latitude: p.geometry.location.lat,
                longitude: p.geometry.location.lng,
              }}
              title={p.name}
              description={p.vicinity ?? p.formatted_address}
            >
              {/*  알약 모양 커스텀 마커 */}
              <View
                style={{
                  width: 34,
                  height: 34,
                  borderRadius: 17,
                  backgroundColor: "#111",
                  alignItems: "center",
                  justifyContent: "center",
                  borderWidth: 2,
                  borderColor: "#fff",
                }}
              >
                <Text style={{ fontSize: 18 }}>💊</Text>
              </View>
            </Marker>
          ))}
        </MapView>
      ) : (
        <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
          <Text>위치 불러오는 중…</Text>
        </View>
      )}

      {/* 검색바를 지도 위에 floating */}
      <View
        pointerEvents="box-none"
        style={{
          position: "absolute",
          top: 12,
          left: 0,
          right: 0,
          paddingHorizontal: 16,
        }}
      >
        <View
          style={{
            flexDirection: "row",
            gap: 10,
            alignItems: "center",
            backgroundColor: "#fff",
            borderRadius: 16,
            padding: 10,
            borderWidth: 1,
            borderColor: "#eee",
            shadowColor: "#000",
            shadowOpacity: 0.08,
            shadowRadius: 10,
            shadowOffset: { width: 0, height: 4 },
          }}
        >
          <TextInput
            value={q}
            onChangeText={setQ}
            placeholder="약국 이름/지역 검색"
            returnKeyType="search"
            onSubmitEditing={onSearch}
            style={{ flex: 1, paddingVertical: 8, paddingHorizontal: 10 }}
          />
          <Pressable
            onPress={onSearch}
            style={({ pressed }) => [
              {
                paddingVertical: 10,
                paddingHorizontal: 14,
                borderRadius: 12,
                backgroundColor: "#111",
              },
              pressed && { opacity: 0.85, transform: [{ scale: 0.98 }] },
            ]}
          >
            <Text style={{ color: "#fff", fontWeight: "900" }}>검색</Text>
          </Pressable>
        </View>
      </View>
    </SafeAreaView>
  );
}

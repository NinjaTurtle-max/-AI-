import { useState } from "react";
import * as ImagePicker from "expo-image-picker";
import { analyzeFoodApi } from "../services/foodApi";

export interface FoodAnalysisResult {
    type: string;
    detected_items: string[];
    main_ingredients: string[];
    warning_message: string;
}

export function useFoodAnalysis() {
    const [imageUri, setImageUri] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<FoodAnalysisResult | null>(null);
    const [error, setError] = useState<string | null>(null);

    const pickFromCamera = async () => {
        try {
            const perm = await ImagePicker.requestCameraPermissionsAsync();
            if (!perm.granted) {
                alert("카메라 권한이 필요합니다.");
                return;
            }

            const res = await ImagePicker.launchCameraAsync({
                quality: 0.8,
                mediaTypes: ImagePicker.MediaTypeOptions.Images,
            });

            if (!res.canceled) {
                setImageUri(res.assets[0].uri);
                setResult(null); // Reset previous result
                setError(null);
                await analyzeImage(res.assets[0].uri);
            }
        } catch (e) {
            console.error(e);
            alert("카메라 실행 중 오류가 발생했습니다.");
        }
    };

    const pickFromGallery = async () => {
        try {
            const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
            if (!perm.granted) {
                alert("사진첩 권한이 필요합니다.");
                return;
            }

            const res = await ImagePicker.launchImageLibraryAsync({
                quality: 0.8,
                mediaTypes: ImagePicker.MediaTypeOptions.Images,
            });

            if (!res.canceled) {
                setImageUri(res.assets[0].uri);
                setResult(null);
                setError(null);
                await analyzeImage(res.assets[0].uri);
            }
        } catch (e) {
            console.error(e);
            alert("이미지 선택 중 오류가 발생했습니다.");
        }
    };

    const analyzeImage = async (uri: string) => {
        setLoading(true);
        setError(null);
        try {
            const data = await analyzeFoodApi(uri);

            // Backend might return { error: "..." } even with 200 OK
            if (data.error) {
                console.error("Backend returned error:", data.error);
                setError(typeof data.error === 'string' ? data.error : "분석 중 오류가 발생했습니다.");
                setResult(null);
            } else {
                setResult(data);
                // Debugging log
                console.log("Food Analysis Result:", JSON.stringify(data));
            }
        } catch (e) {
            console.error("Analysis failed", e);
            setError("분석에 실패했습니다. 다시 시도해주세요.");
        } finally {
            setLoading(false);
        }
    };

    const resetAnalysis = () => {
        setImageUri(null);
        setResult(null);
        setError(null);
    };

    return {
        imageUri,
        loading,
        result,
        error,
        pickFromCamera,
        pickFromGallery,
        resetAnalysis
    };
}

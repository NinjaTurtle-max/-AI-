import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";

export type UserProfile = {
    height: number; // cm
    weight: number; // kg
    bmi: number; // auto-calculated
    gender: "남성" | "여성" | "기타" | "";
};

type ProfileContextValue = {
    profile: UserProfile;
    updateProfile: (updates: Partial<UserProfile>) => void;
    saveProfile: () => Promise<void>;
    isLoading: boolean;
};

const PROFILE_STORAGE_KEY = "@user_profile";

const defaultProfile: UserProfile = {
    height: 0,
    weight: 0,
    bmi: 0,
    gender: "",
};

const ProfileContext = createContext<ProfileContextValue | null>(null);

export function ProfileProvider({ children }: { children: React.ReactNode }) {
    const [profile, setProfile] = useState<UserProfile>(defaultProfile);
    const [isLoading, setIsLoading] = useState(true);

    // Load profile from AsyncStorage on mount
    useEffect(() => {
        loadProfile();
    }, []);

    const loadProfile = async () => {
        try {
            const stored = await AsyncStorage.getItem(PROFILE_STORAGE_KEY);
            if (stored) {
                const parsed = JSON.parse(stored);
                setProfile(parsed);
            }
        } catch (error) {
            console.error("Failed to load profile:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const calculateBMI = (height: number, weight: number): number => {
        if (height <= 0 || weight <= 0) return 0;
        const heightInMeters = height / 100;
        return parseFloat((weight / (heightInMeters * heightInMeters)).toFixed(1));
    };

    const updateProfile = (updates: Partial<UserProfile>) => {
        setProfile((prev) => {
            const newProfile = { ...prev, ...updates };

            // Auto-calculate BMI if height or weight changed
            if (updates.height !== undefined || updates.weight !== undefined) {
                newProfile.bmi = calculateBMI(newProfile.height, newProfile.weight);
            }

            return newProfile;
        });
    };

    const saveProfile = async () => {
        try {
            await AsyncStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(profile));
        } catch (error) {
            console.error("Failed to save profile:", error);
            throw error;
        }
    };

    const value = useMemo(
        () => ({ profile, updateProfile, saveProfile, isLoading }),
        [profile, isLoading]
    );

    return <ProfileContext.Provider value={value}>{children}</ProfileContext.Provider>;
}

export function useProfile() {
    const ctx = useContext(ProfileContext);
    if (!ctx) throw new Error("useProfile must be used within ProfileProvider");
    return ctx;
}

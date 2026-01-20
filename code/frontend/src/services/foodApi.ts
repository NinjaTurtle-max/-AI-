import { BACKEND_URL } from "../config";

export async function analyzeFoodApi(imageUri: string): Promise<any> {
    const formData = new FormData();
    formData.append("file", {
        uri: imageUri,
        name: "food.jpg", // Filename doesn't strictly matter for backend temp logic but good to have extension
        type: "image/jpeg",
    } as any);

    try {
        const response = await fetch(`${BACKEND_URL}/analyze-food-interaction`, {
            method: "POST",
            body: formData,
            headers: {
                "Content-Type": "multipart/form-data",
            },
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        // The backend returns the JSON result directly (fields: type, detected_items, main_ingredients, warning_message)
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Food Analysis API Error:", error);
        throw error;
    }
}

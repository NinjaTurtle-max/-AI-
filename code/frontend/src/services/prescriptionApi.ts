const BACKEND_URL = "http://127.0.0.1:8000";

export async function analyzePrescriptionApi(imageUri: string, mode: "prescription" | "hospital_prescription" = "prescription"): Promise<any> {

  const formData = new FormData();
  formData.append("file", {
    uri: imageUri,
    name: "prescription.jpg",
    type: "image/jpeg",
  } as any);

  try {
    const response = await fetch(`${BACKEND_URL}/register-drug-image?mode=${mode}`, {
      method: "POST",
      body: formData,
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const data = await response.json();
    // data structure: { status: "success", message: "...", detected_data: { medications: [...], ... } }
    return data.detected_data;
  } catch (error) {
    console.error("Prescription API Error:", error);
    throw error;
  }
}

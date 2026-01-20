import { BACKEND_URL } from "../config";

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
    console.log("📥 [FRONTEND] Received data:", JSON.stringify(data, null, 2));
    console.log("📥 [FRONTEND] raw_data:", JSON.stringify(data.raw_data, null, 2));
    // data structure: { status: "success", message: "...", raw_data: { prescribed_drugs: [...], ... } }
    return data.raw_data;
  } catch (error) {
    console.error("Prescription API Error:", error);
    throw error;
  }
}

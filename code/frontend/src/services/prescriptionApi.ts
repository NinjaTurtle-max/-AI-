const BACKEND_URL = "http://127.0.0.1:8000";

export async function analyzePrescriptionApi(imageUri: string): Promise<string> {
    
  await new Promise((r) => setTimeout(r, 900));
  return " 처방전 분석 결과(예시)\n- 약A: 하루 2회\n- 약B: 식후 1정\n(추후 OCR 연동 예정)";
}

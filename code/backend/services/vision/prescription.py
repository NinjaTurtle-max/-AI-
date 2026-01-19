import json
import google.generativeai as genai
import PIL.Image

def analyze_prescription_doc(image_path, api_key, mode="prescription"):
    """
    약봉투(prescription) 또는 병원처방전(hospital_prescription) 분석
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    img = PIL.Image.open(image_path)

    base_instruction = """
    [OCR 및 의료 문서 분석]
    이미지에서 텍스트를 읽어 약 정보를 JSON으로 추출하세요.
    사진이 흐리거나 글자가 안 보이면 {"error": "INVALID_IMAGE"}를 반환하세요.
    """

    if mode == "prescription": # 약봉투
        prompt = base_instruction + """
        응답 형식: {
            "medications": [{"name": "약이름", "effect": "효능", "administer_method": "복용법"}], 
            "precautions": ["주의사항1", "주의사항2"], 
            "schedule": "복용스케줄"
        }
        """
    else: # 병원 처방전
        prompt = base_instruction + """
        응답 형식: {
            "prescribed_drugs": [{"name": "약이름", "administer_method": "투약량/횟수", "effect": "비고"}]
        }
        """

    try:
        response = model.generate_content([prompt, img])
        content = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        return {"error": f"문서 분석 실패: {str(e)}"}
import json
import google.generativeai as genai
import PIL.Image
import os
from urllib.parse import unquote  # [핵심] 키 디코딩용

def analyze_prescription_doc(image_path, api_key, mode="prescription"):
    """
    약봉투(prescription) 또는 병원처방전(hospital_prescription) 분석
    """
    # 1. API 키 안전 처리
    if not api_key:
        return {"error": "Gemini API 키가 없습니다."}
    
    # 인코딩된 키가 들어와도 안전하게 처리
    genai.configure(api_key=unquote(api_key))

    # 2. 이미지 로드
    try:
        if not os.path.exists(image_path):
            return {"error": f"파일 없음: {image_path}"}
        img = PIL.Image.open(image_path)
    except Exception as e:
        return {"error": f"이미지 로드 실패: {e}"}

    # 3. 모델 설정
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        return {"error": f"모델 로드 실패: {e}"}

    # 4. 프롬프트 설정
    base_instruction = """
    [OCR 및 의료 문서 분석 전문가]
    이미지에서 텍스트를 읽어 약 정보를 JSON 형식으로 정확하게 추출하세요.
    사진이 너무 흐리거나 글자가 식별 불가능하면 {"error": "INVALID_IMAGE"}를 반환하세요.
    """

    if mode == "prescription": # 약봉투 (약국)
        prompt = base_instruction + """
        [분석 대상: 약국 약봉투]
        약 이름, 효능, 복용법, 주의사항을 추출하세요.
        
        응답 형식 (JSON):
        {
            "medications": [
                {"name": "약이름", "effect": "효능(짧게)", "administer_method": "1일 3회 식후 30분 등"}
            ], 
            "precautions": ["주의사항1", "주의사항2"], 
            "schedule": "전체적인 복용 스케줄 요약"
        }
        """
    else: # 병원 처방전
        prompt = base_instruction + """
        [분석 대상: 병원 처방전]
        처방된 약품 목록과 투약량을 추출하세요.
        
        응답 형식 (JSON):
        {
            "prescribed_drugs": [
                {"name": "약이름", "administer_method": "1회 투약량 / 1일 투여횟수 / 총 투약일수", "effect": "비고란 내용(없으면 빈칸)"}
            ]
        }
        """

    # 5. 실행 및 파싱
    try:
        response = model.generate_content([prompt, img])
        content = response.text.strip()
        
        # JSON 클리닝 (Markdown 코드블록 제거)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        return json.loads(content)

    except json.JSONDecodeError:
        print(f"❌ 문서 분석 JSON 파싱 실패: {content}")
        return {"error": "AI 응답을 분석할 수 없습니다. (JSON 형식 오류)"}
    except Exception as e:
        return {"error": f"문서 분석 실패: {str(e)}"}
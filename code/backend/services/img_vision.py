import os
from dotenv import load_dotenv

# [핵심] 분리한 모듈들 import
# (폴더 안에 __init__.py가 있어야 import가 잘 됩니다)
from services.vision.pill_identifier import analyze_pill
from services.vision.prescription import analyze_prescription_doc
from services.vision.food_checker import analyze_food_interaction

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MFDS_SERVICE_KEY = os.getenv("KEY_E_DRUG")

def analyze_health_image(image_path, mode="pill_id", current_pill="알약명"):
    print("\n" + "="*60)
    print(f"[STEP 1] 이미지 분석 시작 (모드: {mode})")

    try:
        if not os.path.exists(image_path):
            return {"error": f"파일 없음: {image_path}"}
        img = PIL.Image.open(image_path)
    except Exception as e:
        return {"error": f"이미지 로드 실패: {e}"}

    # [모델 설정]
    try:
        # 우선 2.5 시도
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("🤖 모델: gemini-2.5-flash")
    except:
        # 2.5 실패 시 1.5-flash로 대체
        print("ℹ️ 2.5 로드 불가, gemini-1.5-flash로 전환")
        model = genai.GenerativeModel('gemini-1.5-flash')

    # [중요] 품질 검사 및 반려를 위한 공통 지침
    quality_check_instruction = """
    [이미지 품질 검사 단계]
    분석을 시작하기 전에 이미지 상태를 먼저 확인하세요.
    1. 사진이 너무 흐릿하거나(Blurry), 너무 어둡거나, 해상도가 낮아 글자나 형체를 알아볼 수 없는 경우.
    2. 해당 모드와 관련된 객체(알약, 약봉투, 처방전, 음식)가 사진에 전혀 없는 경우.
    
    위 두 가지 중 하나라도 해당하면, 즉시 아래 JSON 포맷으로만 응답하고 분석을 종료하세요:
    {"error": "INVALID_IMAGE", "reason": "사진이 너무 흐리거나 대상을 찾을 수 없습니다. 다시 선명하게 촬영해주세요."}
    
    이미지가 선명하고 대상이 있다면, 아래 요청을 수행하세요.
    ---------------------------------------------------
    """

    # [프롬프트 설정]
    if mode == "pill_id":
        prompt = quality_check_instruction + """
        이 알약 사진을 분석하여 식약처 DB 검색용 정보를 JSON으로 추출해.
        
        1. item_name: 약 이름이나 글자가 아주 명확하면 적고, 아니면 빈 문자열("").
        2. print_front: 알약 앞면 식별문자 (보이는 대로, 없으면 "").
        3. print_back: 알약 뒷면 식별문자 (없으면 "").
        4. color_class1: [하양, 노랑, 주황, 분홍, 빨강, 갈색, 연두, 초록, 청록, 파랑, 보라, 회색, 검정, 투명] 중 1택.
        5. drug_shape: [원형, 타원형, 장방형, 반원형, 삼각형, 사각형, 마름모형, 오각형, 육각형, 팔각형] 중 1택.
        
        응답 형식 (JSON):
        {"item_name": "", "print_front": "", "print_back": "", "color_class1": "", "drug_shape": ""}
        """
    elif mode == "prescription":
        prompt = quality_check_instruction + """
        이 약봉투 이미지를 분석해. JSON으로 출력해.
        응답 형식: {"medications": [{"name": "약이름", "effect": "효능", "administer_method": "복용법"}], "precautions": [], "schedule": ""}
        """
    elif mode == "hospital_prescription":
        prompt = quality_check_instruction + """
        이 병원 처방전을 분석해. JSON으로 출력해.
        응답 형식: {"prescribed_drugs": [{"name": "약이름", "administer_method": "", "effect": ""}]}
        """
    elif mode == "food":
        prompt = quality_check_instruction + f"""
        이 음식 사진을 분석해. '{current_pill}'과 상호작용 위험이 있는 성분을 찾아 JSON으로 출력해.
        응답 형식: {{"type": "food_interaction_analysis", "detected_items": [], "main_ingredients": [], "warning_message": ""}}
        """
    else:
        return {"error": "지원하지 않는 모드"}

    try:
        print("[STEP 2] Gemini 분석 중...")
        response = model.generate_content([prompt, img])
        content = response.text.strip()
        
        # JSON 클리닝
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        analysis_result = json.loads(content)
        
        # [신규] 반려 로직 처리
        if "error" in analysis_result and analysis_result["error"] == "INVALID_IMAGE":
            print(f"🚫 [반려] {analysis_result['reason']}")
            # API 호출 없이 에러 반환
            return analysis_result

        print(f"✅ 분석 완료: {str(analysis_result)[:100]}...")

        # 알약 식별 모드면 API 호출 연동
        if mode == "pill_id":
            # 알약 전문가에게 토스
            return analyze_pill(image_path, GEMINI_API_KEY, MFDS_SERVICE_KEY)
        
        # 2. 약봉투 / 처방전 모드
        elif mode in ["prescription", "hospital_prescription"]:
            # 문서 전문가에게 토스
            return analyze_prescription_doc(image_path, GEMINI_API_KEY, mode)
            
        # 3. 음식 궁합 모드
        elif mode == "food":
            # 음식 전문가에게 토스
            return analyze_food_interaction(image_path, GEMINI_API_KEY, current_pill)
            
        else:
            return {"error": "지원하지 않는 모드입니다."}

    except Exception as e:
        print(f"❌ [Router Error] {e}")
        return {"error": str(e)}

# 테스트 실행
if __name__ == "__main__":
    test_img = "/Users/ganghyeon-u/Desktop/알약사진_1.png"
    # 여기서 mode를 바꿔가며 테스트 가능
    res = analyze_health_image(test_img, mode="pill_id")
    import json
    print(json.dumps(res, indent=2, ensure_ascii=False))
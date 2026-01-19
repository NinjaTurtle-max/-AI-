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
    """
    [Main Router] 모드에 따라 적절한 전문가(모듈)에게 작업을 위임합니다.
    """
    if not os.path.exists(image_path):
        return {"error": f"파일 없음: {image_path}"}

    print(f"🔄 [Router] 분석 요청: {mode} / 경로: {image_path}")

    try:
        # 1. 알약 식별 모드
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
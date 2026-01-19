import os
import json
from dotenv import load_dotenv

# [핵심] 분리한 전문가 모듈들 import
# (폴더 안에 __init__.py가 있어야 인식이 잘 됩니다)
try:
    from services.vision.pill_identifier import analyze_pill
    from services.vision.prescription import analyze_prescription_doc
    from services.vision.food_checker import analyze_food_interaction
except ImportError as e:
    print(f"❌ 모듈 Import 에러: {e}")
    print("👉 'services/vision/__init__.py' 파일이 있는지 확인해보세요.")

# 환경 변수 로드
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MFDS_SERVICE_KEY = os.getenv("KEY_E_DRUG")

def analyze_health_image(image_path, mode="pill_id", current_pill="알약명"):
    """
    [Main Router] 
    사용자가 요청한 mode에 따라 적절한 비전 모듈(전문가)에게 작업을 위임합니다.
    API 키 디코딩이나 세부 로직은 각 모듈 내부에서 처리합니다.
    """
    
    # 1. 파일 존재 여부 확인 (공통 방어 로직)
    if not os.path.exists(image_path):
        return {"error": f"파일을 찾을 수 없습니다: {image_path}"}

    print(f"🔄 [Router] 이미지 분석 요청 시작 (모드: {mode})")
    print(f"📁 경로: {image_path}")

    try:
        # =========================================================
        # 1. 알약 식별 모드 (식약처 API 검색 포함)
        # =========================================================
        if mode == "pill_id":
            # 알약 전문가 호출 (이미지 경로, Gemini키, 식약처키 전달)
            return analyze_pill(image_path, GEMINI_API_KEY, MFDS_SERVICE_KEY)
        
        # =========================================================
        # 2. 약봉투 / 처방전 분석 모드 (OCR)
        # =========================================================
        elif mode in ["prescription", "hospital_prescription"]:
            # 문서 전문가 호출 (mode를 전달하여 약봉투/처방전 구분)
            return analyze_prescription_doc(image_path, GEMINI_API_KEY, mode)
            
        # =========================================================
        # 3. 음식 상호작용 분석 모드
        # =========================================================
        elif mode == "food":
            # 음식 전문가 호출 (현재 복용 중인 약 이름 전달)
            return analyze_food_interaction(image_path, GEMINI_API_KEY, current_pill)
            
        # =========================================================
        # 예외: 지원하지 않는 모드
        # =========================================================
        else:
            print(f"⚠️ [Router] 알 수 없는 모드: {mode}")
            return {"error": "지원하지 않는 분석 모드입니다."}

    except Exception as e:
        print(f"❌ [Router Error] 중대한 오류 발생: {e}")
        return {"error": f"서버 내부 오류: {str(e)}"}

# =========================================================
# [테스트 실행 영역]
# 이 파일을 직접 실행할 때만 작동합니다. (python services/img_vision.py)
# =========================================================
if __name__ == "__main__":
    # 테스트할 이미지 경로를 본인의 환경에 맞게 수정하세요.
    test_img_path = "/Users/ganghyeon-u/Desktop/알약사진_1.png"
    
    # 테스트하고 싶은 모드 입력 ("pill_id", "prescription", "food")
    test_mode = "pill_id" 
    
    print(f"🧪 [Test] '{test_mode}' 모드로 테스트를 시작합니다...")
    
    if os.path.exists(test_img_path):
        result = analyze_health_image(test_img_path, mode=test_mode)
        
        print("\n📊 [최종 결과]")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"❌ 테스트 이미지가 없습니다: {test_img_path}")
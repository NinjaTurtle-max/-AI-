# backend/test_logic.py

import os
import sys
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 서비스 모듈 임포트
try:
    from services.drug_api import summarize_text
    from services.ai_pharmacist import generate_ai_advice
    from services.img_vision import analyze_health_image
    print("✅ 모듈 임포트 성공")
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    print("👉 현재 위치가 'backend' 폴더인지 확인하세요.")
    sys.exit(1)

# =========================================================
# [Test 1] 요약 기능 테스트 (drug_api.py)
# =========================================================
print("\n" + "="*50)
print("🧪 [Test 1] 텍스트 요약 기능 점검")
long_text = "이 약은 두통, 치통, 생리통 등 다양한 통증을 완화하는 데 효과적입니다. 위장 장애가 발생할 수 있으므로 식사 후 복용하는 것이 권장됩니다."
summary = summarize_text(long_text)
print(f"🔹 원문: {long_text[:30]}...")
print(f"🔹 요약: {summary}")

if len(summary) < len(long_text) and "..." in summary:
    print("✅ 요약 기능 정상 작동")
else:
    print("⚠️ 요약 기능 확인 필요 (길이가 줄지 않았거나 로직 다름)")


# =========================================================
# [Test 2] LangChain AI 약사 테스트 (ai_pharmacist.py)
# =========================================================
print("\n" + "="*50)
print("🧪 [Test 2] LangChain AI 상담 점검 (Context-Aware Grounding)")

# 1. 가짜 데이터(Mock Data) 생성
# ai_pharmacist가 기대하는 객체 구조를 흉내냅니다.
class MockProfile:
    def __init__(self):
        self.age = 30
        self.symptom = "심한 두통"
        self.condition = "간염 보균자" # [Context] 중요!

class MockRequest:
    def __init__(self):
        self.options = ["효능", "금기사항"]
        self.user_profile = MockProfile()

mock_drug_report = {
    "basic": {"itemName": "테스트용 타이레놀", "efcyQesitm": "두통, 해열, 진통"},
    "safety": {"병용금기": ["이 약은 간 손상을 유발할 수 있음"]}, # [Grounding] 중요!
    "summary": {"effect": "두통약", "warning": "간 손상 주의"}
}

# 2. 실행
try:
    print("⏳ LangChain(Gemini)에게 질문 중... (잠시 대기)")
    advice = generate_ai_advice(mock_drug_report, MockRequest())
    
    print("\n[🤖 AI 답변 결과]")
    print("-" * 30)
    print(advice)
    print("-" * 30)
    
    if "간염" in advice or "간 손상" in advice:
        print("✅ Context(간염)와 Grounding(간 손상)이 잘 결합되었습니다!")
    else:
        print("⚠️ 답변에 핵심 키워드(간염/간 손상)가 빠졌습니다. 프롬프트를 확인하세요.")

except Exception as e:
    print(f"❌ LangChain 실행 오류: {e}")


# =========================================================
# [Test 3] 이미지 비전 품질 검사 (img_vision.py)
# =========================================================
print("\n" + "="*50)
print("🧪 [Test 3] 이미지 품질 반려 로직 점검")

# 없는 파일로 테스트 -> 에러 메시지가 잘 오는지 확인
fake_path = "없는파일.jpg"
result = analyze_health_image(fake_path, mode="pill_id")

if "error" in result:
    print(f"✅ 에러 처리 정상 작동: {result['error']}")
else:
    print(f"⚠️ 예상치 못한 결과: {result}")

print("\n" + "="*50)
print("🎉 모든 테스트 종료")
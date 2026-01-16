import os
import json
import PIL.Image
import google.generativeai as genai
from dotenv import load_dotenv

# 1. 환경 변수 로드 (.env 파일에 GEMINI_API_KEY가 있어야 합니다)
load_dotenv()

# 2. Gemini API 설정
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY or API_KEY == "YOUR_GEMINI_API_KEY":
    print("❌ 에러: API 키를 찾을 수 없습니다. .env 파일을 확인하세요.")
else:
    genai.configure(api_key=API_KEY)

def analyze_health_image(image_path, mode="prescription", current_pill="알약명"):
    """
    이미지 분석 수행 (약봉투, 병원 처방전, 음식 및 약물 상호작용 분석)
    
    Args:
        image_path (str): 이미지 파일 경로
        mode (str): 'prescription'(약봉투), 'hospital_prescription'(처방전), 'food'(음식분석)
        current_pill (str): 사용자가 현재 복용 중인 약 이름 (음식 모드에서 경고 문구 생성용)
    """
    try:
        if not os.path.exists(image_path):
            return {"error": f"파일을 찾을 수 없습니다: {image_path}"}
        img = PIL.Image.open(image_path)
    except Exception as e:
        return {"error": f"이미지 로드 실패: {e}"}

    # 모델 설정 (멀티모달에 최적화된 1.5 Flash 사용)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 3. 모드별 프롬프트 설정
    if mode == "prescription":  # [모드 1: 약국 약봉투]
        prompt = """
        이 이미지는 '약봉투'야. 약품 정보와 복약 안내를 분석해서 JSON으로 응답해줘.
        [추출 규칙]
        1. medications: 각 약의 이름, 성분, 효능, 투약 정보 추출.
        2. precautions: 주의사항(예: 졸음 주의, 위장장애 등) 리스트 추출.
        3. schedule: 아침, 점심, 저녁, 취침전 복용 여부와 조건(식후 30분 등) 추출.
        """

    elif mode == "hospital_prescription":  # [모드 2: 병원 처방전]
        prompt = """
        이 이미지는 '병원 처방전'이야. 다음 정보를 JSON으로 추출해줘.
        [추출 규칙]
        1. patient: 환자 성명과 생년월일.
        2. diagnosis_codes: 질병분류기호(K21, J00 등) 리스트.
        3. prescribed_drugs: 처방된 약품 목록과 투약 방법.
        4. institution: 발행한 병원 이름.
        """

    elif mode == "food":  # [모드 3: 음식 성분 및 약물 상호작용 경고]
        prompt = f"""
        이 사진 속 음식을 인식하고, 포함된 주요 식재료 성분을 분석해줘.
        특히 사용자가 복용 중인 '{current_pill}'과 상호작용할 위험이 있는 성분을 찾는 것이 핵심이야.

        [응답 규칙]
        1. detected_items: 인식된 음식 이름 리스트.
        2. main_ingredients: 들어간 주요 식재료 성분 (예: 대두, 우유, 자몽 등).
        3. warning_message: 식재료 중 '{current_pill}'과 충돌할 수 있는 성분(예: 대두)이 있다면, 
           "사진 속 음식에 포함된 '성분명'은 현재 복용 중인 {current_pill}과 먹으면 위험하오니 피하는 것이 좋을 것 같아요" 
           느낌으로 친절한 경고 문구를 작성해줘. 위험 성분이 없으면 "특이사항 없습니다."라고 해줘.

        응답 형식:
        {{
          "type": "food_interaction_analysis",
          "detected_items": ["음식명"],
          "main_ingredients": ["성분1", "성분2"],
          "warning_message": "경고 메시지 내용"
        }}
        """

    else:
        return {"error": "지원하지 않는 모드입니다."}

    try:
        # 모델 분석 실행
        response = model.generate_content([prompt, img])
        content = response.text.strip()
        
        # JSON 파싱 안정화 로직
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        return json.loads(content)
    except Exception as e:
        return {"error": f"분석 또는 파싱 실패: {str(e)}", "raw_content": content if 'content' in locals() else None}


# 4. 메인 실행 예시
if __name__ == "__main__":
    print("✅ 통합 건강 비전 스크립트 준비 완료")

    # [테스트 1: 음식 성분 및 위험 경고 테스트]
    # 실제 테스트 시 이미지 경로와 약 이름을 수정하세요.
    food_image_path = "/Users/ganghyeon-u/Desktop/음식.png" 
    pill_i_take = "갑상선 호르몬제" # 예: 대두와 상호작용하는 약물
    
    if os.path.exists(food_image_path):
        print(f"\n🚀 음식 상호작용 분석 시작 (약물: {pill_i_take})...")
        result = analyze_health_image(food_image_path, mode="food", current_pill=pill_i_take)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    # [테스트 2: 병원 처방전 테스트]
    hospital_image_path = "/Users/ganghyeon-u/Desktop/처방전.png"
    if os.path.exists(hospital_image_path):
        print("\n🚀 병원 처방전 OCR 분석 시작...")
        result = analyze_health_image(hospital_image_path, mode="hospital_prescription")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # [테스트 3: 약봉투(약국) 테스트]
    pill_bag_image_path = "/Users/ganghyeon-u/Desktop/약봉투.png"  # 실제 파일명/확장자에 맞게 수정하세요

    if os.path.exists(pill_bag_image_path):
        print("\n🚀 약봉투 OCR 분석 시작...")
        # 약봉투 분석 모드는 'prescription' 입니다.
        result = analyze_health_image(pill_bag_image_path, mode="prescription")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n⚠️ 테스트 파일을 찾을 수 없습니다: {pill_bag_image_path}")
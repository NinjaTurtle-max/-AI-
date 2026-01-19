import google.generativeai as genai
import os
from dotenv import load_dotenv

# 환경 변수 로드 (독립 실행 시 안전장치)
load_dotenv()

def generate_ai_advice(drug_report, user_req):
    """
    drug_api.py에서 가져온 리포트와 사용자 프로필을 바탕으로
    Gemini가 약사처럼 맞춤형 조언을 생성합니다.
    """
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        return "⚠️ 서버 에러: GEMINI_API_KEY가 설정되지 않았습니다."

    genai.configure(api_key=GEMINI_API_KEY)

    # [모델 설정] img_vision.py와 동일하게 Fallback 로직 적용
    try:
        llm_model = genai.GenerativeModel('gemini-2.5-flash')
        # print("🤖 AI 약사 모델: gemini-2.5-flash")
    except:
        print("ℹ️ 2.5 로드 불가, 1.5-flash로 전환")
        llm_model = genai.GenerativeModel('gemini-1.5-flash')

    # 데이터 안전하게 가져오기
    basic = drug_report.get('basic', {}) or drug_report.get('basic_info', {})
    safety = drug_report.get('safety', {}) or drug_report.get('safety_check', {})
    
    # 약 이름
    drug_name = basic.get('itemName') or basic.get('item_name') or "이 약"

    # 사용자가 선택한 결과물만 담을 변수
    filtered_context = ""
    selected_options = getattr(user_req, 'options', [])

    # [수정] 데이터 처리 로직 개선
    for option in selected_options:
        if option == "효능":
            # API 키 이름이 다를 수 있으므로 여러 개 체크
            effect = basic.get("efcyQesitm") or basic.get("effect") or "식약처 효능 데이터 없음"
            filtered_context += f"[효능 정보]: {effect}\n"
            
        elif option == "복용방법":
            method = basic.get("useMethodQesitm") or basic.get("use_method") or "식약처 복용법 데이터 없음"
            filtered_context += f"[복용방법]: {method}\n"
            
        elif option == "금기사항":
            # [핵심 수정] drug_api.py는 이미 문자열 리스트를 반환함. 딕셔너리 접근 X
            safety_info = ""
            found_issues = False
            
            for category, items in safety.items():
                if items and isinstance(items, list):
                    # 리스트 안에 "특이사항 없음" 등의 텍스트가 있을 수 있음
                    valid_items = [item for item in items if "특이사항 없음" not in item and "조회 실패" not in item]
                    
                    if valid_items:
                        found_issues = True
                        # 너무 길면 3개까지만 요약
                        desc = ", ".join(valid_items[:3])
                        if len(valid_items) > 3: desc += " 등..."
                        safety_info += f"- {category}: {desc}\n"
            
            if not found_issues:
                safety_info = "특이한 금기사항이 발견되지 않았습니다."
            
            # 일반 주의사항
            atpn = basic.get("atpnQesitm") or "일반 주의사항 데이터 없음"
            filtered_context += f"[금기 및 주의사항 분석]:\n{safety_info}\n(참고: {atpn[:200]}...)\n"
            
        else:
            # 기타 토픽
            filtered_context += f"[{option}]: 관련 상세 데이터가 API에 명시되지 않았습니다.\n"

    # 사용자 프로필 안전 처리
    profile = getattr(user_req, 'user_profile', None)
    symptom = profile.symptom if profile else "정보 없음"
    age = profile.age if profile else "미상"
    
    # 최종 프롬프트 생성 (페르소나 강화)
    prompt = f"""
    당신은 친절하고 전문적인 'AI 약사'입니다. 
    아래 제공된 식약처 데이터를 바탕으로 환자에게 복약 지도를 해주세요.

    [환자 프로필]
    - 증상/상황: {symptom}
    - 연령: {age}세
    
    [약품 정보: {drug_name}]
    {filtered_context}

    [답변 가이드라인]
    1. 환자의 나이({age}세)와 증상({symptom})을 고려하여, 말투를 부드럽게 하세요. (예: "~~하셔야 해요", "~~는 조심해 주세요")
    2. 사용자가 선택한 질문({', '.join(selected_options)})에 대해서만 핵심적으로 답변하세요.
    3. 만약 [금기사항]에 내용이 있다면, 환자에게 위험할 수 있음을 정중하지만 명확하게 경고하세요.
    4. 너무 긴 전문 용어는 피하고 이해하기 쉽게 설명하세요.
    5. 답변은 한국어로 작성하세요.
    """
    
    try:
        response = llm_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"죄송합니다. AI 상담 생성 중 오류가 발생했습니다. ({str(e)})"
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
# 최종 프롬프트 생성 (상호작용 분석 강화)
    prompt = f"""
    당신은 20년 경력의 베테랑 'AI 약사'입니다. 
    제공된 식약처 데이터와 당신의 전문 지식을 결합하여 환자에게 복약 지도를 해주세요.

    [환자 프로필]
    - 연령: {age}세
    - 현재 증상: {symptom}
    - **현재 복용 중인 약물**: {current_meds} ✨ (중요: 이 약물들과의 상호작용을 반드시 체크하세요)
    
    [상담 대상 약품: {drug_name}]
    {filtered_context}

    [답변 가이드라인 - 필수 준수]
    1. **상호작용 우선 분석**: 제공된 데이터에 내용이 없더라도, 당신의 지식을 바탕으로 '{drug_name}'과 현재 복용 중인 '{current_meds}'을 함께 복용해도 안전한지 가장 먼저 설명하세요.
    2. **맞춤형 조언**: {age}세라는 연령과 {symptom}이라는 상황에 맞춰, 특히 주의해야 할 부작용이나 복용 팁을 친절하게 알려주세요.
    3. **분량 제한**: 핵심 위주로 **딱 3문장 이내**로 간결하게 답변하세요.
    4. 전문 용어 대신 환자가 이해하기 쉬운 비유나 쉬운 한국어를 사용하세요.
    """
    
    try:
        response = llm_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"죄송합니다. AI 상담 생성 중 오류가 발생했습니다. ({str(e)})"
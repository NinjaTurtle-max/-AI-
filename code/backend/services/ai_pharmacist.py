import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def generate_ai_advice(drug_report, user_req):
    """
    [최종 완성본] 요약문을 제거하고 상세 데이터를 사용하되,
    답변 결과물을 딱 3문장으로 강제하여 중복을 막고 가독성을 극대화합니다.
    """
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY: 
        return "⚠️ 서버 에러: API 키가 설정되지 않았습니다."

    genai.configure(api_key=GEMINI_API_KEY)
    
    # 모델 설정 (안정적인 1.5-flash 권장)
    try:
        llm_model = genai.GenerativeModel('gemini-2.5-flash')
    except:
        llm_model = genai.GenerativeModel('gemini-pro')

    basic = drug_report.get('basic_info', {})
    db_check = drug_report.get('db_interactions', {})
    drug_name = basic.get('item_name', '해당 약물')

    # 사용자가 선택한 주제에 맞는 데이터만 엄격하게 분리 (중복 방지)
    context_data = ""
    for option in user_req.options:
        if option == "효능":
            context_data += f"""
            [주제: 효능]
            - 식약처 원문: {basic.get('raw_effect')}
            - 기존 약물 상호작용(약효 변화): {", ".join(db_check.get('efficacy_conflicts')) if db_check.get('efficacy_conflicts') else "특이사항 없음"}
            """
        elif option == "복용방법":
            context_data += f"""
            [주제: 복용방법]
            - 식약처 원문: {basic.get('raw_usage')}
            - 기존 약물 상호작용(복용 간격): {", ".join(db_check.get('usage_conflicts')) if db_check.get('usage_conflicts') else "특이사항 없음"}
            """
        elif option == "금기사항":
            context_data += f"""
            [주제: 금기사항]
            - 식약처 원문: {basic.get('raw_caution')}
            - 기존 약물 상호작용(위험 경고): {", ".join(db_check.get('strict_warnings')) if db_check.get('strict_warnings') else "특이사항 없음"}
            """

    # ✨ 답변 형식을 완전히 통제하는 3대 규칙 프롬프트
    prompt = f"""
    당신은 20년 경력의 베테랑 약사입니다. 아래 데이터를 바탕으로 {user_req.user_profile.age}세 환자에게 상담을 진행하세요.

    상담 약물: {drug_name}
    데이터: {context_data}

    [상담 답변 규칙 - 필수 준수]
    1. **분량 제한**: 모든 답변은 주제별로 핵심만 뽑아 **반드시 딱 3문장**으로 작성하세요.
    2. **중복 금지**: 선택된 주제의 데이터만 사용하고, 다른 주제(예: 효능 답변에 금기 내용)는 절대 섞지 마세요.
    3. **상호작용 강조**: 현재 복용 중인 약과의 상호작용이 있다면 가장 먼저 언급하여 환자의 안전을 최우선으로 하세요.
    """
    
    try:
        response = llm_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"상담 생성 중 오류가 발생했습니다. ({str(e)})"
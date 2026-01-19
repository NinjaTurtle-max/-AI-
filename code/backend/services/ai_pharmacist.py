import google.generativeai as genai
import os

def generate_ai_advice(drug_report, user_req):
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        # 1) 개발 중이면 그냥 문자열로 반환 (프론트 연결 테스트용)
        return "⚠️ GEMINI_API_KEY가 설정되지 않아 AI 상담을 생성할 수 없습니다. .env에 GEMINI_API_KEY를 추가하세요."

    genai.configure(api_key=GEMINI_API_KEY)
    llm_model = genai.GenerativeModel('gemini-2.5-flash')

    basic = drug_report.get('basic') or {}
    safety = drug_report.get('safety') or {}
    
    # 사용자가 선택한 결과물만 담을 변수
    filtered_context = ""

    # 선택 항목에 따른 로직 분기 (if...elif...else)
    for option in user_req.options:
        if option == "효능":
            effect = basic.get("efcyQesitm", "정보 없음")
            filtered_context += f"[효능 정보]: {effect}\n"
            
        elif option == "복용방법":
            method = basic.get("useMethodQesitm", "정보 없음")
            filtered_context += f"[복용방법]: {method}\n"
            
        elif option == "금기사항":
            # 9가지 DUR 데이터를 요약하여 금기사항 섹션 구성
            safety_info = ""
            for category, items in safety.items():
                if items:
                    desc = [str(i.get('PROVISO', i.get('REMARK', '주의'))) for i in items[:1]]
                    safety_info += f"- {category}: {', '.join(desc)}\n"
            
            atpn = basic.get("atpnQesitm", "정보 없음") # 일반 주의사항 포함
            filtered_context += f"[금기 및 주의사항]:\n{safety_info}\n일반주의: {atpn}\n"
            
        else:
            filtered_context += f"[{option}]: 해당 항목에 대한 상세 데이터가 부족합니다.\n"

    # 최종 프롬프트 생성
    prompt = f"""
    당신은 전문 AI 약사입니다. 사용자가 요청한 특정 정보만을 바탕으로 상담하세요.
    
    [사용자 프로필]
    - 증상: {user_req.user_profile.symptom}
    - 연령: {user_req.user_profile.age}세
    
    [선택된 약품 정보: {basic.get('itemName', '미상')}]
    {filtered_context}

    [지시사항]
    1. 사용자가 선택한 '{', '.join(user_req.options)}' 항목에 대해서만 집중적으로 설명하세요.
    2. 선택하지 않은 정보는 언급을 최소화하세요.
    3. 금기사항이 포함된 경우 사용자의 연령과 증상을 고려해 위험 요소를 강조하세요.
    """
    
    response = llm_model.generate_content(prompt)
    return response.text
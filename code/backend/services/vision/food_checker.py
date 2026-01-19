import json
import google.generativeai as genai
import PIL.Image

def analyze_food_interaction(image_path, api_key, current_pill_name):
    """
    음식 사진을 분석하여 복용 중인 약과의 상호작용 경고
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    img = PIL.Image.open(image_path)

    prompt = f"""
    [영양 및 약물 상호작용 전문가]
    이 음식 사진을 분석하세요.
    현재 사용자가 복용 중인 약물: '{current_pill_name}'
    
    이 음식과 해당 약물이 같이 먹었을 때 위험한지 판단하세요.
    
    응답 형식: {{
        "food_name": "음식 이름",
        "ingredients": ["주요재료1", "주요재료2"],
        "interaction_warning": "주의사항 (없으면 '안전함')",
        "risk_level": "높음/중간/낮음/없음"
    }}
    """
    
    try:
        response = model.generate_content([prompt, img])
        content = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        return {"error": f"음식 분석 실패: {str(e)}"}
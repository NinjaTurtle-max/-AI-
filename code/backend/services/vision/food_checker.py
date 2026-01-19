import json
import google.generativeai as genai
import PIL.Image
import os
from urllib.parse import unquote  # [핵심] 키 디코딩을 위해 추가

def analyze_food_interaction(image_path, api_key, current_pill_name):
    """
    음식 사진을 분석하여 복용 중인 약과의 상호작용 경고 (Gemini Vision)
    """
    # 1. API 키 안전 처리 (인코딩된 키가 들어와도 디코딩하여 원본으로 변환)
    if not api_key:
        return {"error": "Gemini API 키가 없습니다."}
    
    decoded_key = unquote(api_key)
    genai.configure(api_key=decoded_key)

    # 2. 이미지 로드
    try:
        if not os.path.exists(image_path):
            return {"error": f"파일 없음: {image_path}"}
        img = PIL.Image.open(image_path)
    except Exception as e:
        return {"error": f"이미지 로드 실패: {e}"}

    # 3. 모델 로드
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        return {"error": f"모델 로드 실패: {e}"}

    # 4. 프롬프트 작성 (JSON 포맷 강제)
    prompt = f"""
    [영양 및 약물 상호작용 전문가]
    이 음식 사진을 분석하세요.
    현재 사용자가 복용 중인 약물: '{current_pill_name}'
    
    이 음식과 해당 약물이 같이 먹었을 때 위험한지 판단하세요.
    특히 고혈압약(자몽), 와파린(녹색채소), 항생제(유제품) 등의 잘 알려진 상호작용을 주의 깊게 보세요.
    
    응답 형식 (JSON):
    {{
        "food_name": "음식 이름 (예: 자몽 주스)",
        "ingredients": ["주요재료1", "주요재료2"],
        "interaction_warning": "주의사항 (상호작용이 없으면 '안전함'이라고 출력, 위험하면 구체적 이유)",
        "risk_level": "위험/주의/안전 중 1택"
    }}
    """
    
    # 5. 실행 및 결과 파싱
    try:
        response = model.generate_content([prompt, img])
        content = response.text.strip()

        # [디버깅] 원본 응답 확인 (필요시 주석 해제)
        # print(f"🐛 Food Raw Output: {content}")

        # JSON 클리닝 (Markdown 코드블록 제거)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        return json.loads(content)

    except json.JSONDecodeError:
        # AI가 JSON을 망가뜨렸을 때 방어 로직
        print(f"❌ JSON 파싱 실패. 원본: {content}")
        return {
            "food_name": "분석 실패",
            "interaction_warning": "AI 응답을 해석할 수 없습니다.",
            "risk_level": "알 수 없음"
        }
    except Exception as e:
        return {"error": f"음식 분석 중 에러: {str(e)}"}
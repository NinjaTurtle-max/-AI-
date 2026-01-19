import os
import requests
import json
import google.generativeai as genai
import PIL.Image

# 식약처 엔드포인트
PILL_IDENT_API_URL = "http://apis.data.go.kr/1471000/MdcinGrnIdntfcInfoService03/getMdcinGrnIdntfcInfoList03"

def _call_pill_api_logic(pill_features, service_key):
    """
    [내부 함수] 식약처 API 점진적 검색 (엄격 -> 느슨)
    """
    if not service_key:
        print("⚠️ 식약처 API 키 없음")
        return []

    search_strategies = []
    # 1. 전체 검색
    search_strategies.append({"desc": "1. 정밀 검색", "params": pill_features})
    
    # 2. 이름 제외 (식별문자 위주)
    if pill_features.get("item_name"):
        p = pill_features.copy()
        p["item_name"] = ""
        search_strategies.append({"desc": "2. 이름 제외 검색", "params": p})

    # 3. 앞뒤 교차
    f, b = pill_features.get("print_front", ""), pill_features.get("print_back", "")
    if f and b:
        p = pill_features.copy()
        p["item_name"], p["print_front"], p["print_back"] = "", b, f
        search_strategies.append({"desc": "3. 앞뒤 교차 검색", "params": p})

    # 4. 식별문자만
    if f or b:
        search_strategies.append({"desc": "4. 식별문자만 검색", "params": {"print_front": f, "print_back": b}})

    for strat in search_strategies:
        print(f"🔎 시도: {strat['desc']}")
        params = {
            'serviceKey': service_key, 'type': 'json', 'numOfRows': '10', 'pageNo': '1',
            'item_name': strat['params'].get('item_name', ''),
            'print_front': strat['params'].get('print_front', ''),
            'print_back': strat['params'].get('print_back', ''),
            'color_class1': strat['params'].get('color_class1', ''),
            'drug_shape': strat['params'].get('drug_shape', '')
        }
        params = {k: v for k, v in params.items() if v} # 빈 값 제거

        try:
            res = requests.get(PILL_IDENT_API_URL, params=params, timeout=5)
            if res.status_code == 200:
                items = res.json().get('body', {}).get('items', [])
                if items:
                    print(f"   ✅ {len(items)}건 발견!")
                    return items
        except Exception as e:
            print(f"   ⚠️ 에러: {e}")
            
    return []

def analyze_pill(image_path, api_key, service_key):
    """
    [Main] 알약 이미지 분석 및 DB 검색
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    img = PIL.Image.open(image_path)

    prompt = """
    [알약 식별 전문가]
    이 사진 속 '알약'의 특징을 식약처 DB 검색용 JSON으로 추출해.
    배경, 채팅창, 손가락 등은 무시하고 오직 알약에 집중해.
    
    응답 형식:
    {
        "debug_thought": "분석 근거",
        "item_name": "약 이름(확실할때만)", 
        "print_front": "앞면 글자", 
        "print_back": "뒷면 글자", 
        "color_class1": "색상(표준)", 
        "drug_shape": "모양(표준)"
    }
    """
    
    try:
        response = model.generate_content([prompt, img])
        content = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(content)
        
        # API 호출 연결
        candidates = _call_pill_api_logic(result, service_key)
        
        return {
            "mode": "pill_id",
            "detected_features": result,
            "candidates": candidates,
            "total_found": len(candidates)
        }
    except Exception as e:
        return {"error": f"알약 분석 실패: {str(e)}"}
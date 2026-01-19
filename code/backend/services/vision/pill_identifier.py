import os
import requests
import json
import google.generativeai as genai
import PIL.Image
from urllib.parse import unquote  # [핵심] 키 디코딩용

# 식약처 엔드포인트
PILL_IDENT_API_URL = "http://apis.data.go.kr/1471000/MdcinGrnIdntfcInfoService03/getMdcinGrnIdntfcInfoList03"

def _call_pill_api_logic(pill_features, service_key):
    """
    [내부 함수] 식약처 API 점진적 검색 (엄격 -> 느슨)
    """
    if not service_key:
        print("⚠️ 식약처 API 키 없음")
        return []

    # [핵심 수정] Encoding Key가 들어와도 안전하게 디코딩 처리
    decoded_service_key = unquote(service_key)

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
        
        # [핵심 수정] params 딕셔너리에 serviceKey를 직접 포함
        params = {
            'serviceKey': decoded_service_key,  # 디코딩된 키 사용
            'type': 'json', 
            'numOfRows': '10', 
            'pageNo': '1',
            'item_name': strat['params'].get('item_name', ''),
            'print_front': strat['params'].get('print_front', ''),
            'print_back': strat['params'].get('print_back', ''),
            'color_class1': strat['params'].get('color_class1', ''),
            'drug_shape': strat['params'].get('drug_shape', '')
        }
        params = {k: v for k, v in params.items() if v} # 빈 값 제거

        try:
            # requests가 params를 인코딩해주므로, 여기선 순수 디코딩 키를 넘겨야 함
            res = requests.get(PILL_IDENT_API_URL, params=params, timeout=5)
            
            if res.status_code == 200:
                try:
                    data = res.json()
                    items = data.get('body', {}).get('items', [])
                    if items:
                        print(f"   ✅ {len(items)}건 발견!")
                        return items
                    else:
                        print("   ❌ 결과 없음")
                except json.JSONDecodeError:
                    # 키가 틀리거나 인증 에러 시 XML이 반환되어 JSON 파싱 에러 발생 가능
                    print("   ⚠️ 응답 파싱 실패 (XML 에러 가능성 - 키 확인 필요)")
            else:
                print(f"   ⚠️ API 상태 코드 에러: {res.status_code}")
                
        except Exception as e:
            print(f"   ⚠️ 연결 실패: {e}")
            
    return []

def analyze_pill(image_path, api_key, service_key):
    """
    [Main] 알약 이미지 분석 및 DB 검색
    """
    # Gemini API 키도 안전하게 디코딩 적용
    if not api_key:
        return {"error": "Gemini API 키 없음"}
        
    genai.configure(api_key=unquote(api_key))
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        img = PIL.Image.open(image_path)
    except Exception as e:
        return {"error": f"모델/이미지 로드 실패: {str(e)}"}

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
        content = response.text.strip()
        
        # JSON 클리닝 (Markdown 코드블록 제거)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        result = json.loads(content)
        
        # 식약처 API 호출 연결
        candidates = _call_pill_api_logic(result, service_key)
        
        return {
            "mode": "pill_id",
            "detected_features": result,
            "candidates": candidates,
            "total_found": len(candidates)
        }
    except json.JSONDecodeError:
        return {"error": f"AI 응답 파싱 실패: {content}"}
    except Exception as e:
        return {"error": f"알약 분석 실패: {str(e)}"}
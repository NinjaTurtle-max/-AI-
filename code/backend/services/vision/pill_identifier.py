import os
import requests
import json
import google.generativeai as genai
import PIL.Image
from urllib.parse import quote, unquote

# 식약처 의약품 낱알식별 정보 엔드포인트
PILL_IDENT_API_URL = "http://apis.data.go.kr/1471000/MdcinGrnIdntfcInfoService03/getMdcinGrnIdntfcInfoList03"

def _call_pill_api_logic(pill_features, service_key):
    """
    [내부 함수] 식약처 API 점진적 검색 (URL 수동 조립 및 강제 전송)
    이유: requests 라이브러리의 자동 인코딩이 식약처 API 키와 충돌하는 문제를 방지하기 위함.
    """
    if not service_key:
        print("⚠️ 식약처 API 키 없음")
        return []

    # 1. API 키 안전 처리
    # 어떤 형태(Encoding/Decoding)의 키가 들어와도 일단 원본(Decoding) 상태로 만듦
    raw_service_key = unquote(service_key) 
    
    # 우리가 직접 URL에 넣을 것이므로 안전하게 인코딩 (특수문자 처리)
    safe_key = quote(raw_service_key, safe='') 

    # 2. 검색 전략 수립
    search_strategies = []

    # 전략 A: AI가 추출한 모든 정보 사용 (이름 포함)
    search_strategies.append({"desc": "1. 정밀 검색 (전체 일치)", "params": pill_features})
    
    # 전략 B: 약 이름은 무시하고 '식별 문자' 위주 검색 (가장 강력함)
    p_text = pill_features.copy()
    p_text["item_name"] = "" 
    if p_text.get("print_front") or p_text.get("print_back"):
        search_strategies.append({"desc": "2. 식별문자 우선 검색 (이름 무시)", "params": p_text})

    # 전략 C: 식별 문자 앞/뒤 교차 검색
    f, b = pill_features.get("print_front", ""), pill_features.get("print_back", "")
    if f and b:
        p_swap = pill_features.copy()
        p_swap["item_name"] = ""
        p_swap["print_front"], p_swap["print_back"] = b, f
        search_strategies.append({"desc": "3. 앞뒤 교차 검색", "params": p_swap})
        
    # 전략 D: 식별 문자가 없을 때 모양/색상으로만 검색
    if not f and not b:
        p_shape = {
            "color_class1": pill_features.get("color_class1"),
            "drug_shape": pill_features.get("drug_shape"),
            "item_name": ""
        }
        if p_shape["color_class1"] or p_shape["drug_shape"]:
            search_strategies.append({"desc": "4. 모양/색상 검색 (식별문자 없음)", "params": p_shape})

    # 3. 전략 실행 Loop
    for strat in search_strategies:
        print(f"🔎 [API 요청] {strat['desc']}")
        
        # --- [핵심] URL 수동 조립 (requests 간섭 차단) ---
        query_parts = []
        params = strat['params']
        
        if params.get('item_name'):
            query_parts.append(f"item_name={quote(params['item_name'])}")
        if params.get('print_front'):
            query_parts.append(f"print_front={quote(params['print_front'])}")
        if params.get('print_back'):
            query_parts.append(f"print_back={quote(params['print_back'])}")
        if params.get('color_class1'):
            query_parts.append(f"color_class1={quote(params['color_class1'])}")
        if params.get('drug_shape'):
            query_parts.append(f"drug_shape={quote(params['drug_shape'])}")

        # 검색 조건이 하나도 없으면 스킵
        if not query_parts:
            continue

        query_string = "&".join(query_parts)
        final_url = f"{PILL_IDENT_API_URL}?serviceKey={safe_key}&type=json&numOfRows=10&pageNo=1&{query_string}"
        
        # [디버깅용] 생성된 URL 확인
        # print(f"🔗 URL: {final_url}")

        try:
            # Session + PreparedRequest 사용으로 URL 변조 방지
            session = requests.Session()
            req = requests.Request('GET', final_url)
            prepped = session.prepare_request(req)
            prepped.url = final_url # URL 강제 덮어쓰기
            
            res = session.send(prepped, timeout=10)
            
            if res.status_code == 200:
                try:
                    data = res.json()
                    items = data.get('body', {}).get('items', [])
                    
                    if items:
                        print(f"   ✅ {len(items)}건 발견! (성공)")
                        return items
                    else:
                        print("   ❌ 결과 0건")
                except json.JSONDecodeError:
                    print("   ⚠️ 응답 파싱 실패 (API 키 에러 또는 XML 반환됨)")
            else:
                print(f"   ⚠️ API 상태 코드 에러: {res.status_code}")
                
        except Exception as e:
            print(f"   ⚠️ 연결 실패: {e}")

    print("🏁 모든 검색 전략 실패")
    return []

def analyze_pill(image_path, api_key, service_key):
    """
    [Main] 알약 이미지 분석 및 DB 검색
    """
    if not api_key: return {"error": "Gemini API 키 없음"}
    
    # Gemini 키 안전하게 디코딩
    genai.configure(api_key=unquote(api_key))
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        img = PIL.Image.open(image_path)
    except Exception as e:
        return {"error": f"이미지/모델 로드 실패: {str(e)}"}

    prompt = """
    [알약 식별 전문가]
    이 사진 속 알약의 특징(글자, 색상, 모양)을 JSON으로 추출해.
    
    1. print_front/back: 알약 표면의 글자(알파벳, 숫자)를 있는 그대로 읽어라. (매우 중요)
    2. item_name: 약 봉투에 이름이 없으면 추측하지 말고 빈칸("").
    3. 색상/모양: 식약처 표준 용어 사용 (하양, 노랑 / 원형, 타원형, 장방형 등).
    
    응답 형식:
    {
        "debug_thought": "식별 근거",
        "item_name": "", 
        "print_front": "", 
        "print_back": "", 
        "color_class1": "", 
        "drug_shape": ""
    }
    """
    
    try:
        response = model.generate_content([prompt, img])
        content = response.text.strip()
        
        # JSON 클리닝
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        result = json.loads(content)
        
        # 식약처 API 호출 (강제 URL 전송 방식 적용)
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
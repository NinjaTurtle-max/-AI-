import requests
import os
import json
from dotenv import load_dotenv

# config.py에서 URL 상수들 가져오기
from config import * # 1. 환경 변수 로드 (단독 실행 시 필요)
load_dotenv()

# .env의 KEY_E_DRUG는 'Decoding Key'여야 requests가 알아서 인코딩합니다.
DATA_GO_KR_KEY = os.getenv("KEY_E_DRUG")
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "False").lower() == "true"

# =========================================================
# 2. 약품 검색 함수 (이름 -> 코드/상세 변환)
# =========================================================
def search_drug_by_name(drug_name):
    """
    약품명으로 검색하여 itemSeq(품목기준코드) 및 기본 정보를 반환합니다.
    """
    if USE_MOCK_DATA:
        return {
            "item_seq": "123456789", 
            "item_name": drug_name,
            "entp_name": "테스트제약",
            "item_image": None
        }
    
    if not DATA_GO_KR_KEY:
        print("❌ [API] 식약처 키(KEY_E_DRUG)가 없습니다.")
        return None

    # e약은요 서비스 호출 (기본 정보 조회용)
    params = {
        "serviceKey": DATA_GO_KR_KEY,
        "type": "json",
        "pageNo": "1",
        "numOfRows": "5",
        "itemName": drug_name.strip()
    }
    
    try:
        res = requests.get(URL_DRUG_INFO, params=params, timeout=5)
        
        if res.status_code == 200:
            try:
                data = res.json()
                items = data.get('body', {}).get('items', [])
                
                if items:
                    first = items[0]
                    # 프론트엔드 표시에 필요한 정보들을 같이 추출
                    result = {
                        "item_seq": first.get("itemSeq"),
                        "item_name": first.get("itemName"),
                        "entp_name": first.get("entpName"),   # 제조사
                        "item_image": first.get("itemImage"), # 약 이미지 URL
                        "effect": first.get("efcyQesitm"),    # 효능 (간략)
                        "use_method": first.get("useMethodQesitm") # 용법 (간략)
                    }
                    return result
            except json.JSONDecodeError:
                print("⚠️ [API] 검색 응답이 JSON이 아닙니다. (XML 에러 가능성)")
    except Exception as e:
        print(f"❌ [API] 약품 검색 실패: {e}")
    
    return None

# =========================================================
# 3. 종합 안전 리포트 생성 함수 (DUR 전체 스캔)
# =========================================================
def get_full_drug_report(item_seq, item_name):
    """
    제공된 DUR API 엔드포인트들을 모두 호출하여 안전성 리포트를 생성합니다.
    """
    if USE_MOCK_DATA:
        return {"basic": {"item_name": item_name}, "safety": {}}

    print(f"📑 [DUR] '{item_name}' 안전성 정보 조회 시작...")

    report = {
        "basic": {"item_name": item_name, "item_seq": item_seq},
        "safety": {} # 병용금기, 임부금기 등 결과 저장
    }
    
    # 공통 파라미터
    default_params = {
        "serviceKey": DATA_GO_KR_KEY, 
        "type": "json", 
        "pageNo": "1", 
        "numOfRows": "10"
    }
    item_seq_str = str(item_seq).strip()

    # config.py에 정의된 DUR URL 매핑
    dur_apis = {
        "병용금기": URL_DUR_MIXTURE,
        "임부금기": URL_DUR_PREGNANT,
        "연령대금기": URL_DUR_AGE,
        "노인주의": URL_DUR_ELDERLY,
        "용량주의": URL_DUR_CAPACITY,
        "투여기간주의": URL_DUR_PERIOD,
        "효능군중복": URL_DUR_EFFICACY,
        "서방정분할주의": URL_DUR_SPLIT
    }

    # 1. DUR API 순회
    for title, url in dur_apis.items():
        try:
            params = default_params.copy()
            
            # [중요] 병용금기는 약 이름으로 검색해야 정확도가 높을 때가 있음
            if title == "병용금기":
                params["itemName"] = item_name
            else:
                params["itemSeq"] = item_seq_str
                
            res = requests.get(url, params=params, timeout=3)
            
            if res.status_code == 200:
                try:
                    data = res.json()
                    items = data.get('body', {}).get('items', [])
                    
                    if items:
                        # 데이터가 있으면 내용을 리스트로 저장
                        extracted = []
                        for item in items:
                            # API마다 주의사항 필드명이 다를 수 있어 여러 개 확인
                            content = (
                                item.get('PROHBT_CONTENT') or 
                                item.get('NOTE_ETC') or 
                                item.get('INGR_NAME') or 
                                "주의사항 있음"
                            )
                            # 병용금기일 경우 상대 약물 이름 포함
                            if title == "병용금기":
                                mix_name = item.get('MIXTURE_ITEM_NAME', '')
                                if mix_name:
                                    content = f"[{mix_name}]와 함께 복용 금지: {content}"
                            
                            extracted.append(content)
                        report['safety'][title] = extracted
                    else:
                        report['safety'][title] = [] # 특이사항 없음
                except json.JSONDecodeError:
                     report['safety'][title] = ["데이터 처리 오류"]
            else:
                report['safety'][title] = ["조회 실패"]
        except Exception:
            report['safety'][title] = ["연결 에러"]

    print("✅ [DUR] 리포트 생성 완료")
    return report
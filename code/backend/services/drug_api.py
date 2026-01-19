import requests
import os
import json
from dotenv import load_dotenv

# config.py 및 database.py 임포트
from config import *
from database import get_user_drug_list

load_dotenv()

DATA_GO_KR_KEY = os.getenv("KEY_E_DRUG")
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "False").lower() == "true"

def search_drug_by_name(drug_name):
    """약품명으로 검색하여 기본 정보를 반환합니다."""
    if USE_MOCK_DATA:
        return {"item_seq": "123456789", "item_name": drug_name, "entp_name": "테스트제약"}
    
    params = {
        "serviceKey": DATA_GO_KR_KEY,
        "type": "json",
        "pageNo": "1",
        "numOfRows": "5",
        "itemName": drug_name.strip()
    }
    try:
        # 1차 검색: 원본 이름 그대로
        res = requests.get(URL_DRUG_INFO, params=params, timeout=5)
        if res.status_code == 200:
            items = res.json().get('body', {}).get('items', [])
            if items:
                first = items[0]
                return {
                    "item_seq": first.get("itemSeq"),
                    "item_name": first.get("itemName"),
                    "entp_name": first.get("entpName"),
                    "item_image": first.get("itemImage"),
                    "effect": first.get("efcyQesitm"),
                    "use_method": first.get("useMethodQesitm")
                }
    except: return None
            try:
                data = res.json()
                items = data.get('body', {}).get('items', [])
                
                if items:
                    return _parse_drug_item(items[0])
                
                # 2차 검색: 괄호 및 성분명 제거 후 재검색
                # 예: "인데놀정10mg(프로프라놀롤염산염)" -> "인데놀정10mg"
                import re
                cleaned_name = re.sub(r'\(.*?\)', '', drug_name).strip()
                
                if cleaned_name != drug_name:
                    print(f"⚠️ [API] 원본 검색 실패. '{cleaned_name}'으(로) 재검색 시도...")
                    params["itemName"] = cleaned_name
                    res = requests.get(URL_DRUG_INFO, params=params, timeout=5)
                    
                    if res.status_code == 200:
                         data = res.json()
                         items = data.get('body', {}).get('items', [])
                         if items:
                             return _parse_drug_item(items[0])

            except json.JSONDecodeError:
                print("⚠️ [API] 검색 응답이 JSON이 아닙니다. (XML 에러 가능성)")
    except Exception as e:
        print(f"❌ [API] 약품 검색 실패: {e}")
    
    return None

def get_full_drug_report(item_seq, item_name, user_id="test_user"):
    """
    요약문 기능을 제거하고, AI가 직접 분석할 수 있도록 
    상세 원문 데이터와 DB 상호작용 결과를 구조화하여 반환합니다.
    """
    user_drugs = get_user_drug_list(user_id)
def _parse_drug_item(item):
    """API 응답 아이템 파싱 헬퍼"""
    return {
        "item_seq": item.get("itemSeq"),
        "item_name": item.get("itemName"),
        "entp_name": item.get("entpName"),   # 제조사
        "item_image": item.get("itemImage"), # 약 이미지 URL
        "effect": item.get("efcyQesitm"),    # 효능 (간략)
        "use_method": item.get("useMethodQesitm") # 용법 (간략)
    }

# =========================================================
# 3. 종합 안전 리포트 생성 함수 (DUR 전체 스캔)
# =========================================================
def get_full_drug_report(item_seq, item_name):
    """
    제공된 DUR API 엔드포인트들을 모두 호출하여 안전성 리포트를 생성합니다.
    """
    if USE_MOCK_DATA:
        return {"basic": {"item_name": item_name}, "safety": {}, "summary": {}}

    print(f"📑 [DUR] '{item_name}' 안전성 정보 조회 시작...")

    report = {
        "basic": {"item_name": item_name, "item_seq": item_seq},
        "safety": {}, # 병용금기, 임부금기 등 결과 저장
        "summary": {} # [신규] 요약 정보 저장
    }
    
    # 공통 파라미터
    default_params = {
        "serviceKey": DATA_GO_KR_KEY, 
        "type": "json", 
        "pageNo": "1", 
        "numOfRows": "10"
    }
    item_seq_str = str(item_seq).strip()

    # AI에게 전달할 가공되지 않은 상세 리포트 구조
    report = {
        "basic_info": {
            "item_name": item_name,
            "item_seq": item_seq,
            "raw_effect": "",      # 식약처 효능 원문
            "raw_usage": "",       # 식약처 용법 원문
            "raw_caution": ""      # 식약처 주의사항 원문
        },
        "db_interactions": {
            "efficacy_conflicts": [], # DB 약물과 효능 관련 충돌
            "usage_conflicts": [],    # DB 약물과 복용시간 관련 충돌
            "strict_warnings": []     # DB 약물과 절대 금기 사항
        }
    }
    
    default_params = {"serviceKey": DATA_GO_KR_KEY, "type": "json", "pageNo": "1", "numOfRows": "10"}

    # 1. 상세 원문 데이터 수집
    try:
        res = requests.get(URL_DRUG_INFO, params={**default_params, "itemSeq": item_seq_str}, timeout=3)
        if res.status_code == 200:
            item = res.json().get('body', {}).get('items', [])[0]
            report["basic_info"]["raw_effect"] = item.get("efcyQesitm", "데이터 없음")
            report["basic_info"]["raw_usage"] = item.get("useMethodQesitm", "데이터 없음")
            report["basic_info"]["raw_caution"] = item.get("atpnQesitm", "데이터 없음")
    except: pass

    # 2. DUR API 기반 DB 약물 대조 분석
    try:
        # 병용금기 API 호출
        params = {**default_params, "itemName": item_name}
        res = requests.get(URL_DUR_MIXTURE, params=params, timeout=3)
        if res.status_code == 200:
            items = res.json().get('body', {}).get('items', [])
            for item in items:
                mixture_name = item.get('MIXTURE_ITEM_NAME', '')
                content = item.get('PROHBT_CONTENT') or ""
                
                for my_drug in user_drugs:
                    if my_drug in mixture_name or mixture_name in my_drug:
                        # 키워드에 따라 AI용 데이터 분류
                        if any(w in content for w in ["저하", "감소", "변화", "약효"]):
                            report["db_interactions"]["efficacy_conflicts"].append(f"[{my_drug}] 관련: {content}")
                        if any(w in content for w in ["간격", "시간", "조절"]):
                            report["db_interactions"]["usage_conflicts"].append(f"[{my_drug}] 관련: {content}")
                        if any(w in content for w in ["금기", "위험", "부작용"]):
                            report["db_interactions"]["strict_warnings"].append(f"⚠️ [{my_drug}]와 금기 사유: {content}")
    except: pass

    return report
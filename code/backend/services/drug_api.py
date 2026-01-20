import requests
import os
import json
import traceback
from dotenv import load_dotenv

# config.py 및 database.py 임포트
from config import *
from database import get_user_drug_list

load_dotenv()

DATA_GO_KR_KEY = os.getenv("KEY_E_DRUG")
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "False").lower() == "true"

# =========================================================
# 1. 약품 검색 함수 (디버깅 로그 추가)
# =========================================================
def search_drug_by_name(drug_name):
    """약품명으로 검색하여 기본 정보를 반환합니다."""
    if USE_MOCK_DATA:
        print("💡 [DEBUG] Mock Data 모드 사용 중")
        return {"item_seq": "123456789", "item_name": drug_name, "entp_name": "테스트제약"}
    
    if not DATA_GO_KR_KEY:
        print("❌ [DEBUG] 식약처 API 키(KEY_E_DRUG)가 없습니다.")
        return None

    # [핵심] 괄호 제거 로직 추가: 검색 성공률 대폭 상승
    clean_name = drug_name.split('(')[0].strip()
    print(f"\n🔍 [DEBUG] 약품 검색 시작: '{drug_name}' -> 정제: '{clean_name}'")

    params = {
        "serviceKey": DATA_GO_KR_KEY,
        "type": "json",
        "pageNo": "1",
        "numOfRows": "5",
        "itemName": clean_name
    }
    
    try:
        print(f"📡 [DEBUG] API 요청 주소: {URL_DRUG_INFO}")
        res = requests.get(URL_DRUG_INFO, params=params, timeout=5)
        
        print(f"📊 [DEBUG] API 응답 코드: {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            items = data.get('body', {}).get('items', [])
            
            if items:
                first = items[0]
                print(f"✅ [DEBUG] 검색 성공: {first.get('itemName')} ({first.get('itemSeq')})")
                return {
                    "item_seq": first.get("itemSeq"),
                    "item_name": first.get("itemName"),
                    "entp_name": first.get("entpName"),
                    "item_image": first.get("itemImage"),
                    "effect": first.get("efcyQesitm"),
                    "use_method": first.get("useMethodQesitm")
                }
            else:
                print(f"⚠️ [DEBUG] '{clean_name}'에 대한 검색 결과가 식약처 DB에 없습니다.")
    except Exception as e:
        print(f"❌ [DEBUG] 검색 중 오류 발생: {str(e)}")
        print(traceback.format_exc())
        
    return None

# =========================================================
# 2. 종합 안전 리포트 생성 함수 (DUR 상세 분석)
# =========================================================
def get_full_drug_report(item_seq, item_name, user_id="test_user"):
    """
    상세 원문 데이터와 DB 상호작용 결과를 구조화하여 반환합니다.
    """
    user_drugs = get_user_drug_list(user_id)
    item_seq_str = str(item_seq).strip()
    
    print(f"📑 [DEBUG] DUR 분석 시작: {item_name} (비교 대상 약물: {user_drugs})")

    report = {
        "basic_info": {
            "item_name": item_name,
            "item_seq": item_seq,
            "raw_effect": "데이터 없음",      
            "raw_usage": "데이터 없음",       
            "raw_caution": "데이터 없음"      
        },
        "db_interactions": {
            "efficacy_conflicts": [], 
            "usage_conflicts": [],    
            "strict_warnings": []     
        }
    }
    
    default_params = {"serviceKey": DATA_GO_KR_KEY, "type": "json", "pageNo": "1", "numOfRows": "10"}

    # 1. 상세 원문 데이터 수집
    try:
        res = requests.get(URL_DRUG_INFO, params={**default_params, "itemSeq": item_seq_str}, timeout=3)
        if res.status_code == 200:
            body = res.json().get('body', {})
            if body and body.get('items'):
                item = body.get('items')[0]
                report["basic_info"]["raw_effect"] = item.get("efcyQesitm") or "정보 없음"
                report["basic_info"]["raw_usage"] = item.get("useMethodQesitm") or "정보 없음"
                report["basic_info"]["raw_caution"] = item.get("atpnQesitm") or "정보 없음"
    except Exception as e:
        print(f"⚠️ [DEBUG] 상세 정보 로드 실패: {e}")

    # 2. DUR API 기반 DB 약물 대조 분석
    try:
        params = {**default_params, "itemName": item_name}
        res = requests.get(URL_DUR_MIXTURE, params=params, timeout=3)
        
        if res.status_code == 200:
            items = res.json().get('body', {}).get('items', [])
            print(f"🔗 [DEBUG] 병용금기 데이터 {len(items)}건 확인 중...")
            
            for item in items:
                mixture_name = item.get('MIXTURE_ITEM_NAME', '')
                content = item.get('PROHBT_CONTENT') or ""
                
                for my_drug in user_drugs:
                    # DB에 있는 약 이름이 금기 리스트에 포함되어 있는지 체크
                    if my_drug and (my_drug in mixture_name or mixture_name in my_drug):
                        print(f"🚨 [DEBUG] 충돌 발견! ({my_drug} <-> {mixture_name})")
                        if any(w in content for w in ["저하", "감소", "변화", "약효"]):
                            report["db_interactions"]["efficacy_conflicts"].append(f"[{my_drug}] 관련: {content}")
                        if any(w in content for w in ["간격", "시간", "조절"]):
                            report["db_interactions"]["usage_conflicts"].append(f"[{my_drug}] 관련: {content}")
                        if any(w in content for w in ["금기", "위험", "부작용"]):
                            report["db_interactions"]["strict_warnings"].append(f"⚠️ [{my_drug}]와 금기 사유: {content}")
    except Exception as e:
        print(f"⚠️ [DEBUG] DUR 분석 중 오류: {e}")

    print(f"✅ [DEBUG] 리포트 생성 완료")
    return report
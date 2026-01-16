import requests
import os
from config import * # URL 변수들이 config에 저장되어 있다고 가정

# 환경 변수 로드
DATA_GO_KR_KEY = os.getenv("KEY_E_DRUG") or os.getenv("DATA_GO_KR_KEY")
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "True").lower() == "true"

def get_full_drug_report(item_seq, item_name):
    """
    제공된 모든 DUR API 엔드포인트를 호출하여 종합적인 약품 안전 리포트를 생성합니다.
    """
    if USE_MOCK_DATA:
        return {
            "basic": {"itemName": item_name, "efcyQesitm": "테스트 효능"},
            "safety": {"병용금기": [], "노인주의": [], "연령대금기": [], "용량주의": [], "투여기간주의": [], "효능군중복": [], "임부금기": [], "분할주의": []}
        }

    report = {
        "basic": None,
        "safety": {}
    }
    
    # 공통 파라미터
    default_params = {"serviceKey": DATA_GO_KR_KEY, "type": "json", "pageNo": 1, "numOfRows": 10}
    item_seq_str = str(item_seq).strip()

    # 호출할 API 목록 정의 (이름: 엔드포인트URL)
    # config.py에 해당 URL들이 정의되어 있어야 합니다.
    dur_apis = {
        "병용금기": URL_DUR_MIXTURE,       # /getUsjntTabooInfoList03
        "노인주의": URL_DUR_ELDERLY,      # /getOdsnAtentInfoList03
        "연령대금기": URL_DUR_AGE,        # /getSpcifyAgrdeTabooInfoList03
        "용량주의": URL_DUR_CAPACITY,     # /getCpctyAtentInfoList03
        "투여기간주의": URL_DUR_PERIOD,   # /getMdctnPdAtentInfoList03
        "효능군중복": URL_DUR_DUPLICATE,  # /getEfcyDplctInfoList03
        "임부금기": URL_DUR_PREGNANT,     # /getPwnmTabooInfoList03
        "분할주의": URL_DUR_PARTITION     # /getSeobangjeongPartitnAtentInfoList03
    }

    # 1. 기본 정보 호출 (e약은요)
    try:
        res = requests.get(URL_DRUG_INFO, params={**default_params, "itemSeq": item_seq_str}, timeout=5)
        if res.status_code == 200:
            items = res.json().get('body', {}).get('items', [])
            if items: report['basic'] = items[0]
    except: pass

    # 2. 모든 DUR 정보 순회하며 호출
    for title, url in dur_apis.items():
        try:
            # 병용금기는 제품명(itemName)으로 검색하는 것이 더 정확할 때가 많음
            params = default_params.copy()
            if title == "병용금기":
                params["itemName"] = item_name
            else:
                params["itemSeq"] = item_seq_str
                
            res = requests.get(url, params=params, timeout=3)
            if res.status_code == 200:
                report['safety'][title] = res.json().get('body', {}).get('items', [])
            else:
                report['safety'][title] = []
        except:
            report['safety'][title] = []

    return report
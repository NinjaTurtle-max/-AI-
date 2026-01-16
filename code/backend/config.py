# config.py
# API 기본 주소 및 엔드포인트 모음 (전부 최신 03 버전)

# =========================================================
# 1. 의약품 개요 정보 (e약은요) - [필수]
# =========================================================
# 약품명, 효능, 복용법, 주의사항 텍스트 조회
URL_DRUG_INFO = "https://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"

# =========================================================
# 2. DUR 품목 정보 (안전성 점검) - [핵심 안전 기능]
# =========================================================
# * 팁: 품목코드(itemSeq)로 조회하면 해당 약의 성분을 분석해 금기사항을 알려줍니다.

# 병용금기 (같이 먹으면 안 되는 약)
URL_DUR_MIXTURE = "https://apis.data.go.kr/1471000/DURPrdlstInfoService03/getUsjntTabooInfoList03"

# 임부금기 (임산부 복용 금지 성분 포함 여부)
URL_DUR_PREGNANT = "https://apis.data.go.kr/1471000/DURPrdlstInfoService03/getPwnmTabooInfoList03"

# 특정연령대금기 (특정 나이 복용 금지 성분 포함 여부)
URL_DUR_AGE = "https://apis.data.go.kr/1471000/DURPrdlstInfoService03/getSpcifyAgrdeTabooInfoList03"

# 노인주의 (노인 복용 시 주의 성분)
URL_DUR_ELDERLY = "https://apis.data.go.kr/1471000/DURPrdlstInfoService03/getOdsnAtentInfoList03"

# =========================================================
# 3. DUR 기타 주의 정보 (필요시 사용)
# =========================================================
# 용량주의 (1일 최대 용량 초과 주의)
URL_DUR_CAPACITY = "https://apis.data.go.kr/1471000/DURPrdlstInfoService03/getCpctyAtentInfoList03"

# 투여기간주의 (최대 투여 기간 초과 주의)
URL_DUR_PERIOD = "https://apis.data.go.kr/1471000/DURPrdlstInfoService03/getMdctnPdAtentInfoList03"

# 효능군중복 (동일 효능 약 중복 복용 주의)
URL_DUR_EFFICACY = "https://apis.data.go.kr/1471000/DURPrdlstInfoService03/getEfcyDplctInfoList03"

# 서방정분할주의 (쪼개 먹으면 안 되는 약)
URL_DUR_SPLIT = "https://apis.data.go.kr/1471000/DURPrdlstInfoService03/getSeobangjeongPartitnAtentInfoList03"

# drug_api.py 호환용 별칭
URL_DUR_DUPLICATE = URL_DUR_EFFICACY     # 효능군중복
URL_DUR_PARTITION = URL_DUR_SPLIT        # 서방정분할주의
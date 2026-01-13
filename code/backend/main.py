import os
import json
import requests
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# config.py에서 모든 URL 변수 (URL_DRUG_INFO, URL_DUR_MIXTURE 등)를 가져옵니다.
from config import *

# =========================================================
# 1. 환경 변수 및 설정 로드
# =========================================================
load_dotenv()

# API 키 로드 (테스트 코드에서 성공한 KEY_E_DRUG를 우선 참조)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATA_GO_KR_KEY = os.getenv("KEY_E_DRUG") or os.getenv("DATA_GO_KR_KEY")

# 테스트 모드 설정 (실시간 데이터를 보려면 .env에서 False로 설정해야 합니다)
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "True").lower() == "true"

# Gemini 설정
genai.configure(api_key=GEMINI_API_KEY)
llm_model = genai.GenerativeModel('gemini-2.5-flash')

# FastAPI 앱 초기화
app = FastAPI(
    title="AI 약사 상담 서비스",
    description="이미지 식별 결과와 공공데이터를 결합해 AI 약사 상담 서비스를 제공합니다.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 모든 곳에서 오는 요청을 허용
    allow_credentials=True,
    allow_methods=["*"],      # GET, POST 등 모든 방식 허용
    allow_headers=["*"],      # 모든 헤더 허용
)

# =========================================================
# 2. 데이터 모델 정의
# =========================================================
class UserProfile(BaseModel):
    symptom: str
    age: int
    condition: str

class ConsultationRequest(BaseModel):
    class_id: int
    user_profile: UserProfile
    options: list[str]

# =========================================================
# 3. 매핑 파일 로드
# =========================================================
MAPPING_FILE = "drug_mapping.json"
YOLO_LABEL_MAP = {}

if os.path.exists(MAPPING_FILE):
    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        YOLO_LABEL_MAP = json.load(f)
    print(f"✅ 매핑 파일 로드 완료: {len(YOLO_LABEL_MAP)}개 약품")
else:
    print("⚠️ 경고: drug_mapping.json 파일이 없습니다.")

# =========================================================
# 4. 외부 API (식약처 공공데이터) 연동 로직
# =========================================================
def get_full_drug_report(item_seq, item_name):
    """
    테스트 코드에서 성공한 params 형식을 100% 반영하여 데이터를 호출합니다.
    """
    if USE_MOCK_DATA:
        print("ℹ️ [INFO] Mock Data 모드로 작동 중입니다.")
        return {
            "basic": {"itemName": item_name, "efcyQesitm": "테스트 효능", "useMethodQesitm": "테스트 복용법", "atpnQesitm": "테스트 주의사항"},
            "mix_taboo": [], "age_taboo": [], "pregnant_taboo": []
        }

    report = {"basic": None, "mix_taboo": [], "age_taboo": [], "pregnant_taboo": []}
    
    # ★ 테스트 코드 성공 형식을 그대로 적용 (numOfRows를 10으로 늘려 안정성 확보)
    default_params = {
        "serviceKey": DATA_GO_KR_KEY,
        "type": "json",
        "pageNo": 1,
        "numOfRows": 10
    }

    print(f"📡 [DEBUG] API 호출 시작: {item_name} (코드: {item_seq})")

    # [1] 기본 정보 (e약은요) - 품목기준코드(itemSeq)로 검색
    try:
        p = default_params.copy()
        p["itemSeq"] = str(item_seq).strip()
        res = requests.get(URL_DRUG_INFO, params=p, timeout=5)
        
        if res.status_code == 200:
            data = res.json()
            # 테스트 코드 성공 결과인 data['body']['items'] 구조를 따름
            if 'body' in data and 'items' in data['body'] and data['body']['items']:
                report['basic'] = data['body']['items'][0]
                print(f"✅ [SUCCESS] {item_name} 기본 정보 수신 성공")
            else:
                print(f"⚠️ [WARN] {item_name} 검색 결과가 비어있습니다.")
    except Exception as e:
        print(f"❌ [ERROR] 기본 정보 로드 실패: {e}")

    # [2] 병용 금기 (DUR) - 제품명으로 검색
    try:
        p = default_params.copy()
        p["itemName"] = item_name
        res = requests.get(URL_DUR_MIXTURE, params=p, timeout=5)
        if res.status_code == 200:
            report['mix_taboo'] = res.json().get('body', {}).get('items', [])
    except:
        report['mix_taboo'] = []

    # [3] 연령 금기 (DUR)
    try:
        p = default_params.copy()
        p["itemSeq"] = str(item_seq).strip()
        res = requests.get(URL_DUR_AGE, params=p, timeout=5)
        if res.status_code == 200:
            report['age_taboo'] = res.json().get('body', {}).get('items', [])
    except:
        report['age_taboo'] = []

    # [4] 임부 금기 (DUR)
    try:
        p = default_params.copy()
        p["itemSeq"] = str(item_seq).strip()
        res = requests.get(URL_DUR_PREGNANT, params=p, timeout=5)
        if res.status_code == 200:
            report['pregnant_taboo'] = res.json().get('body', {}).get('items', [])
    except:
        report['pregnant_taboo'] = []

    return report

# =========================================================
# 5. Gemini AI 상담 로직
# =========================================================
def generate_ai_advice(drug_report, user_req: ConsultationRequest):
    basic = drug_report.get('basic') or {}
    mix_taboo = drug_report.get('mix_taboo') or []
    age_taboo = drug_report.get('age_taboo') or []
    pregnant_taboo = drug_report.get('pregnant_taboo') or []

    # 정보 추출
    target_info = ""
    mapping = {"효능": "efcyQesitm", "복용법": "useMethodQesitm", "주의사항": "atpnQesitm"}
    for opt in user_req.options:
        key = mapping.get(opt)
        if key: target_info += f"- {opt}: {basic.get(key, '정보 없음')}\n"

    # 경고 문구 생성
    warning_text = ""
    if mix_taboo:
        names = [item.get('MIXTURE_ITEM_NAME', '') for item in mix_taboo]
        warning_text += f"🚨 [병용 금기]: {', '.join(names)}와 함께 복용 금지\n"
    if age_taboo:
        warning_text += f"🚨 [연령 금기]: 특정 연령대 복용 금지 성분 포함\n"
    if pregnant_taboo:
        warning_text += f"🚨 [임부 금기]: 임산부 복용 주의 성분 포함\n"

    # 로그 출력용
    print(f"📋 상담 데이터 구성 완료 (약품명: {basic.get('itemName', '미상')})")

    prompt = f"""
    당신은 전문 AI 약사입니다. 아래 정보를 바탕으로 상담해주세요.

    [사용자 정보]
    - 증상: "{user_req.user_profile.symptom}"
    - 상태: {user_req.user_profile.condition} (나이: {user_req.user_profile.age}세)
    
    [약품 정보: {basic.get('itemName', '미상')}]
    {target_info}
    
    [시스템 안전 경고 데이터]
    {warning_text}

    [지시사항]
    1. 사용자의 상태(나이, 임신여부, 질환)와 약의 금기사항이 충돌하면 즉시 강력하게 경고하세요.
    2. 이 약이 사용자의 증상에 효과적인지 판단해 주세요.
    3. 만약 약품 정보가 '미상'이거나 '정보 없음'이라면, 함부로 복용하지 말고 전문가를 찾으라고 강력히 권고하세요.
    4. 일반인이 이해하기 쉬운 친절한 말투로 설명해주세요.
    """
    
    response = llm_model.generate_content(prompt)
    return response.text

# =========================================================
# 6. API 엔드포인트
# =========================================================
@app.get("/")
def health_check():
    return {"status": "ok", "message": "서버가 정상 가동 중입니다. /docs로 접속하세요."}

@app.post("/consult")
def consult_drug(request: ConsultationRequest):
    str_id = str(request.class_id)
    drug_meta = YOLO_LABEL_MAP.get(str_id)
    
    if not drug_meta:
        raise HTTPException(status_code=404, detail="식별된 약품 정보를 매핑 파일에서 찾을 수 없습니다.")

    # 공공데이터 API 조회
    drug_report = get_full_drug_report(drug_meta['code'], drug_meta['name'])
    
    # AI 상담 생성
    try:
        advice = generate_ai_advice(drug_report, request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini Error: {e}")

    return {
        "drug_name": drug_meta['name'],
        "advice": advice,
        "source": "Mock Data" if USE_MOCK_DATA else "식약처 공공데이터"
    }
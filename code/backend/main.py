import os
import json
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
# 디버깅
import traceback
import logging

# 분리된 서비스 모듈 임포트
from services.img_vision import analyze_health_image
from services.drug_api import get_full_drug_report
from services.ai_pharmacist import generate_ai_advice

# [추가] DB 관리 함수 임포트
# [추가] DB 관리 함수 임포트
from database import register_user_drug, get_user_drug_list, init_db

# config.py에서 URL 설정 로드
from config import *



app = FastAPI(
    title="AI 약사 통합 관리 서비스 (DB 연동형)",
    description="사진 등록, 복약 상담, 음식 상호작용 분석 및 DB 저장 기능을 제공합니다.",
    version="2.1.0"
)

@app.on_event("startup")
def on_startup():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    print(f"✅ 매핑 파일 로드 완료")
else:
    print("⚠️ 경고: drug_mapping.json 파일이 없습니다.")

# =========================================================
# 4. API 엔드포인트
# =========================================================

@app.get("/")
def health_check():
    return {"status": "ok", "message": "AI 약사 서버 가동 중"}

@app.post("/register-drug-image")
async def register_drug_by_image(file: UploadFile = File(...), mode: str = "prescription"):
    """
    [기능 1] 사진을 찍어 약품 등록 + DB 자동 저장
    """
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # 1. 이미지 분석 (Gemini Vision)
        analysis_result = analyze_health_image(temp_path, mode=mode)
        
        # 2. [DB 이식] 분석된 약물 리스트를 DB에 저장
        # Gemini가 보낸 결과(analysis_result) 내에 약물 이름 리스트가 있다고 가정합니다.
        # mode="prescription" -> medications list of objects
        # mode="hospital_prescription" -> prescribed_drugs list of objects
        detected_pills = []
        if "medications" in analysis_result:
            detected_pills = [m.get("name", m.get("drug_name", "Unknown")) for m in analysis_result["medications"]]
        elif "prescribed_drugs" in analysis_result:
             detected_pills = [m.get("name", m.get("drug_name", "Unknown")) for m in analysis_result["prescribed_drugs"]]
        
        # Fallback if just a list of strings
        if not detected_pills:
             detected_pills = analysis_result.get("detected_pills", [])
        
        # 만약 리스트가 있다면 하나씩 DB에 저장
        for pill_name in detected_pills:
            # 우선 user_id는 "test_user"로 고정합니다.
            register_user_drug(user_id="test_user", drug_name=pill_name, mode=mode)
            print(f"💾 DB 저장 완료: {pill_name}")

        return {
            "status": "success",
            "message": f"{len(detected_pills)}개의 약물이 DB에 등록되었습니다.",
            "detected_data": analysis_result
        }
    except Exception as e:
        # Debugging: Log full error
        with open("experiment.log", "a") as log_file:
            log_file.write(f"\n[Error] /register-drug-image failed: {str(e)}\n")
            log_file.write(traceback.format_exc())
            if 'analysis_result' in locals():
                 log_file.write(f"Analysis Result: {json.dumps(analysis_result, ensure_ascii=False)}\n")
            else:
                 log_file.write("Analysis Result: Not available (failed before analysis)\n")
        
        raise HTTPException(status_code=500, detail=f"이미지 분석 및 저장 실패: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/consult")
def consult_drug(request: ConsultationRequest):
    """
    [기능 2] 관리창 맞춤 상담 (e약은요 + 9종 DUR 데이터)
    """
    str_id = str(request.class_id)
    drug_meta = YOLO_LABEL_MAP.get(str_id)
    
    if not drug_meta:
        raise HTTPException(status_code=404, detail="매핑 정보를 찾을 수 없습니다.")

    drug_report = get_full_drug_report(drug_meta['code'], drug_meta['name'])
    
    try:
        advice = generate_ai_advice(drug_report, request)
        return {
            "drug_name": drug_meta['name'],
            "selected_options": request.options,
            "advice": advice
        }
    
    except Exception as e:
        # 디벅깅
        logging.error("❌ /consult crashed: %s", e)
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"상담 생성 오류: {str(e)}")

class ConsultByNameRequest(BaseModel):
    drug_name: str
    topic: str

@app.post("/consult-by-name")
def consult_drug_by_name(request: ConsultByNameRequest):
    """
    [기능 2-1] 약품명으로 상담 (처방전/약봉투에서 추가한 약 지원)
    """
    from services.drug_api import search_drug_by_name
    
    # 1. 약품명으로 itemSeq 검색
    drug_info = search_drug_by_name(request.drug_name)
    
    if not drug_info:
        raise HTTPException(
            status_code=404, 
            detail=f"'{request.drug_name}' 약품 정보를 찾을 수 없습니다. 정확한 약품명을 확인해주세요."
        )
    
    # 2. DUR 리포트 가져오기
    drug_report = get_full_drug_report(drug_info["item_seq"], drug_info["item_name"])
    
    # 3. AI 상담 생성 (기존 generate_ai_advice 재사용)
    # ConsultationRequest 형식으로 변환
    mock_request = ConsultationRequest(
        class_id=0,  # 더미 값 (사용되지 않음)
        user_profile=UserProfile(
            symptom="약품 정보 문의",
            age=30,
            condition="일반"
        ),
        options=[request.topic]
    )
    
    try:
        advice = generate_ai_advice(drug_report, mock_request)
        return {
            "drug_name": drug_info["item_name"],
            "selected_topic": request.topic,
            "advice": advice
        }
    
    except Exception as e:
        logging.error("❌ /consult-by-name crashed: %s", e)
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"상담 생성 오류: {str(e)}")


@app.post("/analyze-food-interaction")
async def analyze_food(file: UploadFile = File(...)):
    """
    [기능 3] 음식 상호작용 분석 (DB에서 내 약 목록 불러오기)
    """
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # 1. [DB 이식] DB에서 이전에 등록한 약 리스트를 싹 가져옵니다.
        current_pill_list = get_user_drug_list(user_id="test_user")
        
        if not current_pill_list:
            current_pill_list = "현재 복용 중인 약 정보 없음 (상담 시 참고만 하세요)"
        
        print(f"🔍 DB에서 불러온 약 목록: {current_pill_list}")

        # 2. 음식 사진과 함께 Gemini에게 분석 요청
        result = analyze_health_image(temp_path, mode="food", current_pill=current_pill_list)
        return result
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
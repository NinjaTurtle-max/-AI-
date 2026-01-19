import os
import json
import shutil
import traceback
import logging

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# services 모듈 임포트
from services.img_vision import analyze_health_image
from services.drug_api import get_full_drug_report, search_drug_by_name

# ai_pharmacist 로드 (에러 방지 처리)
try:
    from services.ai_pharmacist import generate_ai_advice
except ImportError:
    def generate_ai_advice(report, request):
        return "⚠️ AI 약사 모듈 로드 실패"

# DB 및 설정 로드
# [중요] database.py에서 사용자 프로필 관련 함수도 가져옵니다.
from database import (
    register_user_drug, 
    get_user_drug_list, 
    init_db, 
    save_user_profile,  # ✨ 추가됨
    get_user_profile,   # ✨ 추가됨
    delete_user_drug,    # ✨ 삭제 기능 추가
    get_user_drugs_detail, # ✨ 상세 조회 추가
    clear_all_user_drugs   # ✨ 전체 삭제 추가
)
from config import *

# 환경 변수 로드
load_dotenv()

app = FastAPI(
    title="AI 약사 통합 관리 서비스",
    description="식약처 API, Gemini Vision, SQLite DB를 연동한 헬스케어 백엔드",
    version="3.1.0" # 버전 업!
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

# =========================================================
# 1. 데이터 모델 정의 (Pydantic)
# =========================================================

# [✨ 신규] 사용자 정보 저장용 요청 모델
class UserHistoryRequest(BaseModel):
    user_id: str          # 로그인 ID (예: "user_007")
    name: str             # 이름
    age: int              # 나이
    gender: str           # 성별 (Male/Female)
    is_pregnant: bool = False
    chronic_diseases: list[str] = [] # ["고혈압", "당뇨"]
    allergies: list[str] = []        # ["복숭아", "페니실린"]

# 기존 상담용 모델
class UserProfile(BaseModel):
    symptom: str
    age: int
    condition: str

class ConsultationRequest(BaseModel):
    class_id: int
    user_profile: UserProfile
    options: list[str]

class ConsultByNameRequest(BaseModel):
    drug_name: str
    topic: str
    user_id: str = "test_user" # 프론트에서 user_id를 넘겨줄 수 있도록 필드 추가

# 매핑 파일 로드
MAPPING_FILE = "drug_mapping.json"
YOLO_LABEL_MAP = {}
if os.path.exists(MAPPING_FILE):
    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        YOLO_LABEL_MAP = json.load(f)

# =========================================================
# 2. API 엔드포인트
# =========================================================

@app.get("/")
def health_check():
    return {"status": "ok", "message": "AI Pharmacist Backend Ready!"}

# ---------------------------------------------------------
# [기능 A] 사용자 프로필 관리 (신규 추가됨 ✨)
# ---------------------------------------------------------

@app.post("/user/profile")
def update_profile(req: UserHistoryRequest):
    """
    [프론트엔드 -> 백엔드]
    사용자가 입력한 건강 정보(나이, 기저질환 등)를 DB에 저장합니다.
    """
    print(f"👤 프로필 업데이트 요청: {req.name} ({req.user_id})")
    try:
        success = save_user_profile(
            user_id=req.user_id,
            name=req.name,
            age=req.age,
            gender=req.gender,
            diseases=req.chronic_diseases,
            allergies=req.allergies,
            is_pregnant=req.is_pregnant
        )
        if success:
            return {"status": "success", "message": "프로필이 저장되었습니다."}
        else:
            raise HTTPException(status_code=500, detail="DB 저장 실패")
    except Exception as e:
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/profile/{user_id}")
def get_profile(user_id: str):
    """
    [백엔드 -> 프론트엔드]
    앱 실행 시 사용자의 기존 정보를 불러옵니다.
    """
    try:
        profile = get_user_profile(user_id)
        if profile:
            return {"status": "success", "data": profile}
        else:
            return {"status": "empty", "message": "등록된 프로필이 없습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# [기능 1] 이미지로 약 등록 + DB 저장
# ---------------------------------------------------------
# ---------------------------------------------------------
# [기능 1] 이미지로 약 등록 + DB 저장
# ---------------------------------------------------------
@app.post("/register-drug-image")
async def register_drug_by_image(file: UploadFile = File(...), mode: str = Form("prescription"), user_id: str = Form("test_user")):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        print(f"📸 이미지 분석 요청: {file.filename} (모드: {mode})")
        analysis_result = analyze_health_image(temp_path, mode=mode)
        
        detected_pills = []
        if mode == "pill_id":
            if "detected_features" in analysis_result:
                name = analysis_result["detected_features"].get("item_name")
                if name: detected_pills.append(name)
            if not detected_pills and "candidates" in analysis_result:
                candidates = analysis_result.get("candidates", [])
                if candidates: detected_pills.append(candidates[0].get("ITEM_NAME"))

        elif mode == "prescription":
            if "medications" in analysis_result:
                detected_pills = [m.get("name", "Unknown") for m in analysis_result["medications"]]

        elif mode == "hospital_prescription":
            if "prescribed_drugs" in analysis_result:
                detected_pills = [m.get("name", "Unknown") for m in analysis_result["prescribed_drugs"]]
        
        saved_count = 0
        for pill_name in detected_pills:
            if pill_name and pill_name != "Unknown":
                # [수정] 프론트에서 받은 user_id 사용
                register_user_drug(user_id=user_id, drug_name=pill_name, mode=mode)
                saved_count += 1
                print(f"💾 DB 저장: {pill_name}")

        response_data = {
            "status": "success",
            "message": f"{saved_count}개의 약물이 등록되었습니다.",
            "detected_pills": detected_pills,
            "raw_data": analysis_result
        }
        print(f"📤 [RESPONSE] {json.dumps(response_data, ensure_ascii=False, indent=2)}")
        return response_data
    except Exception as e:
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"분석 실패: {str(e)}")
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

# ---------------------------------------------------------
# [기능 2] 약품명으로 상담 (DUR + AI) - ✨ 초개인화 로직 반영
# ---------------------------------------------------------
@app.post("/consult")
def consult_drug_by_name(request: ConsultByNameRequest):
    """
    고정된 더미 데이터가 아닌 실제 DB의 사용자 프로필을 반영합니다.
    URL Path는 /consult 유지 (프론트엔드 호환)
    """
    # ConsultByNameRequest에 user_id가 없으면 오류나므로 모델에도 추가 필요
    # (주의: 모델 정의는 파일 상단에 있으므로 여기서 접근 가능하지만 필드 추가는 별도 작업 필요)
    # 하지만 여기서는 request.user_id 접근 시 에러가 날 수 있으니 getattr 사용하거나 모델 수정 필요.
    # 안전하게 user_id를 가져오기 위해 getattr 사용 (모델 수정은 아래에서 별도로 진행)
    user_id = getattr(request, "user_id", "test_user")

    print(f"💊 상담 요청: {request.drug_name} (사용자: {user_id})")
    
    # 1. DB에서 실제 사용자 정보 조회
    user_info = get_user_profile(user_id)
    
    # 2. 동적 데이터 할당 (DB에 없으면 기본값 사용)
    current_age = user_info["age"] if user_info else 30
    current_condition = ", ".join(user_info["chronic_diseases"]) if user_info and user_info["chronic_diseases"] else "특이사항 없음"
    
    drug_info = search_drug_by_name(request.drug_name)
    if not drug_info:
        raise HTTPException(status_code=404, detail=f"'{request.drug_name}' 정보를 찾을 수 없습니다.")
    
    drug_report = get_full_drug_report(drug_info["item_seq"], drug_info["item_name"])
    
    try:
        # 3. 실제 나이와 증상을 주입하여 AI 상담 요청
        mock_req = ConsultationRequest(
            class_id=0,
            user_profile=UserProfile(
                symptom=f"문의 사항 및 기저질환: {current_condition}", 
                age=current_age, 
                condition=current_condition
            ),
            options=[request.topic]
        )
        advice = generate_ai_advice(drug_report, mock_req)
        
        return {
            "drug_name": drug_info["item_name"],
            "selected_topic": request.topic,
            "advice": advice,
            "user_applied_age": current_age,
            "full_report": drug_report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 상담 생성 오류: {str(e)}")

# ---------------------------------------------------------
# [기능 3] 음식 상호작용 분석
# ---------------------------------------------------------
@app.post("/analyze-food-interaction")
async def analyze_food(file: UploadFile = File(...), user_id: str = Form("test_user")):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # [수정] DB에서 약 목록 가져오기 (user_id 활용)
        drug_list = get_user_drug_list(user_id=user_id) 
        
        if isinstance(drug_list, list):
            current_pill_str = ", ".join(drug_list)
        else:
            current_pill_str = str(drug_list)
            
        if not current_pill_str:
            current_pill_str = "현재 복용 중인 약 없음"
            
        print(f"🔍 [음식분석] 내 약 목록: {current_pill_str}")

        result = analyze_health_image(temp_path, mode="food", current_pill=current_pill_str)
        return result
    except Exception as e:
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"음식 분석 실패: {str(e)}")
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

# ---------------------------------------------------------
# [기능 4] 약물 삭제
# ---------------------------------------------------------
@app.delete("/user/drug/{drug_id}")
def delete_drug(drug_id: int):
    """
    복약 관리에서 약물을 삭제합니다.
    """
    print(f"🗑️ 약물 삭제 요청: ID {drug_id}")
    try:
        success = delete_user_drug(drug_id)
        if success:
            return {"status": "success", "message": "약물이 삭제되었습니다."}
        else:
            raise HTTPException(status_code=404, detail="약물을 찾을 수 없습니다.")
    except HTTPException:
        raise
        raise HTTPException(status_code=500, detail=f"삭제 실패: {str(e)}")

# [✨ 신규] 수동 약물 등록
class UserDrugAddRequest(BaseModel):
    user_id: str
    drug_name: str
    description: str = None

@app.post("/user/drug")
def add_user_drug(req: UserDrugAddRequest):
    """
    사용자가 직접 약물을 등록합니다.
    """
    print(f"➕ 약물 등록 요청: {req.drug_name} ({req.user_id})")
    try:
        new_id = register_user_drug(req.user_id, req.drug_name, mode="manual")
        return {
            "status": "success",
            "message": "약물이 등록되었습니다.",
            "data": {
                "id": new_id,
                "name": req.drug_name,
                "description": req.description
            }
        }
    except Exception as e:
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# [✨ 신규] 사용자 약물 리스트 조회 (앱 켤 때 로딩용)
@app.get("/user/drugs/{user_id}")
def get_user_drugs(user_id: str):
    """
    사용자의 모든 약물 리스트를 반환합니다.
    """
    try:
        drugs = get_user_drugs_detail(user_id)
        return {"status": "success", "data": drugs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# [✨ 신규] 약물 전체 삭제
@app.delete("/user/drugs/all/{user_id}")
def clear_user_drugs(user_id: str):
    """
    사용자의 모든 약물을 삭제합니다.
    """
    print(f"🗑️ [전체 삭제] 사용자 {user_id}의 약물 초기화")
    try:
        success = clear_all_user_drugs(user_id)
        if success:
            return {"status": "success", "message": "모든 약물이 삭제되었습니다."}
        else:
            raise HTTPException(status_code=500, detail="삭제 실패")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
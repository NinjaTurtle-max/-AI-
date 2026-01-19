💊 AI 약사 통합 관리 서비스 - Backend
FastAPI 기반의 헬스케어 백엔드 서버로, Gemini AI와 식약처 공공 API를 연동하여 약물 식별, 처방전/약봉투 분석, 음식 상호작용 경고, AI 약사 상담 등 종합 복약 관리 기능을 제공합니다.

📁 프로젝트 구조
backend/
├── main.py                      # FastAPI 메인 서버 진입점
├── database.py                  # SQLite DB 관리 (사용자, 약물, 금기사항)
├── config.py                    # API 엔드포인트 설정
├── requirements.txt             # 필요 패키지 목록
├── drug_mapping.json            # 약품 ID → 약품명 매핑 (118개 클래스)
├── pill_recognition_rules.json  # 알약 인식 규칙 가이드
├── test.py                      # 모듈 통합 테스트
├── test_logic.py                # 로직 검증 테스트
├── test_prescription.txt        # 테스트용 샘플
├── .env                         # 환경 변수 (API 키, 설정)
├── services/
│   ├── img_vision.py            # 이미지 분석 요청 라우터
│   ├── drug_api.py              # 식약처 API 연동 & 정보 요약
│   ├── ai_pharmacist.py         # Gemini AI 기반 약사 상담
│   └── vision/                  # 세부 비전 모듈
│       ├── pill_identifier.py   # 알약 식별 (특징 추출 + DB 검색)
│       ├── prescription.py      # 약봉투/처방전 OCR
│       └── food_checker.py      # 음식-약물 상호작용 분석
└── scripts/
    └── sync_pill_db.py          # 식약처 알약 데이터 동기화

🚀 설치 및 실행
1. 환경 설정
cd backend

# 가상환경 생성 (권장)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필수 패키지 설치
pip install -r requirements.txt

2. 환경 변수 설정(.env)
backend 폴더에 .env 파일을 생성하고 다음을 입력하세요:
# Gemini API 키 (필수)
GEMINI_API_KEY=your_gemini_api_key_here

# 식약처 공공데이터 API 키 (필수)
# ⚠️ "Decoding Key"를 사용해야 합니다 (Encoding Key 아님)
KEY_E_DRUG=your_data_go_kr_key_here

# 개발용 Mock 데이터 사용 여부
USE_MOCK_DATA=False

API 키 발급:

- Gemini API: Google AI Studio에서 발급
- 식약처 API: 공공데이터포털에서 "e약은요" 서비스 신청 후 Decoding Key 복사

3. 데이터베이스 초기화
python3 database.py

출력 예:
✅ 통합 DB (사용자 프로필 + 약물 + 금기사항) 초기화 완료

4. 서버 실행
python3 main.py
또는:
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

📡 주요 API 엔드포인트
1️⃣ 사용자 프로필 관리
프로필 저장
POST /user/profile
Content-Type: application/json

{
  "user_id": "user_007",
  "name": "김철수",
  "age": 35,
  "gender": "Male",
  "chronic_diseases": ["고혈압", "당뇨"],
  "allergies": ["페니실린"],
  "is_pregnant": false
}

프로필 조회
GET /user/profile/{user_id}

2️⃣ 약물 등록 (이미지 분석)
POST /register-drug-image?mode=prescription
Content-Type: multipart/form-data

file: [이미지 파일]

- pill_id: 알약 사진 식별
- prescription: 약국 약봉투 분석
- hospotal_prescription: 병원 처방전 분석

응답 예시:
{
  "status": "success",
  "message": "3개의 약물이 등록되었습니다.",
  "detected_pills": [
    {
      "name": "타이레놀",
      "efficacy": "해열진통제",
      "dosage": "1일 3회"
    }
  ]
}

3️⃣ 약품명으로 AI 상담
POST /consult-by-name
Content-Type: application/json

{
  "drug_name": "타이레놀",
  "topic": "효능"
}

지원 주제:
- 효능: 약의 주요 효과
- 금기사항: 주의사항, 부작용, 병용금지약물
- 복용법: 용볍, 용량, 복용 시간

응답 예시:
{
  "advice": "타이레놀은 두통과 감기로 인한 발열을 완화하는 해열진통제입니다...",
  "drug_name": "타이레놀",
  "topic": "효능"
}

4️⃣ 음식 상호작용 분석
POST /analyze-food-interaction
Content-Type: multipart/form-data

file: [음식 이미지]

응답 예시:
{
  "type": "food",
  "detected_items": ["자몽", "치즈"],
  "main_ingredients": "자몽, 치즈, 크래커",
  "warning_message": "⚠️ 고혈압약 복용 중 자몽은 피하세요. 약효를 방해합니다."
}

5️⃣ 약물 삭제
DELETE /user/drug/{drug_id}

응답:
{
  "status": "success",
  "message": "약물이 삭제되었습니다."
}

🧪 테스트
통합 테스트 실행
python3 test.py

태스트 항목:
1. ✅ 텍스트 요약 기능 (summarize_text)
2. ✅ Gemini AI 상담 생성 (generate_ai_advice)
3. ✅ 이미지 분석 (알약/약봉투/처방전/음식)
4. ✅ 에러 처리 로직

로직 검증 테스트
python3 test_logic.py
더 자세한 디버깅 정보를 출력합니다.

🗄️ 핵심 DB 함수
# 사용자 관리
save_user_profile(user_id, name, age, gender, diseases, allergies, is_pregnant)
get_user_profile(user_id)

# 약물 관리
register_user_drug(user_id, drug_name, item_seq, mode)
get_user_drug_list(user_id)
delete_user_drug(drug_id)

# 상호작용 검사
check_food_interaction(user_id, detected_food_list)

🔧 주요 모듈 설명
main.py
- FastAPI 앱의 진입점
- 모든 API 엔드포인트 정의
- CORS, 에러 핸들링 설정
- DB 초기화 및 라우팅

services/img_vision.py
이미지 분석 요청 분배 라우터
- 요청 모드(pill_id, prescription 등)에 따라 적절한 분석 모듈로 연결
- Gemini 2.5 Flash 모델 관리 (폴백 로직 포함)

services/vision/pill_identifier.py
알약 식별 (특징 추출 + DB 검색)
- Gemini Vision으로 알약의 색상, 모양, 각인 특징 추출
- pill_recognition_rules.json의 프롬프트 가이드 적용
- 로컬 SQLite DB(식약처 데이터)에서 점진적 검색:
    1차: 각인 정보(정확도 높음)
    2차: 색상 + 모양 (보수적)
    3차: 색상만 (느슨한 매칭)

services/vision/prescription.py
약봉투 & 처방전 OCR
- 약봉투에서 약품명, 용법, 주의사항 추출
- 병원 처방전에서 진단코드, 투약 정보 추출
- JSON 형식으로 정형화

services/vision/food_checker.py
음식-약물 상호작용 분석
- 음식 사진 분석 및 성분 파악
- 사용자 현재 복용 약물과 조합 시 위험도 판정
- 과학 기반 경고 메시지 생성

services/drug_api.py
식약처 "e약은요" API 연동
- 약품명 → 품목기준코드(itemSeq) 변환
- DUR(약물 사용 안전성 정보) 조회:
    병용금기, 임부금기, 연령대금기
    노인주의, 용량주의, 투여기간주의
    효능군중복, 서방정분할주의
- 텍스트 요약: 복잡한 의학정보를 2문장 요약

services/ai_pharmacist.py
Gemini AI 기반 맞춤형 약사 상담
- 사용자 프로필(나이, 기저질환, 알레르기) 컨텍스트 생성
- 약물 정보 + 건강 상태 통합 분석
- 친절한 약사 페르소나로 답변 생성
- Context Grounding: 신뢰성 높은 정보 기반 답변

database.py
SQLite 기반 로컬 데이터 저장
- 사용자 프로필, 약물 목록, 금기사항 관리
- API 호출 결과 캐싱 (반복 조회 최소화)
- 약물 간/음식-약물 상호작용 규칙 저장

config.py
모든 API 엔드포인트 설정
- 식약처 API URLs (e약은요, DUR, 낱알식별 등)
- 요청/응답 파라미터 정의

scripts/sync_pill_db.py
식약처 약품 데이터 동기화 (선택사항)
- 식약처 낱알식별 API에서 모든 약품 정보 수집
- 로컬 SQLite DB(pill_master.db) 구축
- 각인, 색상, 모양 기반 빠른 검색을 위한 인덱싱
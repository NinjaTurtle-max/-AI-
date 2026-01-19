# 💊 AI 약사 & 약물 식별 서비스 (Backend)

Gemini 2.5 Flash와 식약처 공공데이터 API를 활용한 맞춤형 약물 관리 및 상담 서비스입니다.
알약 사진 식별, 약봉투/처방전 분석, 음식 상호작용 경고 기능을 제공합니다.

---## 📂 프로젝트 구조```text
backend/
├── main.py                 # FastAPI 진입점
├── database.py             # SQLite DB 및 캐싱
├── services/
│   ├── ai_pharmacist.py    # AI 복약 지도 (상담)
│   ├── drug_api.py         # 식약처 API 연동 및 요약
│   ├── img_vision.py       # [Router] 이미지 분석 요청 분배
│   └── vision/             # [Module] 비전 기능별 모듈
│       ├── pill_identifier.py  # 알약 식별 & 점진적 검색
│       ├── prescription.py     # 약봉투 OCR
│       └── food_checker.py     # 음식 궁합 분석

🚀 설치 및 실행
1. 가상환경 생성 및 라이브러리 설치
Bash

cd backend
# 가상환경 생성 (권장)
python3 -m venv venvsource venv/bin/activate  # Windows: venv\Scripts\activate
# 의존성 설치
pip install -r requirements.txt

2. 환경 변수 설정 (.env)
backend 폴더 안에 .env 파일을 생성하고 아래 키를 입력하세요.
Ini, TOML

GEMINI_API_KEY=your_gemini_key_hereKEY_E_DRUG=your_data_go_kr_decoding_keyUSE_MOCK_DATA=False

3. DB 초기화 및 서버 실행
Bash

python3 database.py  # DB 테이블 생성 (최초 1회)
python3 main.py      # 서버 시작

📡 주요 API 엔드포인트
서버가 실행되면 Swagger UI(http://localhost:8000/docs)에서 모든 API를 테스트할 수 있습니다.

1. 약물 등록 (이미지 분석)
POST /register-drug-image?mode={mode}
mode 지원:
pill_id: 알약 사진 식별 (식약처 DB 자동 검색)
prescription: 약국 약봉투 분석 (텍스트 추출)
hospital_prescription: 병원 처방전 분석

2. 약품명으로 AI 상담
POST /consult-by-name
사용자의 나이, 기저질환 정보를 고려하여 맞춤형 복약 지도를 제공합니다.
효능, 복용법, 금기사항에 대해 질문할 수 있습니다.

3. 음식 상호작용 분석
POST /analyze-food-interaction
현재 복용 중인 약과 함께 먹으려는 음식의 궁합(위험도)을 분석합니다.

📦 주요 모듈 설명
services/img_vision.py (Router)
이미지 분석 요청을 받아 적절한 전문 모듈로 연결하는 라우터입니다.

vision/pill_identifier.py: 알약 식별 전용. AI가 특징(색상, 모양, 식별문자)을 추출하면 식약처 API를 **점진적(엄격->느슨)**으로 검색하여 정확도를 높입니다.

vision/prescription.py: 약봉투 및 처방전의 텍스트를 인식하여 정형화된 JSON 데이터로 변환합니다.

vision/food_checker.py: 음식 사진을 분석하여 약물 상호작용 경고를 생성합니다.
services/drug_api.py

식약처 "e약은요" API와 연동하여 약물의 효능, 용법, 금기사항(DUR) 정보를 가져옵니다.
스마트 요약: 복잡한 의학 정보를 파이썬 로직으로 핵심만 뽑아 2문장 내외로 깔끔하게 요약합니다.

services/ai_pharmacist.py
Gemini Flash 모델을 사용하여 사용자의 건강 프로필(나이, 기저질환)에 맞춘 페르소나(친절한 약사) 답변을 생성합니다.

🔧 문제 해결 (Troubleshooting)
자주 발생하는 오류
no such table: users: DB 파일이 없어서 발생하는 에러입니다. python3 database.py를 실행하여 DB를 초기화하세요.

식약처 API 응답 없음: .env의 KEY_E_DRUG가 Decoding Key인지 확인하세요. (공공데이터포털의 Encoding Key는 작동하지 않을 수 있습니다.)

ModuleNotFoundError: pip install -r requirements.txt를 통해 모든 패키지가 설치되었는지 확인하세요.
import sqlite3
import json
import google.generativeai as genai
import PIL.Image
import os
from urllib.parse import unquote
import warnings

# [설정] 경고 차단
warnings.filterwarnings("ignore", category=FutureWarning)

# [경로 설정] 현우님이 지정하신 절대 경로 반영
RULES_JSON_PATH = "backend/pill_recognition_rules.json"
MASTER_DB_PATH = "/Users/ganghyeon-u/Desktop/강원대 부트캠프(중급)/code/backend/pill_master.db"

def _load_recognition_rules():
    """전수 조사 결과가 담긴 JSON 가이드를 불러옵니다."""
    try:
        if os.path.exists(RULES_JSON_PATH):
            with open(RULES_JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ 규칙 파일 로드 실패: {e}")
    return None

def _search_local_pill_db(pill_features):
    """
    [핵심 로직] 로컬 DB(ai_pharmacist.db)에서 특징 기반 전수 조사 필터링
    """
    if not os.path.exists(MASTER_DB_PATH):
        print(f"❌ DB 파일을 찾을 수 없습니다: {MASTER_DB_PATH}")
        return []

    conn = sqlite3.connect(MASTER_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Gemini가 추출한 특징들
    target_front = pill_features.get('print_front', '')
    target_back = pill_features.get('print_back', '')
    target_color = pill_features.get('color_class1', '')
    target_shape = pill_features.get('drug_shape', '')

    # 1차 쿼리: 각인(print) 정보로 후보군 추출 (LIKE 검색으로 유연하게 대응)
    query = "SELECT * FROM pill_master_info WHERE (print_front LIKE ? OR print_back LIKE ?)"
    params = (f"%{target_front}%", f"%{target_back}%")

    # 이름 정보가 있다면 추가 검색 조건에 포함
    if pill_features.get('item_name'):
        query += " OR item_name LIKE ?"
        params += (f"%{pill_features['item_name']}%",)

    print(f"📡 [Local DB Scan] '{target_front}/{target_back}' 특징으로 전수 조사 중...")

    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # 2차 필터링: 모양과 색상 유사도 체크
        final_candidates = []
        for row in rows:
            item = dict(row)
            # 가중치 계산 (정확히 일치할수록 상위 노출)
            score = 0
            if target_front and target_front in (item.get('print_front') or ''): score += 3
            if target_back and target_back in (item.get('print_back') or ''): score += 3
            if target_shape and target_shape == item.get('drug_shape'): score += 1
            if target_color and target_color == item.get('color_class1'): score += 1
            
            item['match_score'] = score
            final_candidates.append(item)

        # 점수 높은 순으로 정렬
        final_candidates.sort(key=lambda x: x['match_score'], reverse=True)
        
        conn.close()
        return final_candidates[:10]

    except Exception as e:
        print(f"⚠️ DB 검색 에러: {e}")
        if 'conn' in locals(): conn.close()
        return []

def analyze_pill(image_path, api_key, service_key=None):
    """[Main] Gemini Vision -> Local DB 필터링"""
    if not api_key:
        return {"error": "API 키가 없습니다."}
    
    genai.configure(api_key=unquote(api_key))
    rules = _load_recognition_rules()
    
    # JSON 가이드에서 지침 추출
    instruction = rules.get("prompt_instruction", "") if rules else ""
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash') # 최신 모델 사용
        img = PIL.Image.open(image_path)
    except:
        model = genai.GenerativeModel('gemini-1.5-flash')
        img = PIL.Image.open(image_path)

    # [프롬프트] 전수 조사 규칙을 Gemini에게 주입
    prompt = f"""
    [알약 식별 전문가] 
    사진 속 알약의 특징을 JSON으로 추출하십시오.

    [필독: 각인 추출 규칙]
    {instruction}
    - 람다 기호(밑변 없는 A 모양)는 'Λ'로 읽으십시오.
    - 보이는 그대로를 텍스트화하되 기호는 한글 명칭(분할선, 마크 등)으로 변환하십시오.

    응답 형식: {{"item_name":"", "print_front":"", "print_back":"", "color_class1":"", "drug_shape":""}}
    """
    
    try:
        response = model.generate_content([prompt, img])
        content = response.text.strip().replace('```json', '').replace('```', '')
        detected_features = json.loads(content)
        
        # 로컬 DB 전수 조사 필터링 실행
        candidates = _search_local_pill_db(detected_features)
        
        return {
            "mode": "pill_id",
            "detected_features": detected_features,
            "candidates": candidates,
            "total_found": len(candidates)
        }
    except Exception as e:
        return {"error": f"분석 실패: {str(e)}"}

# =========================================================
# [검증 테스트 블록] - 타치온정 정밀 테스트 (TAT / Da)
# =========================================================
if __name__ == "__main__":
    print("\n🧪 [테스트 시나리오] 타치온정 정밀 검색 (Da / TAT)")
    print("-" * 50)
    
    # 실제 타치온정의 각인 특징 반영
    dummy_detected = {
        "item_name": "",          
        "print_front": "TAT",      # 제조사(대원제약 등) 마크/이니셜
        "print_back": "Da",      # 타치온 식별 각인
        "color_class1": "하양", 
        "drug_shape": "원형"
    }

    print(f"📝 가상 분석 특징: {json.dumps(dummy_detected, ensure_ascii=False)}")
    
    # 로컬 DB 검색 함수 호출
    results = _search_local_pill_db(dummy_detected)
    
    if results:
        print(f"\n✅ 검색 성공! {len(results)}건의 후보 발견")
        for i, res in enumerate(results[:3], 1):
            print(f"{i}. [{res['item_name']}]")
            print(f"   - DB 각인: {res['print_front']} / {res['print_back']}")
            print(f"   - 외형: {res['drug_shape']} ({res['color_class1']})")
            print(f"   - 매칭 점수: {res['match_score']}")
    else:
        print("\n❌ 검색 결과가 없습니다. 'Da' 또는 'TAT'가 DB에 있는지 확인이 필요합니다.")
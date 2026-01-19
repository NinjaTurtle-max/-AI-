import sqlite3
import json

DB_NAME = "ai_pharmacist.db"

def init_db():
    """데이터베이스 및 모든 테이블 초기화"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. [사용자 정보] 나이, 성별, 기저질환 등 (분석의 핵심)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,  -- 고유 ID (로그인 ID 등)
            name TEXT,
            age INTEGER,
            gender TEXT,               -- 'Male', 'Female'
            is_pregnant INTEGER DEFAULT 0, -- 임신 여부 (0:No, 1:Yes)
            chronic_diseases TEXT,     -- 기저질환 (JSON 리스트: ["고혈압", "당뇨"])
            allergies TEXT,            -- 알레르기 (JSON 리스트: ["복숭아", "페니실린"])
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. [복용 약물] 사용자가 현재 먹는 약
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_drugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            drug_name TEXT NOT NULL,
            item_seq TEXT,
            source_mode TEXT,
            reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')
    
    # 3. [약물 캐시] API 호출 최소화용
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drug_cache (
            item_seq TEXT PRIMARY KEY,
            item_name TEXT,
            full_report TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 4. [병용 금기] 약 vs 약 상호작용 DB
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drug_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_a TEXT NOT NULL,
            drug_b TEXT NOT NULL,
            severity TEXT,
            description TEXT,
            UNIQUE(drug_a, drug_b)
        )
    ''')

    # 5. [음식 상호작용] 약 vs 음식 상호작용 DB
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drug_food_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_name TEXT NOT NULL,
            food_category TEXT,
            risk_level TEXT,
            warning_msg TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ 통합 DB (사용자 프로필 + 약물 + 금기사항) 초기화 완료")

# =========================================================
# [A] 사용자 프로필 관리 (신규 추가됨 ✨)
# =========================================================

def save_user_profile(user_id, name, age, gender, diseases=[], allergies=[], is_pregnant=False):
    """사용자 건강 정보를 저장하거나 업데이트합니다 (Upsert)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 리스트 데이터는 JSON 문자열로 변환해서 저장
    diseases_json = json.dumps(diseases, ensure_ascii=False)
    allergies_json = json.dumps(allergies, ensure_ascii=False)
    pregnant_int = 1 if is_pregnant else 0

    try:
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, name, age, gender, chronic_diseases, allergies, is_pregnant)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, age, gender, diseases_json, allergies_json, pregnant_int))
        conn.commit()
        print(f"👤 사용자 프로필 저장 완료: {name} ({user_id})")
        return True
    except Exception as e:
        print(f"❌ 프로필 저장 실패: {e}")
        return False
    finally:
        conn.close()

def get_user_profile(user_id):
    """사용자 정보를 딕셔너리 형태로 가져옵니다."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # 컬럼명으로 접근 가능하게 설정
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "user_id": row["user_id"],
            "name": row["name"],
            "age": row["age"],
            "gender": row["gender"],
            "is_pregnant": bool(row["is_pregnant"]),
            # JSON 문자열을 다시 리스트로 변환
            "chronic_diseases": json.loads(row["chronic_diseases"]),
            "allergies": json.loads(row["allergies"])
        }
    else:
        return None

# =========================================================
# [B] 사용자 약물 관리
# =========================================================

def register_user_drug(user_id, drug_name, item_seq=None, mode="unknown"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_drugs (user_id, drug_name, item_seq, source_mode)
        VALUES (?, ?, ?, ?)
    ''', (user_id, drug_name, item_seq, mode))
    conn.commit()
    conn.close()
    print(f"💊 약물 등록 완료: {drug_name}")

def get_user_drug_list(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT drug_name FROM user_drugs WHERE user_id = ?', (user_id,))
    drugs = [row[0] for row in cursor.fetchall()]
    conn.close()
    return drugs # 리스트 반환

def delete_user_drug(record_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM user_drugs WHERE id = ?', (record_id,))
        count = cursor.rowcount
        conn.commit()
        return count > 0
    except Exception:
        return False
    finally:
        conn.close()

def clear_all_user_drugs(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM user_drugs WHERE user_id = ?', (user_id,))
        conn.commit()
        return True
    finally:
        conn.close()

# =========================================================
# [C] 금기사항 데이터 관리 (기초 데이터 쌓기)
# =========================================================

def add_food_rule(drug_name, food_cat, risk, msg):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO drug_food_interactions (drug_name, food_category, risk_level, warning_msg)
        VALUES (?, ?, ?, ?)
    ''', (drug_name, food_cat, risk, msg))
    conn.commit()
    conn.close()

# =========================================================
# [D] 분석 로직 (사용자 정보 + 약물 + 음식 통합 체크)
# =========================================================

def check_food_interaction(user_id, detected_food_list):
    """
    1. 사용자의 약 리스트 가져옴
    2. 사용자의 기저질환 정보 가져옴 (프로필) - 추후 확장 가능
    3. 음식과 약물의 충돌 체크
    """
    user_drugs = get_user_drug_list(user_id)
    warnings = []

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for drug in user_drugs:
        for food in detected_food_list:
            cursor.execute('''
                SELECT warning_msg, risk_level FROM drug_food_interactions 
                WHERE ? LIKE '%' || drug_name || '%' 
                AND ? LIKE '%' || food_category || '%'
            ''', (drug, food))
            
            rows = cursor.fetchall()
            for row in rows:
                warnings.append({
                    "drug": drug,
                    "food": food,
                    "risk": row[1],
                    "message": row[0]
                })
    
    conn.close()
    return warnings

# =========================================================
# 테스트 실행
# =========================================================
if __name__ == "__main__":
    init_db()
    
    TEST_USER = "user_007"
    
    # 1. 사용자 프로필 저장 (기저질환 포함)
    save_user_profile(
        TEST_USER, 
        name="김철수", 
        age=35, 
        gender="Male", 
        diseases=["고혈압", "역류성식도염"], 
        allergies=["땅콩"]
    )
    
    # 2. 프로필 불러오기 확인
    profile = get_user_profile(TEST_USER)
    print(f"\n📂 불러온 프로필: {json.dumps(profile, ensure_ascii=False, indent=2)}")

    # 3. 약물 등록
    register_user_drug(TEST_USER, "고혈압약", mode="manual")
    
    # 4. 금기 데이터 추가
    add_food_rule("고혈압약", "자몽", "High", "약효가 과도하게 상승하여 저혈압 쇼크 위험이 있습니다.")
    
    # 5. 음식 분석 시뮬레이션
    print("\n🔍 음식 상호작용 분석 중...")
    detected_foods = ["자몽 샐러드", "샌드위치"]
    alerts = check_food_interaction(TEST_USER, detected_foods)
    
    if alerts:
        for alert in alerts:
            print(f"🚨 [경고] {alert['drug']} 복용 중에는 '{alert['food']}' 주의! -> {alert['message']}")
    else:
        print("✅ 특이사항 없음")
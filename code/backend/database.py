import sqlite3
import json

DB_NAME = "ai_pharmacist.db"

def init_db():
    """데이터베이스 및 테이블 초기화"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. 사용자 복용 약물 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_drugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            drug_name TEXT NOT NULL,
            item_seq TEXT,
            source_mode TEXT,
            reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. 약물 상세 정보 캐시 테이블 (매번 API 호출 방지 및 속도 향상)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drug_cache (
            item_seq TEXT PRIMARY KEY,
            item_name TEXT,
            full_report TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ 통합 DB 및 테이블 초기화 완료")

# --- 약물 등록 관련 함수 ---
def register_user_drug(user_id, drug_name, item_seq=None, mode="unknown"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_drugs (user_id, drug_name, item_seq, source_mode)
        VALUES (?, ?, ?, ?)
    ''', (user_id, drug_name, item_seq, mode))
    conn.commit()
    conn.close()

# --- 복용 약물 불러오기 (음식 분석용) ---
def get_user_drug_list(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT drug_name FROM user_drugs WHERE user_id = ?', (user_id,))
    drugs = [row[0] for row in cursor.fetchall()]
    conn.close()
    return ", ".join(drugs)

if __name__ == "__main__":
    init_db()
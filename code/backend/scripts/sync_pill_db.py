import os
import sqlite3
import requests
from urllib.parse import quote
from dotenv import load_dotenv
import time

load_dotenv()

# [설정] API 및 DB 경로
BASE_URL = "http://apis.data.go.kr/1471000/MdcinGrnIdntfcInfoService03/getMdcinGrnIdntfcInfoList03"
DB_PATH = "pill_master.db"  # 식별 정보 전용 DB

def init_db():
    """식별 정보 저장을 위한 테이블 초기화"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 기존 테이블이 있으면 삭제 (최신화를 위해)
    cursor.execute("DROP TABLE IF EXISTS pill_master_info")
    # 테이블 생성 (식약처 API 응답 필드 기준)
    cursor.execute("""
        CREATE TABLE pill_master_info (
            item_seq TEXT PRIMARY KEY,
            item_name TEXT,
            entp_name TEXT,
            chart TEXT,
            item_image TEXT,
            print_front TEXT,
            print_back TEXT,
            drug_shape TEXT,
            color_class1 TEXT,
            color_class2 TEXT,
            line_front TEXT,
            line_back TEXT,
            img_regist_ts TEXT
        )
    """)
    conn.commit()
    return conn

def sync_pill_data():
    service_key = os.getenv("KEY_E_DRUG")
    if not service_key:
        print("❌ 에러: .env 파일에 KEY_E_DRUG가 없습니다.")
        return

    safe_key = quote(service_key, safe='')
    conn = init_db()
    cursor = conn.cursor()

    page_no = 1
    num_of_rows = 100
    total_collected = 0

    print("🚀 [수집 시작] 식약처 알약 식별 정보 전체 동기화 중...")

    while True:
        # API 호출 URL 조립
        final_url = f"{BASE_URL}?serviceKey={safe_key}&type=json&numOfRows={num_of_rows}&pageNo={page_no}"
        
        try:
            # URL 강제 고정 방식 (requests 세션 사용)
            session = requests.Session()
            req = requests.Request('GET', final_url)
            prepped = session.prepare_request(req)
            prepped.url = final_url
            response = session.send(prepped, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                body = data.get('body', {})
                items = body.get('items', [])
                total_count = body.get('totalCount', 0)

                if not items:
                    break

                # DB에 벌크 인서트 (Insert or Replace)
                for item in items:
                    cursor.execute("""
                        INSERT OR REPLACE INTO pill_master_info 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item.get('ITEM_SEQ'),
                        item.get('ITEM_NAME'),
                        item.get('ENTP_NAME'),
                        item.get('CHART'),
                        item.get('ITEM_IMAGE'),
                        item.get('PRINT_FRONT'),
                        item.get('PRINT_BACK'),
                        item.get('DRUG_SHAPE'),
                        item.get('COLOR_CLASS1'),
                        item.get('COLOR_CLASS2'),
                        item.get('LINE_FRONT'),
                        item.get('LINE_BACK'),
                        item.get('IMG_REGIST_TS')
                    ))
                
                conn.commit()
                total_collected += len(items)
                print(f"📦 동기화 중... ({total_collected} / {total_count})")

                # 모든 데이터를 다 가져왔으면 종료
                if total_collected >= total_count:
                    break
                
                page_no += 1
                time.sleep(0.1)  # 서버 매너 타임
            else:
                print(f"❌ {page_no}페이지 호출 실패 (코드: {response.status_code})")
                break
        except Exception as e:
            print(f"⚠️ 에러 발생: {e}")
            break

    # 검색 성능을 위한 인덱스 생성 (각인, 모양, 색상)
    print("⚡ 검색 최적화 인덱스 생성 중...")
    cursor.execute("CREATE INDEX idx_print_front ON pill_master_info(print_front)")
    cursor.execute("CREATE INDEX idx_print_back ON pill_master_info(print_back)")
    cursor.execute("CREATE INDEX idx_item_name ON pill_master_info(item_name)")
    conn.commit()
    conn.close()

    print(f"✅ 동기화 완료! 'pill_master.db'에 {total_collected}개의 데이터가 저장되었습니다.")

if __name__ == "__main__":
    sync_pill_data()
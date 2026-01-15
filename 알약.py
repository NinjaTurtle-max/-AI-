# 1. 상수 정의 (또는 설정 파일에서 불러옴)
KEY_E_DRUG = "drug_list"

# 2. 샘플 데이터
data = {
    KEY_E_DRUG: ["비타민C", "타이레놀", "아스피린"],
    "category": "common_medicine"
}

# 3. 타이레놀 존재 여부 조회 함수
def check_drug_existence(data, drug_name):
    # 키가 존재하는지 먼저 확인
    if KEY_E_DRUG in data:
        # 해당 키의 리스트 안에 타이레놀이 있는지 확인
        if drug_name in data[KEY_E_DRUG]:
            return True
    return False

# 결과 출력
target = "타이레놀"
if check_drug_existence(data, target):
    print(f"조회 결과: {target}이(가) 데이터에 존재합니다.")
else:
    print(f"조회 결과: {target}을(를) 찾을 수 없습니다.")
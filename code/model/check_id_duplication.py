import json
import os
from collections import defaultdict

# 원본 데이터 경로 (건현우님의 환경에 맞게 설정됨)
LABEL_NAME = "/Users/ganghyeon-u/Downloads/166.약품식별 인공지능 개발을 위한 경구약제 이미지 데이터/01.데이터/1.Training/라벨링데이터/경구약제조합 5000종/"

def analyze_json_ids():
    json_files = []
    # 1. JSON 파일 수집
    for dirpath, _, filenames in os.walk(LABEL_NAME):
        for filename in filenames:
            if filename.endswith(".json"):
                json_files.append(os.path.join(dirpath, filename))

    print(f"📊 총 {len(json_files)}개의 JSON 파일 분석 시작...")

    id_occurrences = defaultdict(list)
    total_images_in_files = 0

    # 2. 상위 1000개 파일만 샘플링하여 ID 중복도 체크 (속도 조절)
    for i, file_path in enumerate(json_files[:1000]):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                images = data.get('images', [])
                for img in images:
                    orig_id = img.get('id')
                    # 원본 ID와 해당 ID가 발견된 파일 경로 저장
                    id_occurrences[orig_id].append(os.path.basename(file_path))
                    total_images_in_files += 1
                    
        except Exception as e:
            continue

    print("\n--- 📝 분석 결과 보고서 ---")
    print(f"체크된 파일 수: 1000개")
    print(f"체크된 총 이미지 개수: {total_images_in_files}개")
    print(f"발견된 고유한 원본 ID 개수: {len(id_occurrences)}개")

    # 중복률 계산
    if len(id_occurrences) > 0:
        duplication_ratio = (1 - (len(id_occurrences) / total_images_in_files)) * 100
        print(f"⚠️ ID 중복도: {duplication_ratio:.2f}%")

    print("\n--- 🔍 상세 분석 ---")
    # 가장 많이 중복된 ID 상위 3개 출력
    sorted_ids = sorted(id_occurrences.items(), key=lambda x: len(x[1]), reverse=True)
    
    for orig_id, files in sorted_ids[:3]:
        print(f"원본 ID '{orig_id}'가 {len(files)}개의 파일에서 공통으로 사용됨.")
        print(f"  예시 파일들: {files[:3]}")

    print("\n💡 결론:")
    if duplication_ratio > 10:
        print("결과: 이미지 ID가 각 파일마다 중복(예: 전부 0번)되어 있습니다.")
        print("조치: 'image_id' 대신 'file_name'을 기준으로 새로운 고유 ID를 생성해야 합니다.")
    else:
        print("결과: ID 중복 문제가 아닐 수 있습니다. 데이터 타입을 다시 확인하세요.")

if __name__ == "__main__":
    analyze_json_ids()
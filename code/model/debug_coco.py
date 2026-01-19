import json
import os

def find_bad_bbox(json_path):
    print(f"🔍 불량 데이터 검사 시작: {json_path}")
    
    if not os.path.exists(json_path):
        print(f"❌ 에러: 파일을 찾을 수 없습니다 -> {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    images = {img['id']: img['file_name'] for img in data.get('images', [])}
    annotations = data.get('annotations', [])
    
    bad_count = 0
    print("\n--- 🚨 검출된 불량 데이터 목록 ---")
    
    for ann in annotations:
        bbox = ann.get('bbox', [])
        
        # bbox가 리스트가 아니거나, 요소가 4개가 아닌 경우 탐지
        if not isinstance(bbox, list) or len(bbox) != 4:
            bad_count += 1
            image_id = ann.get('image_id')
            file_name = images.get(image_id, "Unknown")
            
            print(f"[{bad_count}] 파일명: {file_name}")
            print(f"    - Image ID: {image_id}")
            print(f"    - 잘못된 BBox 내용: {bbox} (요소 개수: {len(bbox)})")
            
            if bad_count >= 10: # 너무 많으면 상위 10개만 출력
                print("\n⚠️ 불량 데이터가 너무 많아 상위 10개만 표시합니다.")
                break

    if bad_count == 0:
        print("✅ 모든 BBox 데이터가 정상(4개 요소)입니다.")
    else:
        print(f"\n❌ 총 {bad_count}개의 불량 데이터가 발견되었습니다.")

if __name__ == "__main__":
    # 경로를 확인하세요
    target_json = "/Users/ganghyeon-u/Desktop/강원대 부트캠프(중급)/code/model/dataset/annotations/train_coco.json"
    find_bad_bbox(target_json)
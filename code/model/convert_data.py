import json
import os
from collections import defaultdict
from typing import Dict, List, Any
from pathlib import Path

# 원본 데이터 경로
label_name = "/Users/ganghyeon-u/Downloads/166.약품식별 인공지능 개발을 위한 경구약제 이미지 데이터/01.데이터/1.Training/라벨링데이터/경구약제조합 5000종/"

def find_all_json_files(base_path: str) -> List[str]:
    json_files = []
    for dirpath, _, filenames in os.walk(base_path):
        for filename in filenames:
            if filename.endswith(".json") and not filename.startswith("._"):
                json_files.append(os.path.join(dirpath, filename))
    return json_files

def main():
    print("🔍 모든 JSON 파일 찾는 중...")
    json_files = find_all_json_files(label_name)
    print(f"✅ 발견된 JSON 파일: {len(json_files)}개")

    coco_data = {
        "images": [],
        "annotations": [],
        "categories": []
    }
    
    drug_to_id = {}
    drug_mapping_dict = {}
    category_counter = 0
    image_counter = 1
    ann_counter = 1

    print("🚀 데이터 변환 및 매칭 시작...")
    for i, json_file in enumerate(json_files):
        if (i + 1) % 1000 == 0:
            print(f"처리 중: {i + 1}/{len(json_files)}...")

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 1. 이미지 정보 처리
            for img in data.get('images', []):
                file_name = img.get('file_name')
                dl_name = img.get('dl_name') # 약품명
                item_seq = img.get('item_seq')

                # 카테고리(약품명) 등록
                if dl_name not in drug_to_id:
                    drug_to_id[dl_name] = category_counter
                    drug_mapping_dict[str(category_counter)] = {"code": str(item_seq), "name": dl_name}
                    coco_data["categories"].append({
                        "id": category_counter,
                        "name": dl_name,
                        "supercategory": "drug"
                    })
                    category_counter += 1

                # 새 고유 이미지 정보 생성
                new_img_obj = {
                    "id": image_counter,
                    "file_name": file_name,
                    "width": img.get('width'),
                    "height": img.get('height')
                }
                coco_data["images"].append(new_img_obj)

                # 2. 어노테이션 정보 처리 (현재 파일 내의 모든 어노테이션을 이 이미지 ID에 할당)
                # 원본 파일들은 이미지 1개당 파일 1개 구조이므로 이 방식이 가장 정확합니다.
                for ann in data.get('annotations', []):
                    coco_data["annotations"].append({
                        "id": ann_counter,
                        "image_id": image_counter, # 위에서 새로 만든 고유 ID 사용
                        "category_id": drug_to_id[dl_name],
                        "bbox": ann.get('bbox'),
                        "area": ann.get('bbox')[2] * ann.get('bbox')[3],
                        "iscrowd": 0
                    })
                    ann_counter += 1
                
                image_counter += 1

        except Exception as e:
            # print(f"Error in {json_file}: {e}")
            continue

    # 결과 저장
    output_dir = os.getcwd()
    with open(os.path.join(output_dir, "train_coco.json"), 'w', encoding='utf-8') as f:
        json.dump(coco_data, f, ensure_ascii=False, indent=2)
    with open(os.path.join(output_dir, "drug_mapping.json"), 'w', encoding='utf-8') as f:
        json.dump(drug_mapping_dict, f, ensure_ascii=False, indent=2)

    print(f"\n✨ 변환 완료!")
    print(f"이미지: {len(coco_data['images'])}개 / 어노테이션: {len(coco_data['annotations'])}개")

if __name__ == "__main__":
    main()
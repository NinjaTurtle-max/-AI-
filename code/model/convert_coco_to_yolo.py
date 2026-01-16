"""
COCO 포맷을 YOLO 포맷으로 변환하는 스크립트 (최종 버전)
- 오염 데이터(BBox 5개 등) 자동 스킵 및 요약 보고
- 이미지 복사 생략 (이미 완료됨)
"""
import json
import os
from pathlib import Path
from typing import Dict
from collections import defaultdict


def convert_coco_to_yolo(
    coco_json_path: str,
    output_labels_dir: str,
    class_mapping: Dict[int, int] = None
):
    # COCO JSON 로드
    print(f"📂 Loading COCO JSON: {os.path.basename(coco_json_path)}...")
    with open(coco_json_path, 'r', encoding='utf-8') as f:
        coco_data = json.load(f)
    
    images = {img['id']: img for img in coco_data['images']}
    annotations = coco_data['annotations']
    
    # 이미지 ID별 annotation 그룹화
    image_annotations = defaultdict(list)
    for ann in annotations:
        image_annotations[ann['image_id']].append(ann)
    
    os.makedirs(output_labels_dir, exist_ok=True)
    
    converted_count = 0
    skipped_files = [] # 건너뛴 불량 데이터 목록
    total_skipped_anns = 0

    for image_id, image_info in images.items():
        file_name = image_info['file_name']
        img_width = image_info['width']
        img_height = image_info['height']
        
        # 확장자를 제외한 파일명 + .txt
        label_file_name = Path(file_name).stem + '.txt'
        label_path = os.path.join(output_labels_dir, label_file_name)
        
        anns = image_annotations.get(image_id, [])
        yolo_lines = []
        
        for ann in anns:
            bbox = ann.get('bbox', [])
            
            # 🚨 [중요] 데이터 정합성 체크: bbox 요소가 정확히 4개가 아니면 스킵
            if not isinstance(bbox, list) or len(bbox) != 4:
                skipped_files.append(f"{file_name} (BBox: {bbox})")
                total_skipped_anns += 1
                continue
            
            x, y, w, h = bbox
            
            # 유효하지 않은 박스 크기 스킵
            if w <= 0 or h <= 0:
                continue
            
            # YOLO 정규화 (0~1 사이 값)
            center_x = (x + w / 2) / img_width
            center_y = (y + h / 2) / img_height
            norm_width = w / img_width
            norm_height = h / img_height
            
            class_id = ann.get('category_id')
            if class_mapping:
                class_id = class_mapping.get(class_id, class_id)
            
            # YOLO 형식: class_id x_center y_center width height
            yolo_lines.append(f"{class_id} {center_x:.6f} {center_y:.6f} {norm_width:.6f} {norm_height:.6f}\n")
        
        # 라벨 파일 쓰기
        with open(label_path, 'w') as f:
            f.writelines(yolo_lines)
        
        converted_count += 1
        if converted_count % 5000 == 0:
            print(f"   ... {converted_count} images processed")
    
    # 보고서 출력
    print(f"\n" + "="*55)
    print(f"✅ Conversion Summary: {os.path.basename(coco_json_path)}")
    print(f"   - Successfully converted: {converted_count} images")
    print(f"   - Invalid annotations skipped: {total_skipped_anns}")
    if skipped_files:
        print(f"   - First 3 skipped files: {skipped_files[:3]}")
    print("="*55 + "\n")


def create_yolo_dataset_structure(
    base_dir: str,
    train_coco_json: str,
    val_coco_json: str
):
    base_path = Path(base_dir)
    
    # 라벨 저장 경로 설정
    train_labels_dir = base_path / "train" / "labels"
    val_labels_dir = base_path / "val" / "labels"
    
    print("🚀 [1/2] Converting Train Labels...")
    convert_coco_to_yolo(train_coco_json, str(train_labels_dir))
    
    print("🚀 [2/2] Converting Val Labels...")
    convert_coco_to_yolo(val_coco_json, str(val_labels_dir))


if __name__ == "__main__":
    # 1. 경로 설정 (사용자님의 Mac 환경 기준)
    base_path = Path("/Users/ganghyeon-u/Desktop/강원대 부트캠프(중급)/code/model/dataset")
    
    train_json = base_path / "annotations" / "train_coco.json"
    val_json = base_path / "annotations" / "val_coco.json"
    
    # 최종 결과물이 저장될 yolo_format 폴더
    yolo_output_dir = base_path / "yolo_format"
    
    if not train_json.exists():
        print(f"❌ Error: {train_json} 파일을 찾을 수 없습니다. split_dataset을 먼저 실행하세요.")
        exit(1)
    
    # 2. 실행
    create_yolo_dataset_structure(
        base_dir=str(yolo_output_dir),
        train_coco_json=str(train_json),
        val_coco_json=str(val_json)
    )
    
    print(f"✨ 모든 라벨 변환이 완료되었습니다!")
    print(f"📂 결과 폴더: {yolo_output_dir}")
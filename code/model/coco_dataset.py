"""
COCO 포맷 데이터셋을 Ultralytics RT-DETR에서 사용할 수 있도록 변환하는 유틸리티
"""
import json
import os
from pathlib import Path
from typing import Dict, List
import yaml


def create_ultralytics_dataset_yaml(
    coco_train_json: str,
    coco_val_json: str,
    images_dir: str,
    output_yaml: str,
    num_classes: int = 118
):
    """
    COCO JSON 파일들을 기반으로 Ultralytics용 YAML 파일 생성
    
    Args:
        coco_train_json: Train COCO JSON 파일 경로
        coco_val_json: Val COCO JSON 파일 경로
        images_dir: 이미지 디렉토리 경로
        output_yaml: 출력 YAML 파일 경로
        num_classes: 클래스 개수
    """
    # COCO JSON에서 카테고리 정보 로드
    with open(coco_train_json, 'r', encoding='utf-8') as f:
        train_data = json.load(f)
    
    categories = train_data['categories']
    categories = sorted(categories, key=lambda x: x['id'])
    
    # 클래스 이름 리스트 생성
    class_names = [cat['name'] for cat in categories]
    
    # YAML 데이터 생성
    yaml_data = {
        'path': str(Path(images_dir).parent.absolute()),
        'train': f"images",  # images 폴더
        'val': f"images",     # images 폴더 (동일)
        'nc': num_classes,
        'names': {i: name for i, name in enumerate(class_names)}
    }
    
    # YAML 파일 저장
    with open(output_yaml, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Created Ultralytics dataset YAML: {output_yaml}")
    print(f"   Classes: {num_classes}")
    print(f"   Images directory: {images_dir}")


class COCODataset:
    """
    COCO 포맷 데이터셋을 로드하고 Ultralytics 형식으로 변환하는 클래스
    """
    
    def __init__(self, coco_json_path: str, images_dir: str):
        """
        Args:
            coco_json_path: COCO JSON 파일 경로
            images_dir: 이미지 디렉토리 경로
        """
        self.coco_json_path = coco_json_path
        self.images_dir = images_dir
        
        # COCO 데이터 로드
        with open(coco_json_path, 'r', encoding='utf-8') as f:
            self.coco_data = json.load(f)
        
        self.images = {img['id']: img for img in self.coco_data['images']}
        self.annotations = self.coco_data['annotations']
        self.categories = {cat['id']: cat for cat in self.coco_data['categories']}
        
        # 이미지 ID별 annotation 그룹화
        self.image_annotations = {}
        for ann in self.annotations:
            img_id = ann['image_id']
            if img_id not in self.image_annotations:
                self.image_annotations[img_id] = []
            self.image_annotations[img_id].append(ann)
    
    def get_image_path(self, image_id: int) -> str:
        """이미지 ID로 이미지 파일 경로 반환"""
        if image_id not in self.images:
            return None
        image_info = self.images[image_id]
        return os.path.join(self.images_dir, image_info['file_name'])
    
    def get_annotations(self, image_id: int) -> List[Dict]:
        """이미지 ID로 해당 이미지의 annotation 리스트 반환"""
        return self.image_annotations.get(image_id, [])
    
    def convert_to_yolo_format(self, image_id: int) -> List[List[float]]:
        """
        COCO bbox를 YOLO 형식 (normalized center x, center y, width, height)으로 변환
        
        Returns:
            [[class_id, x_center, y_center, width, height], ...] 리스트
        """
        if image_id not in self.images:
            return []
        
        image_info = self.images[image_id]
        img_width = image_info['width']
        img_height = image_info['height']
        
        yolo_annotations = []
        for ann in self.get_annotations(image_id):
            # COCO bbox: [x, y, width, height] (top-left corner)
            bbox = ann['bbox']
            x, y, w, h = bbox
            
            # YOLO 형식으로 변환: [center_x, center_y, width, height] (normalized)
            center_x = (x + w / 2) / img_width
            center_y = (y + h / 2) / img_height
            norm_width = w / img_width
            norm_height = h / img_height
            
            class_id = ann['category_id']
            yolo_annotations.append([class_id, center_x, center_y, norm_width, norm_height])
        
        return yolo_annotations


if __name__ == "__main__":
    # 예시 사용법
    script_dir = Path(__file__).parent
    dataset_dir = script_dir / "dataset"
    
    train_json = dataset_dir / "annotations" / "train_coco.json"
    val_json = dataset_dir / "annotations" / "val_coco.json"
    images_dir = dataset_dir / "images"
    output_yaml = script_dir / "dataset.yaml"
    
    if train_json.exists() and val_json.exists():
        create_ultralytics_dataset_yaml(
            coco_train_json=str(train_json),
            coco_val_json=str(val_json),
            images_dir=str(images_dir),
            output_yaml=str(output_yaml),
            num_classes=118
        )
    else:
        print("COCO JSON files not found. Please run train_val_split.py first.")

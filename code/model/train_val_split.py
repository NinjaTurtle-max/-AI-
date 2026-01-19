import json
import os
import random
import shutil
from pathlib import Path

def split_coco_dataset_with_images(
    coco_json_path: str,
    source_images_dir: str,  # 이미지가 다 모여 있는 경로
    output_base_dir: str,
    val_ratio: float = 0.15,
    random_seed: int = 42
):
    random.seed(random_seed)
    
    # 1. COCO JSON 로드
    print(f"📦 Loading COCO JSON: {coco_json_path}...")
    with open(coco_json_path, 'r', encoding='utf-8') as f:
        coco_data = json.load(f)
    
    images = coco_data.get('images', [])
    annotations = coco_data.get('annotations', [])
    categories = coco_data.get('categories', [])
    
    # 2. 이미지 ID 리스트 분할
    image_ids = [img['id'] for img in images]
    random.shuffle(image_ids)
    split_idx = int(len(image_ids) * (1 - val_ratio))
    train_ids = set(image_ids[:split_idx])
    val_ids = set(image_ids[split_idx:])
    
    # 3. 출력 경로 설정
    train_img_out = Path(output_base_dir) / "images" / "train"
    val_img_out = Path(output_base_dir) / "images" / "val"
    ann_out = Path(output_base_dir) / "annotations"
    
    for d in [train_img_out, val_img_out, ann_out]:
        d.mkdir(parents=True, exist_ok=True)

    # 4. 이미지 복사 및 데이터 처리
    def process_data(target_ids, split_name, target_dir):
        split_images = [img for img in images if img['id'] in target_ids]
        split_anns = [ann for ann in annotations if ann['image_id'] in target_ids]
        
        print(f"🚀 [{split_name}] 이미지 복사 시작 (대상: {len(split_images)}개)...")
        copied_count = 0
        missing_count = 0
        
        for img in split_images:
            file_name = img['file_name']
            src_path = Path(source_images_dir) / file_name
            dst_path = target_dir / file_name
            
            if src_path.exists():
                if not dst_path.exists():
                    shutil.copy2(src_path, dst_path)
                copied_count += 1
            else:
                missing_count += 1
        
        print(f"✅ [{split_name}] 완료: {copied_count}개 복사 (누락: {missing_count}개)")
        return split_images, split_anns

    # 5. 실행
    train_imgs, train_anns = process_data(train_ids, "Train", train_img_out)
    val_imgs, val_anns = process_data(val_ids, "Val", val_img_out)

    # 6. JSON 저장
    with open(ann_out / "train_coco.json", 'w', encoding='utf-8') as f:
        json.dump({"images": train_imgs, "annotations": train_anns, "categories": categories}, f, ensure_ascii=False, indent=2)
    with open(ann_out / "val_coco.json", 'w', encoding='utf-8') as f:
        json.dump({"images": val_imgs, "annotations": val_anns, "categories": categories}, f, ensure_ascii=False, indent=2)

    print(f"\n✨ 모든 작업 완료! 총 {len(images)}장 중 {copied_count + copied_count}장 처리됨.")

if __name__ == "__main__":
    INPUT_COCO = "/Users/ganghyeon-u/Desktop/강원대 부트캠프(중급)/code/model/train_coco.json"
    
    # 이미지가 다 모여 있다고 하신 바로 그 경로!
    SOURCE_IMG_DIR = "/Users/ganghyeon-u/Desktop/강원대 부트캠프(중급)/code/model/dataset 오후 4.31.14/images"
    
    OUTPUT_BASE = "/Users/ganghyeon-u/Desktop/강원대 부트캠프(중급)/code/model/dataset"
    
    split_coco_dataset_with_images(INPUT_COCO, SOURCE_IMG_DIR, OUTPUT_BASE)
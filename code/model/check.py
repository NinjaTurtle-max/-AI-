import os
from pathlib import Path

def check_yolo_dataset(base_path, split_name):
    print(f"\n🔍 [{split_name} 데이터셋 검수 시작]")
    
    # 경로 설정
    split_path = Path(base_path) / split_name
    image_dir = split_path / "images"
    label_dir = split_path / "labels"
    
    if not image_dir.exists() or not label_dir.exists():
        print(f"❌ 에러: {split_name} 폴더 내에 images 또는 labels 폴더가 없습니다.")
        return

    # 파일 목록 가져오기
    image_files = sorted([f.stem for f in image_dir.glob("*") if f.suffix.lower() in ['.png', '.jpg', '.jpeg']])
    label_files = sorted([f.stem for f in label_dir.glob("*.txt")])
    
    image_set = set(image_files)
    label_set = set(label_files)
    
    # 1. 개수 비교
    print(f"📊 통계:")
    print(f"   - 발견된 이미지 수: {len(image_set)}개")
    print(f"   - 발견된 라벨 수: {len(label_set)}개")
    
    # 2. 매칭 확인 (1:1 매칭)
    missing_labels = image_set - label_set
    missing_images = label_set - image_set
    
    if not missing_labels and not missing_images:
        print("   ✅ 이미지와 라벨이 1:1로 완벽하게 매칭됩니다.")
    else:
        if missing_labels:
            print(f"   ⚠️ 라벨이 없는 이미지 (첫 5개): {list(missing_labels)[:5]}")
        if missing_images:
            print(f"   ⚠️ 이미지가 없는 라벨 (첫 5개): {list(missing_images)[:5]}")

    # 3. 라벨 내용 검수 (비어있는지, 형식은 맞는지)
    empty_labels = 0
    sample_content = ""
    
    for txt_file in label_dir.glob("*.txt"):
        if os.path.getsize(txt_file) == 0:
            empty_labels += 1
        elif not sample_content:
            with open(txt_file, 'r') as f:
                sample_content = f.readline().strip()

    print(f"📝 내용 검사:")
    if empty_labels == 0:
        print(f"   ✅ 모든 라벨 파일에 데이터가 포함되어 있습니다.")
    else:
        print(f"   🚨 경고: {empty_labels}개의 라벨 파일이 비어있습니다 (Background 이미지).")
    
    if sample_content:
        print(f"   📍 라벨 내용 샘플: {sample_content} (정상: 'class x_center y_center width height')")
    else:
        print(f"   🚨 라벨 내용을 확인할 수 없습니다.")

if __name__ == "__main__":
    # 검수할 yolo_format 최상위 경로
    YOLO_ROOT = "/Users/ganghyeon-u/Desktop/강원대 부트캠프(중급)/code/model/dataset/yolo_format"
    
    check_yolo_dataset(YOLO_ROOT, "train")
    check_yolo_dataset(YOLO_ROOT, "val")
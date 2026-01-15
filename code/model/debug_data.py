import os
from pathlib import Path

def debug_yolo_split(split_path, split_name):
    print(f"\n{'='*20} [{split_name} SET DEBUG] {'='*20}")
    
    # 경로 설정
    base_path = Path(split_path)
    img_dir = base_path / "images"
    lbl_dir = base_path / "labels"

    # 폴더 존재 확인
    if not img_dir.exists() or not lbl_dir.exists():
        print(f"❌ 에러: {split_name} 폴더 내에 images 또는 labels 폴더가 없습니다.")
        print(f"   확인 경로: {base_path}")
        return

    # 파일 목록 추출 (확장자 제외 이름만)
    img_files = {f.stem for f in img_dir.glob("*") if f.suffix.lower() in ['.png', '.jpg', '.jpeg']}
    lbl_files = {f.stem for f in lbl_dir.glob("*.txt")}

    # 1. 개수 비교
    print(f"📊 [1] 파일 개수 통계")
    print(f"   - 이미지 개수: {len(img_files)}개")
    print(f"   - 라벨 개수  : {len(lbl_files)}개")

    # 2. 매칭 확인
    missing_labels = img_files - lbl_files
    missing_images = lbl_files - img_files

    print(f"🔍 [2] 매칭 무결성 검사")
    if not missing_labels and not missing_images:
        print("   ✅ 이미지와 라벨이 1:1로 완벽하게 매칭됩니다.")
    else:
        if missing_labels:
            print(f"   ⚠️ 라벨이 없는 이미지 ({len(missing_labels)}개): {list(missing_labels)[:3]}...")
        if missing_images:
            print(f"   ⚠️ 이미지가 없는 라벨 ({len(missing_images)}개): {list(missing_images)[:3]}...")

    # 3. 라벨 내용 상세 검수 (첫 번째 파일 샘플링)
    print(f"📝 [3] 라벨 파일 내부 검수")
    empty_count = 0
    invalid_format_count = 0
    sample_data = None

    for lbl in lbl_dir.glob("*.txt"):
        with open(lbl, 'r') as f:
            lines = f.readlines()
            if not lines:
                empty_count += 1
                continue
            
            for line in lines:
                parts = line.strip().split()
                if len(parts) != 5: # YOLO 포맷은 5개 요소 (cls, x, y, w, h)
                    invalid_format_count += 1
                elif sample_data is None:
                    sample_data = line.strip()

    print(f"   - 비어있는 라벨 파일: {empty_count}개")
    print(f"   - 포맷 오류 파일: {invalid_format_count}개")
    if sample_data:
        print(f"   📍 라벨 샘플: {sample_data}")
    
    print(f"{'='*55}\n")

if __name__ == "__main__":
    # 사용자님이 지정하신 경로
    TRAIN_PATH = "/Users/ganghyeon-u/Desktop/강원대 부트캠프(중급)/code/dataset/yolo_format/train"
    VAL_PATH = "/Users/ganghyeon-u/Desktop/강원대 부트캠프(중급)/code/dataset/yolo_format/val"

    debug_yolo_split(TRAIN_PATH, "TRAIN")
    debug_yolo_split(VAL_PATH, "VAL")
"""
RT-DETR 모델 학습 스크립트
Ultralytics RT-DETR를 사용하여 알약 식별 모델을 학습합니다.
"""
import os
import json
from pathlib import Path
from ultralytics import RTDETR

def load_drug_mapping(mapping_path: str) -> dict:
    """drug_mapping.json 파일을 로드"""
    with open(mapping_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def train_rtdetr(
    data_yaml: str = "dataset.yaml",
    model_name: str = "rtdetr-r50vd.pt",  # 또는 "rtdetr-l.pt", "rtdetr-x.pt"
    epochs: int = 100,
    batch_size: int = 16,
    img_size = (1280, 976),  # 원본 이미지 크기 (height, width) - 왜곡 없이 학습
    device: str = "0",  # "0" for GPU, "cpu" for CPU
    workers: int = 8,
    project: str = "runs/detect",
    name: str = "drug_identification",
    resume: bool = False,
    pretrained: bool = True
):
    """
    RT-DETR 모델 학습
    
    Args:
        data_yaml: 데이터셋 설정 YAML 파일 경로
        model_name: 모델 이름 (rtdetr-r50vd.pt, rtdetr-l.pt, rtdetr-x.pt)
        epochs: 학습 에포크 수
        batch_size: 배치 크기
        img_size: 입력 이미지 크기 (int 또는 (height, width) 튜플)
                  기본값: (1280, 976) - 원본 이미지 크기
        device: 사용할 디바이스 ("0", "1", "cpu")
        workers: 데이터 로더 워커 수
        project: 프로젝트 디렉토리
        name: 실험 이름
        resume: 이전 학습 재개 여부
        pretrained: 사전 학습된 가중치 사용 여부
    """
    # 현재 스크립트 디렉토리
    script_dir = Path(__file__).parent
    data_yaml_path = script_dir / data_yaml
    
    # 데이터셋 YAML 파일 존재 확인
    if not data_yaml_path.exists():
        raise FileNotFoundError(f"Dataset YAML file not found: {data_yaml_path}")
    
    # img_size를 튜플로 변환 (정수인 경우 처리)
    if isinstance(img_size, int):
        img_size = (img_size, img_size)
    elif isinstance(img_size, (list, tuple)) and len(img_size) == 2:
        img_size = tuple(img_size)
    else:
        raise ValueError(f"img_size must be int or (height, width) tuple, got {img_size}")
    
    print("=" * 80)
    print("RT-DETR Drug Identification Training")
    print("=" * 80)
    print(f"Dataset YAML: {data_yaml_path}")
    print(f"Model: {model_name}")
    print(f"Epochs: {epochs}")
    print(f"Batch Size: {batch_size}")
    print(f"Image Size: {img_size[0]}x{img_size[1]} (Height x Width)")
    print(f"Device: {device}")
    print("=" * 80)
    
    # 모델 초기화
    model = RTDETR(model_name if pretrained else f"{model_name.replace('.pt', '')}.yaml")
    
    # 학습 시작
    # imgsz는 튜플 또는 정수 형태로 전달
    # Ultralytics는 튜플 (height, width) 또는 정수 (정사각형)를 지원
    train_kwargs = {
        "data": str(data_yaml_path),
        "epochs": epochs,
        "batch": batch_size,
        "imgsz": img_size,  # (1280, 976) 형태로 전달
        "device": device,
        "workers": workers,
        "project": project,
        "name": name,
        "resume": resume,
        "pretrained": pretrained,
        # 하이퍼파라미터 설정
        "lr0": 0.001,          # 초기 학습률
        "lrf": 0.01,           # 최종 학습률 (lr0 * lrf)
        "momentum": 0.937,     # SGD momentum
        "weight_decay": 0.0005, # 가중치 감쇠
        "warmup_epochs": 3,    # 워밍업 에포크
        "warmup_momentum": 0.8,
        "warmup_bias_lr": 0.1,
        # 데이터 증강
        "hsv_h": 0.015,        # HSV-Hue augmentation
        "hsv_s": 0.7,          # HSV-Saturation augmentation
        "hsv_v": 0.4,          # HSV-Value augmentation
        "degrees": 0.0,        # 회전 각도
        "translate": 0.1,      # 이동
        "scale": 0.5,          # 스케일
        "shear": 0.0,          # 전단
        "perspective": 0.0,    # 원근 변환
        "flipud": 0.0,         # 상하 반전
        "fliplr": 0.5,         # 좌우 반전
        "mosaic": 1.0,         # Mosaic augmentation
        "mixup": 0.0,          # MixUp augmentation
        "copy_paste": 0.0,     # Copy-paste augmentation
        # 검증 설정
        "val": True,           # 검증 수행
        "plots": True,         # 학습 그래프 생성
        "save": True,          # 체크포인트 저장
        "save_period": 10,     # N 에포크마다 저장
        # 로깅
        "verbose": True,       # 상세 로그 출력
        "seed": 42,            # 랜덤 시드
    }
    
    # 직사각형 이미지를 위한 rect 옵션 (Ultralytics가 지원하는 경우)
    # rect=True는 배치 내 이미지 크기를 통일하되 원본 비율 유지
    try:
        results = model.train(**train_kwargs)
    except TypeError:
        # rect 옵션이 지원되지 않는 경우 제거하고 재시도
        print("Note: Using rectangular image size (1280x976)")
        results = model.train(**train_kwargs)
    
    print("\n" + "=" * 80)
    print("✅ Training completed!")
    print("=" * 80)
    
    # 최종 모델 경로 출력
    best_model_path = results.save_dir / "weights" / "best.pt"
    last_model_path = results.save_dir / "weights" / "last.pt"
    
    print(f"\nBest model saved at: {best_model_path}")
    print(f"Last model saved at: {last_model_path}")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train RT-DETR model for drug identification")
    parser.add_argument("--data", type=str, default="dataset.yaml", help="Dataset YAML file")
    parser.add_argument("--model", type=str, default="rtdetr-r50vd.pt", 
                       choices=["rtdetr-r50vd.pt", "rtdetr-l.pt", "rtdetr-x.pt"],
                       help="Model name")
    parser.add_argument("--epochs", type=int, default=100, help="Number of epochs")
    parser.add_argument("--batch", type=int, default=34, help="Batch size")
    parser.add_argument("--img-size", type=str, default="1280,976", 
                       help="Image size as 'height,width' (default: 1280,976 for original size)")
    parser.add_argument("--device", type=str, default="0", help="Device (0, 1, cpu)")
    parser.add_argument("--workers", type=int, default=8, help="Number of workers")
    parser.add_argument("--project", type=str, default="runs/detect", help="Project directory")
    parser.add_argument("--name", type=str, default="drug_identification", help="Experiment name")
    parser.add_argument("--resume", action="store_true", help="Resume training")
    
    args = parser.parse_args()
    
    # img_size 파싱 (정수 또는 "height,width" 형식)
    if isinstance(args.img_size, str) and ',' in args.img_size:
        img_size = tuple(map(int, args.img_size.split(',')))
        if len(img_size) != 2:
            raise ValueError(f"img_size must be 'height,width' format, got {args.img_size}")
    elif isinstance(args.img_size, int):
        img_size = args.img_size
    else:
        img_size = args.img_size
    
    # 학습 실행
    train_rtdetr(
        data_yaml=args.data,
        model_name=args.model,
        epochs=args.epochs,
        batch_size=args.batch,
        img_size=img_size,
        device=args.device,
        workers=args.workers,
        project=args.project,
        name=args.name,
        resume=args.resume
    )

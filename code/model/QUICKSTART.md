# 🚀 빠른 시작 가이드

SSH 서버에서 RT-DETR 모델을 학습시키는 단계별 가이드입니다.

## 1단계: 환경 확인 및 설치

```bash
# Python 버전 확인 (3.8+ 필요)
python3 --version

# 필요한 패키지 설치
pip install ultralytics torch torchvision opencv-python numpy pyyaml

# 또는 requirements.txt 사용
pip install -r requirements.txt

# GPU 확인 (CUDA 사용 가능한지)
python3 -c "import torch; print(torch.cuda.is_available())"
```

## 2단계: 데이터셋 준비

현재 구조:
```
code/model/
├── train_coco.json      # 전체 데이터셋
├── dataset/
│   └── images/          # 모든 이미지 파일
└── drug_mapping.json    # 약품 매핑
```

### 2-1. Train/Val 분할

```bash
cd code/model
python3 train_val_split.py
```

**출력 예시:**
```
Loading COCO JSON from ...
Total images: 50000
Total annotations: 50000
Total categories: 118

Split results:
  Train images: 42500 (85.0%)
  Val images: 7500 (15.0%)

✅ Dataset split completed!
```

이제 다음 파일이 생성됩니다:
- `dataset/annotations/train_coco.json`
- `dataset/annotations/val_coco.json`

## 3단계: COCO → YOLO 변환 (필수)

Ultralytics RT-DETR은 YOLO 포맷을 사용하므로 COCO를 변환해야 합니다:

```bash
python3 convert_coco_to_yolo.py
```

이 스크립트는:
- `dataset/yolo_format/train/` 폴더 생성
- `dataset/yolo_format/val/` 폴더 생성
- 각 이미지에 대한 `.txt` 라벨 파일 생성

**중요:** 이미지 파일을 복사하거나 심볼릭 링크를 생성해야 합니다:

```bash
# 이미지 복사 (또는 심볼릭 링크)
cp -r dataset/images/* dataset/yolo_format/train/images/
cp -r dataset/images/* dataset/yolo_format/val/images/

# 또는 심볼릭 링크 (디스크 공간 절약)
ln -s $(pwd)/dataset/images/* dataset/yolo_format/train/images/
ln -s $(pwd)/dataset/images/* dataset/yolo_format/val/images/
```

## 4단계: dataset.yaml 수정

`dataset.yaml` 파일을 열어서 YOLO 형식 경로로 수정:

```yaml
path: ./dataset/yolo_format
train: train/images
val: val/images
nc: 118
names:
  # ... (이미 작성되어 있음)
```

## 5단계: 모델 학습 시작

### 기본 학습 (GPU 사용)

```bash
python3 train_rtdetr.py \
    --data dataset.yaml \
    --model rtdetr-r50vd.pt \
    --epochs 100 \
    --batch 16 \
    --device 0
```

### CPU만 사용하는 경우

```bash
python3 train_rtdetr.py \
    --data dataset.yaml \
    --model rtdetr-r50vd.pt \
    --epochs 100 \
    --batch 4 \
    --device cpu \
    --workers 4
```

### GPU 메모리가 부족한 경우

```bash
python3 train_rtdetr.py \
    --data dataset.yaml \
    --model rtdetr-r50vd.pt \
    --epochs 100 \
    --batch 8 \          # 배치 크기 줄이기
    --img-size 512 \     # 이미지 크기 줄이기
    --device 0
```

## 6단계: 학습 모니터링

학습 중 터미널에 다음과 같은 정보가 출력됩니다:

```
Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
  1/100      4.2G      1.234      2.456      0.789        1234        640
  2/100      4.2G      1.123      2.345      0.678        1234        640
  ...
```

**중요:** SSH 연결이 끊어지면 학습이 중단됩니다. `screen` 또는 `tmux` 사용 권장:

```bash
# screen 사용
screen -S training
python3 train_rtdetr.py --data dataset.yaml --model rtdetr-r50vd.pt --epochs 100 --batch 16 --device 0
# Ctrl+A, D로 detach

# 다시 연결
screen -r training

# tmux 사용
tmux new -s training
python3 train_rtdetr.py --data dataset.yaml --model rtdetr-r50vd.pt --epochs 100 --batch 16 --device 0
# Ctrl+B, D로 detach

# 다시 연결
tmux attach -t training
```

## 7단계: 학습 완료 후 추론 테스트

학습이 완료되면 `runs/detect/drug_identification/weights/best.pt` 파일이 생성됩니다.

### 단일 이미지 테스트

```bash
python3 inference.py \
    --model runs/detect/drug_identification/weights/best.pt \
    --image dataset/images/example.png \
    --mapping drug_mapping.json \
    --conf 0.25 \
    --visualize
```

**출력 예시:**
```
Predicting on image: dataset/images/example.png

Found 1 detections:

  Detection 1:
    Class ID: 42
    Drug Code: 200710817
    Drug Name: 맥시부펜이알정 300mg
    Confidence: 0.9234
    BBox: [123.4, 456.7, 234.5, 567.8]
```

## 🔧 문제 해결

### CUDA out of memory
```bash
# 배치 크기 줄이기
--batch 8  # 또는 4

# 이미지 크기 줄이기
--img-size 512
```

### 데이터셋을 찾을 수 없음
```bash
# dataset.yaml의 path가 올바른지 확인
cat dataset.yaml | grep "path:"

# 이미지 파일이 있는지 확인
ls dataset/yolo_format/train/images/ | head -5
ls dataset/yolo_format/train/labels/ | head -5
```

### 학습이 너무 느림
- GPU 사용 확인: `nvidia-smi`
- `--workers` 수 조정 (기본값 8)
- 더 작은 모델 사용: `rtdetr-r50vd.pt`

## 📊 학습 체크포인트

학습 중 다음 위치에 체크포인트가 저장됩니다:
- `runs/detect/drug_identification/weights/best.pt` - 최고 성능 모델
- `runs/detect/drug_identification/weights/last.pt` - 마지막 체크포인트
- `runs/detect/drug_identification/results.png` - 학습 그래프

## 🎯 다음 단계

1. 학습 완료 후 `best.pt` 모델 사용
2. 실제 이미지로 추론 테스트
3. 필요시 더 많은 에포크로 재학습
4. 다른 모델 크기 시도 (`rtdetr-l.pt`, `rtdetr-x.pt`)

---

**Happy Training! 🚀**

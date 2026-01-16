# RT-DETR 알약 식별 AI 학습 가이드

이 프로젝트는 RT-DETR (Real-Time DEtection TRansformer) 모델을 사용하여 알약 식별 AI를 학습시키는 전체 파이프라인을 제공합니다.

## 📁 프로젝트 구조

```
code/model/
├── dataset/
│   ├── images/              # 모든 이미지 파일 (.png)
│   └── annotations/
│       ├── train_coco.json  # Train 데이터셋 (COCO 포맷)
│       └── val_coco.json   # Val 데이터셋 (COCO 포맷)
├── train_coco.json          # 원본 전체 데이터셋 (COCO 포맷)
├── drug_mapping.json        # 약품 ID → 약품명 매핑 (118개 클래스)
├── dataset.yaml             # 데이터셋 설정 파일
├── train_val_split.py       # Train/Val 분할 스크립트
├── train_rtdetr.py          # RT-DETR 학습 스크립트
├── inference.py             # 추론 및 매핑 테스트 스크립트
├── coco_dataset.py          # COCO 데이터셋 유틸리티
├── convert_coco_to_yolo.py  # COCO → YOLO 변환 스크립트
└── README.md                # 이 파일
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# Python 3.8+ 필요
pip install ultralytics torch torchvision
# 또는
pip install -r requirements.txt
```

### 2. 데이터셋 준비

이미 `train_coco.json`과 `dataset/images/` 폴더가 준비되어 있다고 가정합니다.

#### 2-1. Train/Val 분할

```bash
python train_val_split.py
```

이 스크립트는:
- `train_coco.json`을 읽어서
- 85%는 train, 15%는 val로 분할
- `dataset/annotations/train_coco.json`과 `dataset/annotations/val_coco.json` 생성

**출력:**
```
Loading COCO JSON from ...
Total images: XXXX
Total annotations: XXXX
Total categories: 118

Split results:
  Train images: XXXX (85.0%)
  Val images: XXXX (15.0%)

✅ Dataset split completed!
```

### 3. 데이터셋 설정 확인

`dataset.yaml` 파일이 올바르게 설정되어 있는지 확인하세요:
- `nc: 118` (클래스 개수)
- `path`, `train`, `val` 경로가 올바른지 확인

### 4. 모델 학습

#### 기본 학습 (권장)

```bash
python train_rtdetr.py \
    --data dataset.yaml \
    --model rtdetr-r50vd.pt \
    --epochs 100 \
    --batch 16 \
    --device 0
```

#### 고급 옵션

```bash
python train_rtdetr.py \
    --data dataset.yaml \
    --model rtdetr-l.pt \          # 더 큰 모델
    --epochs 200 \
    --batch 8 \                     # GPU 메모리가 부족하면 줄이기
    --img-size 640 \
    --device 0 \
    --workers 8 \
    --name drug_identification_exp1
```

#### 학습 재개 (중단된 학습 이어서 하기)

```bash
python train_rtdetr.py \
    --data dataset.yaml \
    --model runs/detect/drug_identification/weights/last.pt \
    --epochs 100 \
    --resume
```

### 5. 추론 및 테스트

#### 단일 이미지 추론

```bash
python inference.py \
    --model runs/detect/drug_identification/weights/best.pt \
    --image dataset/images/example.png \
    --mapping drug_mapping.json \
    --conf 0.25 \
    --visualize
```

#### 배치 추론

```bash
python inference.py \
    --model runs/detect/drug_identification/weights/best.pt \
    --image-dir dataset/images \
    --mapping drug_mapping.json \
    --conf 0.25 \
    --visualize \
    --output-dir results/visualizations
```

## 📊 하이퍼파라미터 추천

### 모델 선택

| 모델 | 크기 | 속도 | 정확도 | 메모리 |
|------|------|------|--------|--------|
| `rtdetr-r50vd.pt` | 중간 | 빠름 | 중간 | ~4GB |
| `rtdetr-l.pt` | 큼 | 보통 | 높음 | ~6GB |
| `rtdetr-x.pt` | 매우 큼 | 느림 | 매우 높음 | ~8GB |

**권장:** 처음에는 `rtdetr-r50vd.pt`로 시작

### 배치 크기

- **GPU 메모리 8GB:** `--batch 8` 또는 `16`
- **GPU 메모리 16GB+:** `--batch 16` 또는 `32`
- **CPU만 사용:** `--batch 4` 또는 `8`, `--device cpu`

### 학습률

기본값이 잘 작동합니다:
- 초기 학습률: `0.001`
- 최종 학습률: `0.00001` (lr0 * lrf)

### 에포크 수

- **최소:** 50 에포크
- **권장:** 100-200 에포크
- **충분한 시간이 있다면:** 300+ 에포크

## 🔍 학습 모니터링

학습 중 터미널에 다음과 같은 정보가 출력됩니다:

```
Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
  1/100      4.2G      1.234      2.456      0.789        1234        640
```

학습 완료 후:
- `runs/detect/drug_identification/weights/best.pt` - 최고 성능 모델
- `runs/detect/drug_identification/weights/last.pt` - 마지막 체크포인트
- `runs/detect/drug_identification/` - 학습 그래프 및 결과

## 📝 주요 스크립트 설명

### `train_val_split.py`
- COCO 포맷 데이터셋을 train/val로 분할
- 기본적으로 85:15 비율
- 랜덤 시드 42로 고정 (재현 가능)

### `train_rtdetr.py`
- RT-DETR 모델 학습 메인 스크립트
- Ultralytics RT-DETR 사용
- 자동으로 검증 수행 및 체크포인트 저장

### `inference.py`
- 학습된 모델로 추론 수행
- `drug_mapping.json`과 자동 매핑
- 시각화 옵션 제공

### `convert_coco_to_yolo.py`
- COCO 포맷을 YOLO 포맷으로 변환
- Ultralytics가 COCO를 직접 지원하지 않는 경우 사용

## 🐛 문제 해결

### 1. CUDA out of memory
```bash
# 배치 크기 줄이기
--batch 8  # 또는 4

# 이미지 크기 줄이기
--img-size 512  # 기본값 640
```

### 2. 데이터셋을 찾을 수 없음
- `dataset.yaml`의 `path`가 절대 경로인지 확인
- 이미지 경로와 annotation 경로가 올바른지 확인

### 3. 클래스 개수 불일치
- `dataset.yaml`의 `nc: 118` 확인
- `drug_mapping.json`에 0~117까지 있는지 확인

### 4. 학습이 너무 느림
- `--workers` 수를 늘리기 (기본값 8)
- GPU 사용 확인: `nvidia-smi`
- 더 작은 모델 사용: `rtdetr-r50vd.pt`

## 📈 성능 최적화 팁

1. **데이터 증강:** 기본 설정이 잘 되어 있지만, 필요시 조정 가능
2. **Early Stopping:** 검증 손실이 더 이상 개선되지 않으면 학습 중단 고려
3. **학습률 스케줄링:** 기본 cosine 스케줄 사용 중
4. **Mixed Precision:** 자동으로 활성화됨 (GPU 사용 시)

## 🔗 참고 자료

- [Ultralytics RT-DETR 문서](https://docs.ultralytics.com/models/rtdetr/)
- [RT-DETR 논문](https://arxiv.org/abs/2304.08069)

## 📧 문의

문제가 발생하면 다음을 확인하세요:
1. Python 버전 (3.8+)
2. PyTorch 및 CUDA 버전
3. 데이터셋 경로 및 파일 존재 여부
4. GPU 메모리 사용량

---

**Happy Training! 🚀**

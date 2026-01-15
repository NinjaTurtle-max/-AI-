# 🍎 M2 맥북 데모 학습 가이드 (MPS)

맥북 에어 13 M2 칩에서 MPS(Metal Performance Shaders)를 사용하여 RT-DETR 모델을 데모 학습하는 가이드입니다.

## 📋 사전 요구사항

### 1. PyTorch MPS 지원 확인

```bash
python3 -c "import torch; print(f'MPS available: {torch.backends.mps.is_available()}')"
```

`True`가 출력되어야 합니다.

### 2. 필요한 패키지

```bash
pip install ultralytics torch torchvision
```

**중요:** PyTorch 1.12+ 버전이 필요하며, MPS 지원이 포함된 버전이어야 합니다.

## 🚀 빠른 시작

### 1. 데모 학습 실행

```bash
python3 train_demo.py \
    --data dataset.yaml \
    --model rtdetr-r50vd.pt \
    --epochs 5 \
    --batch 4 \
    --img-size 640,640 \
    --device mps
```

### 2. 데모 추론 실행

```bash
python3 inference_demo.py \
    --model runs/detect/drug_identification_demo/weights/best.pt \
    --image dataset/images/example.png \
    --mapping drug_mapping.json \
    --device mps \
    --visualize
```

## ⚙️ 권장 설정 (M2 맥북)

### 학습 설정

| 파라미터 | 권장값 | 설명 |
|---------|--------|------|
| `--batch` | 2-4 | M2 GPU 메모리 제한 고려 |
| `--img-size` | 640,640 | 메모리 절약을 위해 작은 크기 |
| `--epochs` | 5-10 | 데모용으로 적은 에포크 |
| `--workers` | 2 | 맥북에서는 워커 수 줄이기 |
| `--device` | mps | Apple Silicon GPU 사용 |

### 메모리 문제 발생 시

GPU 메모리 부족 오류가 발생하면:

```bash
# 배치 크기 줄이기
python3 train_demo.py --batch 2 --device mps

# 이미지 크기 더 줄이기
python3 train_demo.py --img-size 512,512 --device mps

# CPU 사용 (느리지만 안정적)
python3 train_demo.py --device cpu
```

## 📝 주요 차이점 (데모 vs 정식 학습)

| 항목 | 정식 학습 (`train_rtdetr.py`) | 데모 학습 (`train_demo.py`) |
|------|------------------------------|----------------------------|
| **디바이스** | GPU (CUDA) | MPS (Apple Silicon) |
| **기본 배치 크기** | 16 | 4 |
| **기본 이미지 크기** | 1280x976 (원본) | 640x640 (데모용) |
| **기본 에포크** | 100 | 5 |
| **워커 수** | 8 | 2 |
| **데이터 증강** | 전체 | 축소 (Mosaic 0.5) |
| **저장 주기** | 10 에포크마다 | 1 에포크마다 |

## 🔧 문제 해결

### 1. MPS를 사용할 수 없음

```
⚠️  MPS is not available. Falling back to CPU.
```

**해결책:**
- macOS 12.3+ 확인
- PyTorch 1.12+ 버전 확인
- 최신 macOS 업데이트

### 2. GPU 메모리 부족

```
RuntimeError: MPS backend out of memory
```

**해결책:**
```bash
# 배치 크기 줄이기
--batch 2

# 이미지 크기 줄이기
--img-size 512,512

# CPU 사용
--device cpu
```

### 3. 학습 속도가 느림

MPS는 CUDA만큼 빠르지 않을 수 있습니다:
- **정상**: MPS는 CUDA 대비 50-70% 성능
- 배치 크기를 줄이면 더 느려질 수 있음
- 데모 목적이라면 5 에포크 정도로 충분

### 4. MPS 관련 오류

```python
# MPS 캐시 정리 (스크립트에 자동 포함됨)
import torch
torch.mps.empty_cache()
```

## 💡 최적화 팁

1. **작은 데이터셋 사용**: 데모 목적이라면 일부 데이터만 사용
   ```bash
   # train_val_split.py에서 val_ratio를 0.5로 설정하여 더 작은 train set 생성
   ```

2. **이미지 크기 조정**: 640x640이면 충분한 경우가 많음

3. **워커 수 조정**: 맥북에서는 2-4가 적절

4. **배치 크기**: 메모리 허용 범위 내에서 최대한 크게

## 📊 예상 성능 (M2 맥북 에어 13)

| 설정 | 학습 시간 (5 에포크) | 메모리 사용량 |
|------|---------------------|--------------|
| batch=4, 640x640 | ~20-30분 | ~6-8GB |
| batch=2, 640x640 | ~30-40분 | ~4-6GB |
| batch=4, 512x512 | ~15-20분 | ~4-6GB |
| CPU 모드 | ~2-3시간 | ~2-4GB |

*실제 성능은 데이터셋 크기와 하드웨어 사양에 따라 다를 수 있습니다.*

## 🎯 사용 예시

### 기본 데모 학습

```bash
python3 train_demo.py
```

### 커스텀 설정

```bash
python3 train_demo.py \
    --data dataset.yaml \
    --model rtdetr-r50vd.pt \
    --epochs 10 \
    --batch 4 \
    --img-size 640,640 \
    --device mps \
    --workers 2 \
    --name my_demo_experiment
```

### 단일 이미지 추론

```bash
python3 inference_demo.py \
    --model runs/detect/drug_identification_demo/weights/best.pt \
    --image dataset/images/test.png \
    --mapping drug_mapping.json \
    --device mps \
    --conf 0.25 \
    --visualize
```

### 배치 추론

```bash
python3 inference_demo.py \
    --model runs/detect/drug_identification_demo/weights/best.pt \
    --image-dir dataset/images \
    --mapping drug_mapping.json \
    --device mps \
    --visualize \
    --output-dir results/demo_predictions
```

## ⚠️ 주의사항

1. **데모 목적**: 이 스크립트는 데모/테스트 목적으로 설계되었습니다
2. **전체 학습**: 실제 프로덕션 모델은 SSH 서버에서 `train_rtdetr.py` 사용 권장
3. **메모리 제한**: M2 GPU 메모리는 제한적이므로 배치 크기에 주의
4. **성능**: MPS는 CUDA 대비 느릴 수 있음

## 🔗 관련 파일

- `train_demo.py` - MPS 지원 데모 학습 스크립트
- `inference_demo.py` - MPS 지원 데모 추론 스크립트
- `train_rtdetr.py` - 정식 학습 스크립트 (GPU 서버용)
- `inference.py` - 정식 추론 스크립트

---

**Happy Demo Training on M2 MacBook! 🍎🚀**

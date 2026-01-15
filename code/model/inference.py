"""
RT-DETR 모델 추론 및 Drug Mapping 테스트 스크립트
학습된 모델을 사용하여 이미지를 추론하고 drug_mapping.json과 매핑합니다.
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Tuple
import cv2
import numpy as np
from ultralytics import RTDETR

def load_drug_mapping(mapping_path: str) -> Dict[str, Dict[str, str]]:
    """
    drug_mapping.json 파일을 로드
    
    Returns:
        {drug_id: {"code": ..., "name": ...}} 형태의 딕셔너리
    """
    with open(mapping_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def predict_image(
    model_path: str,
    image_path: str,
    conf_threshold: float = 0.25,
    iou_threshold: float = 0.45,
    device: str = "0"
) -> List[Dict]:
    """
    단일 이미지에 대해 추론 수행
    
    Args:
        model_path: 학습된 모델 가중치 경로 (best.pt 또는 last.pt)
        image_path: 추론할 이미지 경로
        conf_threshold: 신뢰도 임계값
        iou_threshold: IoU 임계값 (NMS)
        device: 사용할 디바이스
    
    Returns:
        검출 결과 리스트 [{"class_id": int, "confidence": float, "bbox": [x1, y1, x2, y2], "drug_name": str}, ...]
    """
    # 모델 로드
    model = RTDETR(model_path)
    
    # 추론 수행
    results = model.predict(
        source=image_path,
        conf=conf_threshold,
        iou=iou_threshold,
        device=device,
        verbose=False
    )
    
    # 결과 파싱
    detections = []
    result = results[0]
    
    if result.boxes is not None and len(result.boxes) > 0:
        boxes = result.boxes
        for i in range(len(boxes)):
            cls_id = int(boxes.cls[i].item())
            conf = float(boxes.conf[i].item())
            bbox = boxes.xyxy[i].cpu().numpy().tolist()  # [x1, y1, x2, y2]
            
            detections.append({
                "class_id": cls_id,
                "confidence": conf,
                "bbox": bbox
            })
    
    return detections

def predict_batch(
    model_path: str,
    image_dir: str,
    conf_threshold: float = 0.25,
    iou_threshold: float = 0.45,
    device: str = "0"
) -> Dict[str, List[Dict]]:
    """
    여러 이미지에 대해 배치 추론 수행
    
    Args:
        model_path: 학습된 모델 가중치 경로
        image_dir: 이미지 디렉토리 경로
        conf_threshold: 신뢰도 임계값
        iou_threshold: IoU 임계값
        device: 사용할 디바이스
    
    Returns:
        {image_name: [detections, ...]} 형태의 딕셔너리
    """
    model = RTDETR(model_path)
    
    # 이미지 파일 찾기
    image_extensions = ['.png', '.jpg', '.jpeg', '.bmp']
    image_files = []
    for ext in image_extensions:
        image_files.extend(Path(image_dir).glob(f"*{ext}"))
        image_files.extend(Path(image_dir).glob(f"*{ext.upper()}"))
    
    print(f"Found {len(image_files)} images in {image_dir}")
    
    # 배치 추론
    results = model.predict(
        source=str(image_dir),
        conf=conf_threshold,
        iou=iou_threshold,
        device=device,
        verbose=True
    )
    
    # 결과 정리
    all_results = {}
    for i, result in enumerate(results):
        image_name = Path(result.path).name
        detections = []
        
        if result.boxes is not None and len(result.boxes) > 0:
            boxes = result.boxes
            for j in range(len(boxes)):
                cls_id = int(boxes.cls[j].item())
                conf = float(boxes.conf[j].item())
                bbox = boxes.xyxy[j].cpu().numpy().tolist()
                
                detections.append({
                    "class_id": cls_id,
                    "confidence": conf,
                    "bbox": bbox
                })
        
        all_results[image_name] = detections
    
    return all_results

def map_to_drug_name(class_id: int, drug_mapping: Dict[str, Dict[str, str]]) -> Tuple[str, str]:
    """
    클래스 ID를 약품명으로 매핑
    
    Args:
        class_id: 예측된 클래스 ID (0~117)
        drug_mapping: drug_mapping.json에서 로드한 딕셔너리
    
    Returns:
        (drug_code, drug_name) 튜플
    """
    drug_id_str = str(class_id)
    if drug_id_str in drug_mapping:
        drug_info = drug_mapping[drug_id_str]
        return drug_info.get("code", ""), drug_info.get("name", f"Unknown (ID: {class_id})")
    else:
        return "", f"Unknown (ID: {class_id})"

def visualize_prediction(
    image_path: str,
    detections: List[Dict],
    drug_mapping: Dict[str, Dict[str, str]],
    output_path: str = None,
    conf_threshold: float = 0.25
):
    """
    추론 결과를 이미지에 시각화
    
    Args:
        image_path: 원본 이미지 경로
        detections: 검출 결과 리스트
        drug_mapping: 약품 매핑 딕셔너리
        output_path: 출력 이미지 경로 (None이면 표시만)
        conf_threshold: 시각화할 최소 신뢰도
    """
    # 이미지 로드
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load image {image_path}")
        return
    
    # 검출 결과 그리기
    for det in detections:
        if det["confidence"] < conf_threshold:
            continue
        
        class_id = det["class_id"]
        conf = det["confidence"]
        bbox = det["bbox"]
        
        # 약품명 가져오기
        _, drug_name = map_to_drug_name(class_id, drug_mapping)
        
        # 바운딩 박스 그리기
        x1, y1, x2, y2 = map(int, bbox)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # 라벨 텍스트
        label = f"{drug_name} ({conf:.2f})"
        
        # 텍스트 배경
        (text_width, text_height), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
        )
        cv2.rectangle(
            img,
            (x1, y1 - text_height - baseline - 5),
            (x1 + text_width, y1),
            (0, 255, 0),
            -1
        )
        
        # 텍스트 그리기
        cv2.putText(
            img,
            label,
            (x1, y1 - baseline - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 0),
            2
        )
    
    # 결과 저장 또는 표시
    if output_path:
        cv2.imwrite(output_path, img)
        print(f"Visualization saved to {output_path}")
    else:
        cv2.imshow("Prediction", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def main():
    """메인 함수 - 예시 사용법"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RT-DETR Inference and Drug Mapping")
    parser.add_argument("--model", type=str, required=True, help="Model weight path (best.pt or last.pt)")
    parser.add_argument("--image", type=str, help="Single image path for inference")
    parser.add_argument("--image-dir", type=str, help="Image directory for batch inference")
    parser.add_argument("--mapping", type=str, default="drug_mapping.json", help="Drug mapping JSON file")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=0.45, help="IoU threshold")
    parser.add_argument("--device", type=str, default="0", help="Device (0, 1, cpu)")
    parser.add_argument("--visualize", action="store_true", help="Visualize predictions")
    parser.add_argument("--output-dir", type=str, help="Output directory for visualizations")
    
    args = parser.parse_args()
    
    # drug_mapping 로드
    script_dir = Path(__file__).parent
    mapping_path = script_dir / args.mapping
    if not mapping_path.exists():
        raise FileNotFoundError(f"Drug mapping file not found: {mapping_path}")
    
    drug_mapping = load_drug_mapping(str(mapping_path))
    print(f"Loaded drug mapping with {len(drug_mapping)} classes")
    
    # 단일 이미지 추론
    if args.image:
        print(f"\nPredicting on image: {args.image}")
        detections = predict_image(
            model_path=args.model,
            image_path=args.image,
            conf_threshold=args.conf,
            iou_threshold=args.iou,
            device=args.device
        )
        
        print(f"\nFound {len(detections)} detections:")
        for i, det in enumerate(detections, 1):
            class_id = det["class_id"]
            conf = det["confidence"]
            code, name = map_to_drug_name(class_id, drug_mapping)
            
            print(f"\n  Detection {i}:")
            print(f"    Class ID: {class_id}")
            print(f"    Drug Code: {code}")
            print(f"    Drug Name: {name}")
            print(f"    Confidence: {conf:.4f}")
            print(f"    BBox: {det['bbox']}")
        
        # 시각화
        if args.visualize:
            output_path = None
            if args.output_dir:
                os.makedirs(args.output_dir, exist_ok=True)
                output_path = os.path.join(
                    args.output_dir,
                    f"pred_{Path(args.image).name}"
                )
            visualize_prediction(
                image_path=args.image,
                detections=detections,
                drug_mapping=drug_mapping,
                output_path=output_path,
                conf_threshold=args.conf
            )
    
    # 배치 추론
    elif args.image_dir:
        print(f"\nPredicting on images in: {args.image_dir}")
        all_results = predict_batch(
            model_path=args.model,
            image_dir=args.image_dir,
            conf_threshold=args.conf,
            iou_threshold=args.iou,
            device=args.device
        )
        
        print(f"\n{'='*80}")
        print("Batch Inference Results")
        print(f"{'='*80}")
        
        for image_name, detections in all_results.items():
            print(f"\n{image_name}: {len(detections)} detections")
            for det in detections:
                class_id = det["class_id"]
                conf = det["confidence"]
                code, name = map_to_drug_name(class_id, drug_mapping)
                print(f"  - {name} (ID: {class_id}, Conf: {conf:.3f})")
        
        # 시각화
        if args.visualize and args.output_dir:
            os.makedirs(args.output_dir, exist_ok=True)
            for image_name, detections in all_results.items():
                image_path = os.path.join(args.image_dir, image_name)
                output_path = os.path.join(args.output_dir, f"pred_{image_name}")
                visualize_prediction(
                    image_path=image_path,
                    detections=detections,
                    drug_mapping=drug_mapping,
                    output_path=output_path,
                    conf_threshold=args.conf
                )
    
    else:
        parser.print_help()
        print("\nError: Either --image or --image-dir must be specified")


if __name__ == "__main__":
    main()

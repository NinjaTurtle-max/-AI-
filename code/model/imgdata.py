import os
import shutil
import json
from pathlib import Path
from tqdm import tqdm
from collections import defaultdict

# ============================================================================
# Configuration Area - 서버 경로에 맞춰 수정하세요
# ============================================================================
SOURCE_ROOT_DIR = '/Users/ganghyeon-u/Downloads/166.약품식별 인공지능 개발을 위한 경구약제 이미지 데이터/01.데이터/1.Training/원천데이터'
DESTINATION_DIR = './dataset/images'

# 지원하는 이미지 확장자
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'}

# 실패한 파일 목록 저장 경로
FAILED_FILES_LOG = './failed_files.json'

# ============================================================================
# Disk Space Utilities
# ============================================================================

def get_disk_usage(path: str) -> dict:
    """
    디스크 사용량 정보 반환
    
    Args:
        path: 확인할 경로
        
    Returns:
        {'total': 총 용량(바이트), 'used': 사용 중(바이트), 'free': 여유 공간(바이트)}
    """
    stat = shutil.disk_usage(path)
    return {
        'total': stat.total,
        'used': stat.used,
        'free': stat.free
    }

def format_bytes(bytes_size: int) -> str:
    """바이트를 읽기 쉬운 형식으로 변환"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

def check_disk_space(destination_dir: str, required_space: int) -> tuple[bool, dict]:
    """
    디스크 공간이 충분한지 확인
    
    Args:
        destination_dir: 대상 디렉토리
        required_space: 필요한 공간 (바이트)
        
    Returns:
        (충분 여부, 디스크 정보 딕셔너리)
    """
    disk_info = get_disk_usage(destination_dir)
    is_sufficient = disk_info['free'] >= required_space
    
    return is_sufficient, disk_info

def calculate_required_space(image_files: list, destination_dir: str) -> int:
    """
    복사에 필요한 총 공간 계산 (이미 복사된 파일 제외)
    
    Args:
        image_files: 복사할 이미지 파일 경로 리스트
        destination_dir: 대상 디렉토리
        
    Returns:
        필요한 총 공간 (바이트)
    """
    total_size = 0
    existing_files = set()
    
    # 이미 존재하는 파일 목록 생성
    if os.path.exists(destination_dir):
        for filename in os.listdir(destination_dir):
            existing_files.add(filename)
    
    print("Calculating required disk space...")
    for source_path in tqdm(image_files, desc="Calculating", unit="file"):
        try:
            filename = os.path.basename(source_path)
            # 이미 복사된 파일이면 제외
            if filename in existing_files:
                target_path = os.path.join(destination_dir, filename)
                if os.path.exists(target_path):
                    source_size = os.path.getsize(source_path)
                    target_size = os.path.getsize(target_path)
                    # 크기가 다르면 중복 파일로 저장될 수 있으므로 포함
                    if source_size != target_size:
                        total_size += source_size
            else:
                total_size += os.path.getsize(source_path)
        except Exception:
            # 파일 크기를 읽을 수 없으면 일단 포함
            pass
    
    return total_size

# ============================================================================
# Main Functions
# ============================================================================

def find_all_images(source_dir: str) -> list:
    """
    원본 디렉토리에서 모든 이미지 파일을 재귀적으로 찾아 반환
    
    Args:
        source_dir: 탐색할 원본 디렉토리 경로
        
    Returns:
        찾은 이미지 파일 경로 리스트
    """
    image_files = []
    
    print(f"Scanning directory: {source_dir}")
    print("This may take a while for large directories...")
    
    for dirpath, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            file_ext = os.path.splitext(filename)[1]
            if file_ext in IMAGE_EXTENSIONS:
                full_path = os.path.join(dirpath, filename)
                image_files.append(full_path)
    
    return image_files

def get_unique_filename(destination_dir: str, filename: str) -> str:
    """
    중복 파일명을 처리하여 고유한 파일명 생성
    
    Args:
        destination_dir: 대상 디렉토리
        filename: 원본 파일명
        
    Returns:
        고유한 파일명 (중복 시 _duplicate_N 접미사 추가)
    """
    base_name, ext = os.path.splitext(filename)
    target_path = os.path.join(destination_dir, filename)
    
    # 파일이 존재하지 않으면 원본 이름 반환
    if not os.path.exists(target_path):
        return filename
    
    # 중복 파일 처리
    counter = 1
    while True:
        new_filename = f"{base_name}_duplicate_{counter}{ext}"
        new_target_path = os.path.join(destination_dir, new_filename)
        
        if not os.path.exists(new_target_path):
            return new_filename
        
        counter += 1

def move_images(image_files: list, destination_dir: str, check_space: bool = True) -> dict:
    """
    이미지 파일들을 대상 디렉토리로 이동
    
    Args:
        image_files: 이동할 이미지 파일 경로 리스트
        destination_dir: 대상 디렉토리
        check_space: 디스크 공간 확인 여부
        
    Returns:
        통계 딕셔너리 (success, duplicate, error, error_files)
    """
    # 대상 디렉토리 생성
    os.makedirs(destination_dir, exist_ok=True)
    
    stats = {
        'success': 0,
        'duplicate': 0,
        'error': 0,
        'error_files': []
    }
    
    # 파일명 중복 추적 (같은 원본 파일명이 여러 개 있을 수 있음)
    filename_counter = defaultdict(int)
    
    # 디스크 공간 확인
    if check_space:
        required_space = calculate_required_space(image_files, destination_dir)
        is_sufficient, disk_info = check_disk_space(destination_dir, required_space)
        
        print(f"\n디스크 공간 정보:")
        print(f"  총 용량: {format_bytes(disk_info['total'])}")
        print(f"  사용 중: {format_bytes(disk_info['used'])}")
        print(f"  여유 공간: {format_bytes(disk_info['free'])}")
        print(f"  필요 공간: {format_bytes(required_space)}")
        
        if not is_sufficient:
            print(f"\n⚠️  경고: 디스크 공간이 부족합니다!")
            print(f"  부족한 공간: {format_bytes(required_space - disk_info['free'])}")
            response = input("  계속 진행하시겠습니까? (y/n): ")
            if response.lower() != 'y':
                print("작업이 취소되었습니다.")
                return stats
    
    print(f"\nMoving {len(image_files)} images to {destination_dir}...")
    
    for source_path in tqdm(image_files, desc="Moving images", unit="file"):
        try:
            # 원본 파일이 존재하는지 확인 (이미 이동되었을 수 있음)
            if not os.path.exists(source_path):
                stats['duplicate'] += 1
                continue
            
            # 원본 파일명 추출
            original_filename = os.path.basename(source_path)
            
            # 중복 처리
            if original_filename in filename_counter:
                filename_counter[original_filename] += 1
                base_name, ext = os.path.splitext(original_filename)
                new_filename = f"{base_name}_duplicate_{filename_counter[original_filename]}{ext}"
                stats['duplicate'] += 1
            else:
                # 대상 디렉토리에 같은 이름의 파일이 있는지 확인
                target_path = os.path.join(destination_dir, original_filename)
                if os.path.exists(target_path):
                    # 파일 내용 비교 (같은 파일인지 확인)
                    if os.path.getsize(source_path) == os.path.getsize(target_path):
                        # 크기가 같으면 원본 파일 삭제 (이미 이동된 것으로 간주)
                        try:
                            os.remove(source_path)
                        except:
                            pass
                        stats['duplicate'] += 1
                        continue
                    else:
                        # 크기가 다르면 중복 이름으로 저장
                        new_filename = get_unique_filename(destination_dir, original_filename)
                        stats['duplicate'] += 1
                else:
                    new_filename = original_filename
            
            # 파일 이동
            destination_path = os.path.join(destination_dir, new_filename)
            shutil.move(source_path, destination_path)
            stats['success'] += 1
            
        except OSError as e:
            # 디스크 공간 부족 등 OS 오류
            if e.errno == 28:  # No space left on device
                stats['error'] += 1
                error_msg = f"[Errno 28] No space left on device"
                stats['error_files'].append((source_path, error_msg))
                tqdm.write(f"❌ 디스크 공간 부족: {os.path.basename(source_path)}")
                # 디스크 공간 부족 시 중단 여부 확인
                if stats['error'] == 1:  # 첫 번째 오류일 때만
                    response = input("\n⚠️  디스크 공간이 부족합니다. 계속 시도하시겠습니까? (y/n): ")
                    if response.lower() != 'y':
                        print("작업이 중단되었습니다.")
                        break
            else:
                stats['error'] += 1
                stats['error_files'].append((source_path, str(e)))
                tqdm.write(f"Error moving {source_path}: {e}")
        except Exception as e:
            stats['error'] += 1
            stats['error_files'].append((source_path, str(e)))
            tqdm.write(f"Error moving {source_path}: {e}")
    
    return stats

def save_failed_files(stats: dict, log_path: str = FAILED_FILES_LOG):
    """
    실패한 파일 목록을 JSON 파일로 저장
    
    Args:
        stats: move_images에서 반환된 통계 딕셔너리
        log_path: 저장할 파일 경로
    """
    if stats['error'] > 0:
        failed_data = {
            'total_failed': stats['error'],
            'failed_files': [
                {
                    'source_path': file_path,
                    'error': error_msg
                }
                for file_path, error_msg in stats['error_files']
            ]
        }
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(failed_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 실패한 파일 목록이 저장되었습니다: {log_path}")

def retry_failed_files(log_path: str = FAILED_FILES_LOG, destination_dir: str = None):
    """
    이전에 실패한 파일들을 다시 시도
    
    Args:
        log_path: 실패한 파일 목록이 저장된 파일 경로
        destination_dir: 대상 디렉토리 (None이면 DESTINATION_DIR 사용)
    """
    if destination_dir is None:
        destination_dir = DESTINATION_DIR
    
    if not os.path.exists(log_path):
        print(f"❌ 실패한 파일 목록을 찾을 수 없습니다: {log_path}")
        return
    
    with open(log_path, 'r', encoding='utf-8') as f:
        failed_data = json.load(f)
    
    failed_files = [item['source_path'] for item in failed_data['failed_files']]
    
    if len(failed_files) == 0:
        print("재시도할 파일이 없습니다.")
        return
    
    print(f"\n재시도: {len(failed_files)}개 파일 이동 시도...")
    stats = move_images(failed_files, destination_dir, check_space=True)
    
    # 재시도 후 성공한 파일은 로그에서 제거
    if stats['success'] > 0:
        remaining_failed = [
            item for item in failed_data['failed_files']
            if item['source_path'] not in [f for f, _ in stats['error_files']]
        ]
        
        if len(remaining_failed) < len(failed_data['failed_files']):
            failed_data['failed_files'] = remaining_failed
            failed_data['total_failed'] = len(remaining_failed)
            
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(failed_data, f, ensure_ascii=False, indent=2)
    
    return stats

def print_summary(total_found: int, stats: dict):
    """
    작업 요약 정보 출력
    
    Args:
        total_found: 탐색된 총 파일 수
        stats: copy_images에서 반환된 통계 딕셔너리
    """
    print("\n" + "="*60)
    print("작업 요약 (Summary)")
    print("="*60)
    print(f"총 탐색 파일 수 (Total files found):     {total_found:,}")
    print(f"이동 성공 수 (Successfully moved):       {stats['success']:,}")
    print(f"중복/스킵 수 (Duplicates/Skipped):       {stats['duplicate']:,}")
    print(f"실패 수 (Errors):                        {stats['error']:,}")
    print("="*60)
    
    if stats['error'] > 0:
        print(f"\n⚠️  {stats['error']}개 파일 이동 실패:")
        
        # 오류 유형별 분류
        error_types = defaultdict(list)
        for file_path, error_msg in stats['error_files']:
            if 'No space left' in error_msg or 'Errno 28' in error_msg:
                error_types['disk_full'].append((file_path, error_msg))
            else:
                error_types['other'].append((file_path, error_msg))
        
        if error_types['disk_full']:
            print(f"\n  💾 디스크 공간 부족: {len(error_types['disk_full'])}개 파일")
            print(f"     → 해결 방법: 디스크 공간을 확보한 후 재시도하세요.")
            print(f"     → 재시도 명령: python imgdata.py --retry")
        
        if error_types['other']:
            print(f"\n  ⚠️  기타 오류: {len(error_types['other'])}개 파일")
            for file_path, error_msg in error_types['other'][:5]:
                print(f"     - {os.path.basename(file_path)}: {error_msg}")
            if len(error_types['other']) > 5:
                print(f"     ... 외 {len(error_types['other']) - 5}개 파일")
        
        print(f"\n  💡 실패한 파일 목록은 {FAILED_FILES_LOG}에 저장되었습니다.")
        print(f"     재시도하려면: python imgdata.py --retry")
    
    success_rate = (stats['success'] / total_found * 100) if total_found > 0 else 0
    print(f"\n성공률 (Success rate): {success_rate:.2f}%")

def main():
    """메인 실행 함수"""
    import sys
    
    # 재시도 모드 확인
    if len(sys.argv) > 1 and sys.argv[1] == '--retry':
        print("="*60)
        print("실패한 파일 재시도 모드")
        print("="*60)
        stats = retry_failed_files(FAILED_FILES_LOG, DESTINATION_DIR)
        print_summary(len(stats.get('error_files', [])), stats)
        return
    
    print("="*60)
    print("이미지 파일 Flatten 스크립트")
    print("="*60)
    print(f"Source: {SOURCE_ROOT_DIR}")
    print(f"Destination: {DESTINATION_DIR}")
    print("="*60)
    
    # 소스 디렉토리 존재 확인
    if not os.path.exists(SOURCE_ROOT_DIR):
        print(f"❌ 오류: 소스 디렉토리를 찾을 수 없습니다: {SOURCE_ROOT_DIR}")
        return
    
    # 모든 이미지 파일 찾기
    print("\n[Step 1] 이미지 파일 탐색 중...")
    image_files = find_all_images(SOURCE_ROOT_DIR)
    
    if len(image_files) == 0:
        print("❌ 이미지 파일을 찾을 수 없습니다.")
        return
    
    print(f"✓ {len(image_files):,}개의 이미지 파일을 찾았습니다.")
    
    # 이미지 파일 이동
    print("\n[Step 2] 이미지 파일 이동 중...")
    stats = move_images(image_files, DESTINATION_DIR, check_space=True)
    
    # 실패한 파일 목록 저장
    save_failed_files(stats)
    
    # 요약 출력
    print_summary(len(image_files), stats)
    
    if stats['error'] == 0:
        print(f"\n✓ 작업 완료! 이미지들이 {DESTINATION_DIR}로 이동되었습니다.")
    else:
        print(f"\n⚠️  작업 완료 (일부 파일 실패)")
        print(f"   성공: {stats['success']:,}개, 실패: {stats['error']:,}개")
        print(f"   재시도: python imgdata.py --retry")

if __name__ == "__main__":
    main()

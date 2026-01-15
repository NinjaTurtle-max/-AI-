import json, os

label_name = "/Users/doeun/Downloads/166.약품식별 인공지능 개발을 위한 경구약제 이미지 데이터/01.데이터/1.Training/라벨링데이터/경구약제조합 5000종/"

label_path = []
for dirpath, dirnames, filenames in os.walk(label_name):
    for filename in filenames:
        for filename in filenames:
            if filename.endswith("json"):
                full_path = os.path.join(dirpath, filename)
                label_path.append(full_path)

if __name__ == "__main__":
    print(len(label_path))
    print(label_path[:10])
    
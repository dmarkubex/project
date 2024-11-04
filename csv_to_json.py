import csv
import json
import os

# 读取 CSV 文件并转换为 JSON 格式
def csv_to_json(csv_file_path, json_file_path):
    data = []
    with open(csv_file_path, encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)
    
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 文件路径
csv_file_path = os.path.join(current_dir, 'QC2020.csv')
json_file_path = os.path.join(current_dir, 'QC2020.json')

# 检查文件是否存在
if not os.path.exists(csv_file_path):
    print(f"File not found: {csv_file_path}")
else:
    # 转换
    csv_to_json(csv_file_path, json_file_path)
    print(f"Conversion completed: {json_file_path}")
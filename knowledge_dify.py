import requests
import json
from datetime import datetime, timedelta
import time

# 配置常量
URL = "https://directus.fegroup.cn:8055/items/qc_reason_analy"
ATTACH_URL = "https://directus.fegroup.cn:8055/items/qc_reason_analy_files"
FILE_URL = "https://directus.fegroup.cn:8055/assets"
BEARER_TOKEN = "9DSgXZQYMHlSj1xwPlJGLhskED3YxK7p"
DIFY_API_ENDPOINT = "https://ai.fegroup.cn:8800/v1/datasets/c8cf659e-c413-45dd-a10d-3b503e0d6f7f/document"
DIFY_API_KEY = "dataset-kKrCMqS6eRzKeVm3FEvhPBzv"

# 设置请求头
HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

DIFY_HEADERS = {
    "Authorization": f"Bearer {DIFY_API_KEY}",
    "Content-Type": "application/json"
}

def get_file_info(qc_reason_analy_id):
    try:
        # 查询qc_reason_analy_id对应的记录
        response = requests.get(f"{URL}/{qc_reason_analy_id}", headers=HEADERS)
        response.raise_for_status()
        record = response.json().get("data")
        
        if record:
            file_id = record.get("directus_file_id")  # 替换为实际的文件字段名
            if file_id:
                # 获取文件详细信息
                file_response = requests.get(f"{FILE_URL}/{file_id}", headers=HEADERS)
                file_response.raise_for_status()
                file_info = file_response.json()
                return file_info
            else:
                print("文件字段为空")
        else:
            print("记录不存在")
        
    except requests.RequestException as e:
        print(f"获取文件信息失败: {e}")
    
    return None

def fetch_records_with_attachments():
    try:
        # 获取记录
        response = requests.get(URL, headers=HEADERS)
        response.raise_for_status()
        records = response.json().get("data", [])
        
        for record in records:
            attachment_id = get_file_info(record)  # 替换为实际的附件字段名
            if attachment_id:
                # 获取附件详细信息
                file_response = requests.get(f"{FILE_URL}/{attachment_id}?download=", headers=HEADERS)
                file_response.raise_for_status()
                file_info = file_response.json()
                file_url = file_info.get("data", {}).get("url")
                record['attachment_url'] = file_url
                file_id = file_info.get("data", {}).get("directus_files_id")
                if file_id:
                    # 获取文件详细信息
                    file_info_response = requests.get(f"{FILE_URL}/{file_id}", headers=HEADERS)
                    file_info_response.raise_for_status()
                    file_info = file_info_response.json()
                    record['file_info'] = file_info
                else:
                    record['file_info'] = None
            else:
                record['attachment_url'] = None
                record['file_info'] = None
        return records
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return []

def write_to_dify_knowledge_base(records):
    for record in records:
        document = {
            "id": record["id"],  # 使用记录的唯一标识符
            "content": json.dumps(record),  # 将记录内容转换为JSON字符串
            "metadata": {
                "attachment_url": record.get("attachment_url")
            }
        }
        response = requests.post(DIFY_API_ENDPOINT, headers=DIFY_HEADERS, data=json.dumps(document))
        if response.status_code == 200:
            print(f"Record ID: {record['id']} successfully written to Dify knowledge base.")
        else:
            print(f"Failed to write Record ID: {record['id']} to Dify knowledge base. Status code: {response.status_code}")

def daily_task():
    while True:
        print(f"Task started at {datetime.now()}")
        records = fetch_records_with_attachments()
        # write_to_dify_knowledge_base(records)
        # print(f"Task completed at {datetime.now()}")

        https://directus.fegroup.cn:8055/assets/04c60f40-4151-450c-9f35-65a8e141b915?download=

        https://directus.fegroup.cn:8055/asstets/2230c7a8-9d15-42ea-9c49-3eccb311016d?download=

# 启动定时任务
daily_task()

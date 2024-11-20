import requests
import json
from datetime import datetime
import time

# 配置常量
DIRECTUS_URL = "http://10.1.20.152:8055/items/ai_questions"
DIRECTUS_BEARER_TOKEN = "9DSgXZQYMHlSj1xwPlJGLhskED3YxK7p"
DIFY_API_ENDPOINT = "https://ai.fegroup.cn:8800/v1/datasets/994a5097-d77d-4f0b-be5f-7b186e3dd097/document/create-by-text"
DIFY_API_KEY = "dataset-kKrCMqS6eRzKeVm3FEvhPBzv"

# 设置请求头
DIRECTUS_HEADERS = {
    "Authorization": f"Bearer {DIRECTUS_BEARER_TOKEN}"
}

DIFY_HEADERS = {
    "Authorization": f"Bearer {DIFY_API_KEY}",
    "Content-Type": "application/json"
}

def fetch_records():
    try:
        # 获取记录
        response = requests.get(DIRECTUS_URL, headers=DIRECTUS_HEADERS)
        response.raise_for_status()
        records = response.json().get("data", [])
        return records
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return []

def create_document_in_dify(records):
    # 获取当前日期
    current_date = datetime.now().strftime("%Y-%m-%d")
    document_name = f"AI问答_{current_date}"
    
    # 组合所有 query 和 answer
    text_content = ""
    for record in records:
        query = record.get("query", "No Query")
        answer = record.get("answer", "No Answer")
        text_content += f"Query: {query}\nAnswer: {answer}\n\n"
    
    document = {
        "name": document_name,  # 使用“AI问答”加上日期作为文档名称
        "text": text_content,  # 将所有 query 和 answer 组合成文本
        "indexing_technique": "high_quality",
        "process_rule": {
            "mode": "automatic",
            "rules": {},
            "pre_processing_rules": [
                {"id": "remove_extra_spaces", "enabled": True},
                {"id": "remove_urls_emails", "enabled": True}
            ],
            "segmentation": {
                "separator": "\n",
                "max_tokens": 1000
            }
        }
    }
    
    # 打印请求体以进行调试
    print("请求体:", json.dumps(document, indent=2, ensure_ascii=False))
    
    # 重试逻辑
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(DIFY_API_ENDPOINT, headers=DIFY_HEADERS, data=json.dumps(document), proxies={"http": None, "https": None})
            if response.status_code == 200:
                print(f"Document '{document_name}' successfully created in Dify knowledge base.")
                return
            else:
                print(f"Attempt {attempt + 1} failed to create document '{document_name}' in Dify knowledge base. Status code: {response.status_code}")
                print("响应内容:", response.text)
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} encountered an error: {e}")
        
        if attempt < max_retries - 1:
            time.sleep(5)  # 等待 5 秒后重试

    print(f"Failed to create document '{document_name}' in Dify knowledge base after {max_retries} attempts.")

def main():
    records = fetch_records()
    if records:
        create_document_in_dify(records)

# 执行主函数
main()
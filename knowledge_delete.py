import requests
import json
from datetime import datetime

# 配置常量
DIFY_API_ENDPOINT = "https://ai.fegroup.cn:8800/v1/datasets/994a5097-d77d-4f0b-be5f-7b186e3dd097"
DIFY_API_KEY = "dataset-kKrCMqS6eRzKeVm3FEvhPBzv"
DOCUMENT_NAME_BASE = "AI问答"

# 设置请求头
DIFY_HEADERS = {
    "Authorization": f"Bearer {DIFY_API_KEY}",
    "Content-Type": "application/json"
}

def get_documents():
    try:
        response = requests.get(f"{DIFY_API_ENDPOINT}/documents", headers=DIFY_HEADERS)
        response.raise_for_status()
        documents = response.json().get("data", [])
        return documents
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return []

def delete_document(document_id):
    try:
        response = requests.delete(f"{DIFY_API_ENDPOINT}/documents/{document_id}", headers=DIFY_HEADERS)
        response.raise_for_status()
        print(f"Document ID: {document_id} successfully deleted.")
    except requests.RequestException as e:
        print(f"删除文档失败: {e}")

def main():
    documents = get_documents()
    for document in documents:
        if document["name"].startswith(DOCUMENT_NAME_BASE):
            delete_document(document["id"])

# 执行主函数
main()
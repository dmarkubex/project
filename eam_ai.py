import sys
import mysql.connector
import requests
import json

# 设置默认编码为 utf-8
sys.stdout.reconfigure(encoding='utf-8')

# 配置连接
db_config = {
    'user': 'app',
    'password': 'YDeam@2023..',
    'host': '10.1.14.30',
    'database': 'sieiot_eam'
}

# 配置API接口
api_url = "https://ai.fegroup.cn:8800/v1/chat-messages"
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer app-0lJTngcxoxFhHI4q0M7LSv4f'  # 替换为你的实际 token
}

# 查询设备故障现象
def fetch_fault_descriptions():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """select ew_id, ac_name, fault_description FROM eam_workorder_m ewm where ewm.creation_date>=CURDATE() - INTERVAL 1 DAY and not exists(
    select '1'
    from ai_service_suggest ass
    where ass.ew_id=ewm.ew_id
    )"""
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results

# 清理输入数据
def clean_input(input_str):
    return input_str.encode('utf-8', 'ignore').decode('utf-8')

# 调用API获取建议解决措施
def get_suggested_solution(ac_name, fault_description):
    ac_name = clean_input(ac_name)
    fault_description = clean_input(fault_description)
    query = f"{ac_name} {fault_description}"
    payload = {
        "inputs": {},
        "query": query,
        "response_mode": "blocking",
        "conversation_id": "",
        "user": "service-time",
        "files": []
    }
    response = requests.post(api_url, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        print(f"API Response: {response_data}")  # 打印API响应
        return response_data.get('answer', None)
    else:
        print(f"Error fetching suggestion: {response.status_code} - {response.text}")
        return None

# 插入建议解决措施到数据库
def insert_service_suggest(ew_id, fault_description, suggestion):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    insert_query = """
    INSERT INTO ai_service_suggest (ew_id, fault_description, suggest_method)
    VALUES (%s, %s, %s)
    """
    cursor.execute(insert_query, (ew_id, fault_description, suggestion))
    connection.commit()
    cursor.close()
    connection.close()

# 主函数
def main():
    fault_descriptions = fetch_fault_descriptions()
    for ew_id, ac_name, fault_description in fault_descriptions:
        suggestion = get_suggested_solution(ac_name, fault_description)
        if suggestion:  # 仅在获取到建议时插入数据库
            insert_service_suggest(ew_id, fault_description, suggestion)
            print(f"Processed ew_id: {ew_id}, suggestion: {suggestion}")
        else:
            print(f"Skipped ew_id: {ew_id} due to no suggestion")

if __name__ == "__main__":
    main()
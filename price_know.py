import requests
from datetime import datetime

def fetch_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch data:", response.status_code, response.text)
        return None

def save_to_txt(data, file_path):
    if not data or 'data' not in data:
        print("No data to save.")
        return

    with open(file_path, mode='w', encoding='utf-8') as file:
        for row in data['data']:
            day = row['day']
            type_name = row['type_name']
            price = row['price']
            try:
                rate = int(row['rate'].replace('-', ''))  # Remove all '-' characters from rate
            except ValueError:
                print("Invalid rate value:", row['rate'])
                continue
            change = f"变动{rate}元" if rate >= 0 else f"变动{rate}元"
            line = f"{day} SMM {type_name}的价格为{price}，{change}；"
            file.write(line + '\n')

def upload_file_to_kb(file_path, kb_name, token, parser_id='naive'):
    url = 'http://10.1.80.185/v1/api/document/upload'  # Replace with your actual API URL
    files = {'file': open(file_path, 'rb')}  # The file to upload
    data = {'kb_name': kb_name, 'parser_id': parser_id, 'run': '1'}  # Additional form data
    headers = {'Authorization': f'Bearer {token}'}  # Replace with your actual Bearer token

    response = requests.post(url, files=files, data=data, headers=headers)

    if response.status_code == 200:
        print("File uploaded successfully:", response.json())
    else:
        print("Failed to upload file:", response.status_code, response.text)

# 获取当天日期
today = datetime.now().strftime('%Y-%m-%d')
fileday = datetime.now().strftime('%Y%m%d')

# API URL
api_url = f'http://10.1.20.152:8055/items/per_price?fields=day,type_name,price,uom,rate&filter[day][_contains]={today}'

# Fetch data from API
data = fetch_data(api_url)

# Save data to TXT
txt_file_path = f'./documents/price_{fileday}.txt'
save_to_txt(data, txt_file_path)

# Upload TXT file to knowledge base
knowledge_base_name = '铜铝知识'
token = 'ragflow-VhMDExMjJjOGM1YzExZWY5N2M5MDI0Mm'  # Replace with your actual knowledge base API token
upload_file_to_kb(txt_file_path, knowledge_base_name, token)
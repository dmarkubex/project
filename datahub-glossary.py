import requests
import json

# 定义请求 URL
url = "http://10.1.10.43:9002/openapi/v3/entity/glossaryterm?start=0&count=100"

# 定义请求头，包含 API 令牌
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhY3RvclR5cGUiOiJVU0VSIiwiYWN0b3JJZCI6ImRhdGFodWIiLCJ0eXBlIjoiUEVSU09OQUwiLCJ2ZXJzaW9uIjoiMiIsImp0aSI6IjYxZmMxYjc5LTU3NTMtNDlkYy04NWIxLTM1MzNhNzQ4OWRhNiIsInN1YiI6ImRhdGFodWIiLCJleHAiOjE3MzM1NTQxMjksImlzcyI6ImRhdGFodWItbWV0YWRhdGEtc2VydmljZSJ9.Az6s1VRSiAzcYV60QrfD-Y3x_Rm-ZhRMECGrr_-AYlM"
}

# 发送 GET 请求
response = requests.get(url, headers=headers)

# 检查响应状态码
if response.status_code == 200:
    data = response.json()
    glossary_terms = data.get('entities', [])

    # 打印调试信息
    print(f"Total glossary terms: {len(glossary_terms)}")

    # 提取 name 和 definition 的内容
    extracted_data = []
    for term in glossary_terms:
        glossary_term_info = term.get('glossaryTermInfo', {}).get('value', {})
        name = glossary_term_info.get('name', 'N/A')
        definition = glossary_term_info.get('definition', 'N/A')
        extracted_data.append((name, definition))

        # 打印调试信息
        print(f"Extracted term: {name}, definition: {definition[:30]}...")

    # 打印提取的数据
    print("Extracted data:")
    for name, definition in extracted_data:
        print(f"指标名: {name}, 指标定义: {definition[:30]}...")

    # 生成 Markdown 内容
    markdown_content = ""
    for name, definition in extracted_data:
        markdown_content += f"### {name}\n\n{definition}\n\n"

    # 将 Markdown 内容写入文件
    with open("glossary_terms.md", "w", encoding="utf-8") as file:
        file.write(markdown_content)

    print("Markdown 内容已生成并保存为 glossary_terms.md")
else:
    print(f"请求失败，状态码: {response.status_code}")
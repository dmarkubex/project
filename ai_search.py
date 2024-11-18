import streamlit as st
import requests

# 设置页面标题
st.title("AI 搜索应用")

# 输入框用于输入搜索问题
question_input = st.text_input("请输入查询内容:")

# 设置 API 端点和请求头
api_url = "https://ai.fegroup.cn:8800/v1/chat-messages"
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer app-6MH9TZ4wWery2K2meNFWZKHQ'  # 替换为你的实际 token
}

# 清理输入
def clean_input(text):
    return text.strip()

# 调用API获取建议解决措施
def get_suggested_solution(question):
    ques = clean_input(question)
    query = f"{ques}"
    payload = {
        "inputs": {},
        "query": query,
        "response_mode": "blocking",
        "conversation_id": "",
        "user": "service-time",
        "files": []
    }
    response = requests.post(api_url, headers=headers, json=payload)
    return response

# 按钮用于触发搜索
if st.button("搜索"):
    # 发送请求到 API
    response = get_suggested_solution(question_input)
    
    # 检查响应状态码
    if response.status_code == 200:
        # 解析响应数据
        results = response.json()
        
        # 显示搜索结果
        with st.expander("搜索结果"):
            if "answer" in results:
                answer = results["answer"]
                st.markdown(answer)
            else:
                st.write("未找到相关结果。")
    else:
        st.write("搜索失败，请检查 API 配置。")
        st.write(f"状态码: {response.status_code}")
        st.write(f"响应内容: {response.text}")
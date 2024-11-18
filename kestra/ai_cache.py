import requests
import psycopg2

# Directus API 配置
directus_url = "https://directus.fegroup.cn:8055/items/ai_questions"
headers = {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN"  # 替换为你的 Directus 访问令牌
}

# PostgreSQL 配置
pg_config = {
    "dbname": "your_dbname",
    "user": "your_username",
    "password": "your_password",
    "host": "your_host",
    "port": "your_port"
}

def fetch_directus_data():
    response = requests.get(directus_url, headers=headers)
    response.raise_for_status()
    return response.json()["data"]

def insert_into_postgres(data):
    conn = psycopg2.connect(**pg_config)
    cursor = conn.cursor()
    
    for item in data:
        cursor.execute(
            """
            INSERT INTO ai_questions (id, question, answer) VALUES (%s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET question = EXCLUDED.question, answer = EXCLUDED.answer;
            """,
            (item["id"], item["question"], item["answer"])
        )
    
    conn.commit()
    cursor.close()
    conn.close()

def main():
    data = fetch_directus_data()
    insert_into_postgres(data)

if __name__ == "__main__":
    main()
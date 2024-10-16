import asyncio
from crawl4ai import AsyncWebCrawler

# 配置登录信息
login_url = "http://10.1.80.186/login"
username = "88440561@qq.com"
password = "Dkyo198246@"

# 配置抓取目标
target_url = "http://10.1.80.186/fe-group/projects/fa977426-9a67-45d2-a510-e20c5c66b430/issues/"

async def main():
    # 使用async with语句来管理AsyncWebCrawler实例
    async with AsyncWebCrawler(verbose=True) as crawler:
        # 登录
        login_payload = {
            "username": username,
            "password": password
        }
        await crawler.arun(url=login_url, method="POST", data=login_payload)

        # 抓取目标页面
        result = await crawler.arun(url=target_url)

        # 处理抓取到的数据
        print("抓取成功")
        print(result.markdown)

# 运行异步主函数
asyncio.run(main())
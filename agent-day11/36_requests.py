import requests

# 💡 极其拟人化：一行直接拿到响应对象（而且是同步阻塞式的，天然不需要写 await！）
# response = requests.get("https://api.github.com/users/octocat")
# print(response.status_code)  # 打印出原始的文本/JSON 字符串
# print("=" * 50)
# print(response.json())
# print("=" * 50)
# print(response.raise_for_status())

url = "https://api.github.com/search/repositories"

# 🌟 1. 组装查询参数 (对齐 Axios 的 params)
# 最终拼装出的 URL 会自动变成: ...?q=nextjs&sort=stars
query_params = {
    "q": "nextjs",
    "sort": "stars"
}

# 🌟 2. 组装请求头 (对齐 Axios 的 headers)
custom_headers = {
    "Authorization": "Bearer YOUR_GITHUB_TOKEN_HERE",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "SaaS-Agent-Platform" # GitHub API 强制要求传入 User-Agent
}

# 🌟 3. 发射请求
res = requests.get(url, params=query_params, headers=custom_headers)
print(f"HTTP 状态码: {res.status_code}")
print("=" * 50)
print(f"响应头: {res.headers}")
print("=" * 50)
print(f"响应体: {res.json()}")  # 自动解析 JSON
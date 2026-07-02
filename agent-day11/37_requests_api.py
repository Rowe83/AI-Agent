import requests

def invoke_ai_gateway():
    # 模拟一个符合 OpenAI/DeepSeek 标准的 Mock API 终结点
    # 💡 提示：这是一家提供测试的真实合法的 HTTP 响应沙箱
    api_url = "https://httpbin.org/post"

    # 1. 配置合规鉴权请求头
    headers = {
        "Authorization": "Bearer sk-deepseek-mock-key-666",
        "User-Agent": "SaaS-Frontend-Agent-V15"
    }

    # 2. 组装需要提交的 JSON 格式 Payload（剧本）
    payload = {
        "model": "deepseek-reasoner",
        "messages": [
            {"role": "user", "content": "请对 components/Navbar.tsx 提出首屏闪烁(Flicker)重构建议。"}
        ],
        "temperature": 0.0,
        "stream": False
    }

    print("📡 正在向 AI 智能网关发射 POST 请求...")
    print("-" * 60)

    try:
        # 🌟 核心一枪：必须使用 json= 参数，死死锁住 application/json 传输协议！
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        
        # 🌟 熔断卫语句：如果后端挂了（如 502/401），立刻抛出异常，绝不带病运行
        response.raise_for_status()
    except ValueError as ve:
        print(f"🛑 [数据层爆破] JSON 解析失败: {ve}")
        return
    except KeyError as ke:
        print(f"🛑 [数据层爆破] 关键字段缺失: {ke}")
        return
    except requests.exceptions.RequestException as error:
        print(f"🛑 [网络层爆破] 请求遭遇灾难性失败: {error}")
        return

    # 3. 拦截解析状态码
    print(f"🟢 网关响应成功！状态码: {response.status_code}")
    
    # 4. 解析 JSON 数据
    # 因为我们发给了 httpbin.org，它会把我们发送的请求原封不动地包裹在 "json" 键里返回回来
    raw_response_dict = response.json()
    
    # 提取我们刚刚发过去的 model，验证网关链路的原子完整性
    echo_model = raw_response_dict.get("json", {}).get("model", "UNKNOWN")
    echo_headers = raw_response_dict.get("headers", {})
    
    print("\n📦 [网关返回报文审计结果]：")
    print(f"  - 目标识别模型 : {echo_model}")
    print(f"  - 校验请求头   : Content-Type -> {echo_headers.get('Content-Type')}")
    print(f"  - 鉴权令牌快照 : {echo_headers.get('Authorization')}")
    print("-" * 60)
    print("🎉 链路全线打通，Agent 网络接入成功！")

if __name__ == "__main__":
    invoke_ai_gateway()
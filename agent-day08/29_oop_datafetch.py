import json
from typing import Dict, Any, Optional

class DataFetcher:
    """
    通用数据抓取基类 (对比 TS 的 class DataFetcher)
    """
    # 类属性（相当于 JS 的 static 属性，由所有实例共享）
    USER_AGENT: str = "AgentLearningBot/1.0"

    def __init__(self, base_url: str, timeout: int = 10):
        """
        构造方法 (对应 JS 的 constructor)
        """
        self.base_url: str = base_url.rstrip("/")  # 实例属性
        self.timeout: int = timeout
        # 约定俗成的“私有属性”（受保护属性），外部不应该直接访问
        self._headers: Dict[str, str] = {
            "User-Agent": self.USER_AGENT,
            "Content-Type": "application/json"
        }

    def _build_url(self, endpoint: str) -> str:
        """内部辅助方法：拼接 URL"""
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def handle_response(self, response_data: str) -> Dict[str, Any]:
        """
        解析响应数据（可由子类重写）
        """
        try:
            return json.loads(response_data)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON status", "raw": response_data}


class LLMApiFetcher(DataFetcher):
    """
    大模型 API 专属抓取器，继承自 DataFetcher (对应 class LLMApiFetcher extends DataFetcher)
    """
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        # 调用父类构造函数 (对应 super())
        super().__init__(base_url, timeout)
        self.api_key: str = api_key
        
        # 为大模型请求定制更新 Headers
        self._headers.update({
            "Authorization": f"Bearer {self.api_key}"
        })

    def handle_response(self, response_data: str) -> Dict[str, Any]:
        """
        方法重写 (Override)：定制大模型的响应解析逻辑
        """
        # 先调用父类的通用解析
        parsed = super().handle_response(response_data)
        if "error" in parsed:
            return parsed
        
        # 模拟大模型特定字段提取
        return {
            "success": True,
            "reply": parsed.get("choices", [{}])[0].get("message", {}).get("content", ""),
            "usage": parsed.get("usage", {})
        }

    def simulate_post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        模拟发起 POST 请求（明天第8天会正式学 requests 库，今天先用 mock 数据跑通 OOP 流程）
        """
        full_url = self._build_url(endpoint)
        print(f"[MOCK POST] Sending to {full_url} with headers: {list(self._headers.keys())}")
        
        # 模拟真实的 OpenAI 格式返回
        mock_raw_response = """
        {
            "choices": [{"message": {"content": "你好！我是AI助手，很高兴为你服务。"}}],
            "usage": {"total_tokens": 42}
        }
        """
        return self.handle_response(mock_raw_response)


# ===== 测试运行 =====
if __name__ == "__main__":
    print("--- 开始测试 Python OOP ---")
    
    # 实例化子类
    ai_client = LLMApiFetcher(
        base_url="https://api.openai.com/v1", 
        api_key="sk-mock-123456"
    )
    
    # 调用模拟请求
    result = ai_client.simulate_post(
        endpoint="/chat/completions", 
        payload={"model": "gpt-4o", "messages": []}
    )
    
    print("\n最终解析出来的 AI 回复:")
    print(result["reply"])
    print(f"Token 消耗: {result['usage']}")
from langchain_core.tools import tool

@tool
def get_stock_price(symbol: str) -> str:
    """获取指定股票的实时股价信息。

    Args:
        symbol: 股票代码，如 "NVDA" 或 "AAPL"
    Returns:
        股票的实时股价信息，如 "NVIDIA 实时股价为 $125.50 (上涨 +1.25%)" 或 "苹果公司实时股价为 $150.75 (上涨 +0.50%)"
    """
    mock_db = {
        "NVDA": "NVIDIA 实时股价为 $125.50 (上涨 +1.25%)",
        "AAPL": "苹果公司实时股价为 $150.75 (上涨 +0.50%)"
    }
    return mock_db.get(symbol.upper(), "未找到该股票信息")

print(get_stock_price.invoke("NVDA"))
print(f"工具名称：{get_stock_price.name} \n")
print(f"工具描述：{get_stock_price.description} \n")
print(f"工具参数：{get_stock_price.args} \n")
# src/aggregator/utils.py
import csv
from pathlib import Path
from typing import List, Dict, Any

def clean_and_flatten_data(weather: Dict[str, Any], news: Dict[str, Any], exchange: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    将三个异构 API 返回的复杂嵌套数据进行打平（Flatten）与清洗
    """
    cleaned_rows: List[Dict[str, Any]] = []
    
    # 1. 解析天气 (来自 httpbin 的 echo 数据或模拟结构)
    # 运用 dict.get() 防御 KeyError
    city = weather.get("json", {}).get("city", "UNKNOWN").strip().upper()
    temp = float(weather.get("json", {}).get("temp", 0.0))
    
    # 2. 解析新闻列表 (提取前 2 条)
    articles = news.get("json", {}).get("articles", [])[:2]
    
    # 3. 解析汇率
    usd_to_cny = float(exchange.get("json", {}).get("rate", 7.25))

    # 4. 交叉捏合组装
    for art in articles:
        cleaned_rows.append({
            "City": city,
            "Temperature_C": temp,
            "Headline": art.get("title", "").replace("闪烁", "").strip(),
            "News_Source": art.get("source", "REUTERS"),
            "USD_CNY_Rate": usd_to_cny
        })
        
    return cleaned_rows


def export_to_audit_log(data_rows: List[Dict[str, Any]]) -> None:
    """
    将打平后的数据流式写入本地 CSV 报表
    """
    if not data_rows:
        return
        
    # 跨平台定位到项目根目录下的 report.csv
    output_path = Path(__file__).resolve().parents[2] / "global_dashboard_report.csv"
    headers = ["City", "Temperature_C", "Headline", "News_Source", "USD_CNY_Rate"]
    
    # 显式锁死 newline="" 和 encoding="utf-8" 防翻车
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data_rows)
        
    print(f"💾 [IO 系统] 聚合数据已成功固化至: {output_path.name}")
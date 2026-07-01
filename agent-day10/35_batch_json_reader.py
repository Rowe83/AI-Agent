import json
from pathlib import Path
from typing import Dict, Any, List

def batch_load_json_files(dir_name: str, new_dir: str) -> List[Dict[str, Any]]:
    """
    批量读取指定文件夹内的所有 JSON 文件，并将其转化为对象列表返回
    """
    base_dir = Path.cwd()
    target_dir = base_dir / dir_name
    new_dir_path = base_dir / new_dir
    
    
    # 如果目录不存在，先创建它，方便我们模拟测试
    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 已自动创建空目录: {dir_name}，请往里放入 JSON 文件。")
        return []

    results: List[Dict[str, Any]] = []
    
    # 计数器
    success_count = 0
    failure_count = 0

    print(f"🚀 开始扫描目录下的 JSON 文件: {target_dir}")
    
    # 使用 pathlib 的 rglob("*.json") 可以递归扫描子目录，这里用 glob("*.json") 只扫描当前层
    json_files = list(target_dir.glob("*.json"))

    if not json_files:
        print("⚠️ 未找到任何 .json 文件。")
        return []

    for file_path in json_files:
        # file_path 是一个 Path 对象
        try:
            # 1. 优雅读取文本
            content = file_path.read_text(encoding="utf-8")
            
            # 2. 解析 JSON (等同于 JS 的 JSON.parse)
            data = json.loads(content)
            
            # 3. 注入元数据：把文件名也存进去，方便溯源
            if isinstance(data, dict):
                data["_source_file"] = file_path.name
                results.append(data)
            elif isinstance(data, list):
                # 如果 JSON 根节点是数组，追加标记后整体存入
                results.append({"data": data, "_source_file": file_path.name})
                
            success_count += 1
            
        except json.JSONDecodeError as je:
            print(f"❌ 语法错误！文件 [{file_path.name}] 不是合法的 JSON 格式: {je}")
            failure_count += 1
        except Exception as e:
            print(f"❌ 读取文件 [{file_path.name}] 失败: {e}")
            failure_count += 1

    print("\n" + "="*30)
    print(f"📊 处理报告: 成功 {success_count} 个, 失败 {failure_count} 个")
    print("="*30)

    with open(new_dir_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return results

# ===== 模拟数据准备与测试 =====
def generate_mock_data(dir_name: str):
    """辅助函数：在本地快速生成几个测试文件，包含一个坏掉的 JSON"""
    mock_path = Path.cwd() / dir_name
    mock_path.mkdir(exist_ok=True)
    
    # 1. 正常的 Agent 配置
    with open(mock_path / "agent_weather.json", "w", encoding="utf-8") as f:
        json.dump({"agent_name": "WeatherBot", "tools": ["get_temperature"]}, f, indent=2)
        
    # 2. 正常的 Prompt 模板
    with open(mock_path / "prompt_summary.json", "w", encoding="utf-8") as f:
        json.dump({"template_name": "summary", "max_tokens": 500}, f, indent=2)
        
    # 3. 一个故意写错、格式损坏的 JSON 文件（少了大括号）
    broken_file = mock_path / "broken_data.json"
    broken_file.write_text("{ 'name': 'broken', 'age': ", encoding="utf-8")


if __name__ == "__main__":
    folder = "agent_configs"
    
    # 先生成测试数据
    generate_mock_data(folder)
    
    # 执行批量读取
    all_configs = batch_load_json_files(folder, "batch_load_report.json")
    
    print("\n🔥 最终读取到的成功数据流:")
    print(json.dumps(all_configs, indent=2, ensure_ascii=False))
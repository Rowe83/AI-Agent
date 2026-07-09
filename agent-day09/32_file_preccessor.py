import json
from pathlib import Path

def merge_json_files(input_dir_name: str, output_file_name: str) -> None:
    """
    扫描 input_dir_name 目录下的所有 json 文件，合并输出到 output_file_name
    """
    # 1. 建立基础路径对象（相对于当前工作目录）
    base_dir = Path.cwd()
    target_dir = base_dir / input_dir_name
    output_path = base_dir / output_file_name

    # 自动创建模拟用的测试文件夹
    target_dir.mkdir(exist_ok=True)
    
    # 2. 模拟创建两个 JSON 文件供测试（使用 with 写入）
    with open(target_dir / "plugin_weather.json", "w", encoding="utf-8") as f:
        json.dump({"name": "weather", "version": "1.0", "desc": "查询天气"}, f, ensure_ascii=False, indent=2)
    with open(target_dir / "plugin_search.json", "w", encoding="utf-8") as f:
        json.dump({"name": "search", "version": "2.0", "desc": "谷歌搜索"}, f, ensure_ascii=False, indent=2)

    print(f"📂 正在扫描目录: {target_dir}")
    
    merged_data = []

    # 3. 遍历文件夹：使用 glob 匹配所有 .json 文件 (相当于前端的 globby / tiny-glob)
    for file_path in target_dir.glob("*.json"):
        print(f"✨ 发现 JSON 文件: {file_path.name}")
        
        # 使用 pathlib 提供的便捷方法直接读取文本，并用 json 解析
        try:
            content = file_path.read_text(encoding="utf-8")
            data = json.loads(content)
            merged_data.append(data)
        except Exception as e:
            print(f"❌ 读取 {file_path.name} 失败: {e}")

    # 4. 将合并后的结果安全写入新文件
    with open(output_path, "w", encoding="utf-8") as f:
        # indent=4 让 JSON 美化输出，ensure_ascii=False 保证中文不乱码
        json.dump(merged_data, f, indent=4, ensure_ascii=False)
    
    print(f"✅ 合并完成！结果已保存至: {output_path}")

if __name__ == "__main__":
    # 执行合并任务
    merge_json_files(input_dir_name="mock_configs", output_file_name="combined_config.json")
import csv
from pathlib import Path
from typing import List, Dict

def run_csv_pipeline():
    base_dir = Path.cwd()
    input_csv = base_dir / "llm_tasks.csv"
    output_csv = base_dir / "llm_results.csv"

    # ==========================================
    # 步骤 1: 模拟创建初始的 CSV 任务数据集
    # ==========================================
    headers = ["task_id", "prompt_template", "user_input"]
    mock_tasks = [
        {"task_id": "101", "prompt_template": "请将以下文本翻译成英文：", "user_input": "今天天气真好"},
        {"task_id": "102", "prompt_template": "提取这段话的关键实体：", "user_input": "小明在2026年加入了微软。"},
        {"task_id": "103", "prompt_template": "判断以下评论的情感倾向：", "user_index": "这东西太难用了！"}  # 故意写错一个key测试兼容性
    ]

    # 写入 CSV（注意：newline="" 是 Python 读写 CSV 的标准防空行牛皮癣写法）
    with open(input_csv, "w", encoding="utf-8", newline="") as f:
        # 初始化 DictWriter，显式指定表头
        writer = csv.DictWriter(f, fieldnames=headers)
        # 写入表头行
        writer.writeheader()
        # 批量写入数据行（它会自动过滤掉多余的 key，补齐缺少的 key）
        for task in mock_tasks:
            # 过滤出符合 headers 的字典，防止报错
            safe_row = {k: task.get(k, "") for k in headers}
            writer.writerow(safe_row)

    print(f"📝 成功创建测试任务集: {input_csv.name}")

    # ==========================================
    # 步骤 2: 读取 CSV 并模拟大模型处理
    # ==========================================
    processed_results: List[Dict[str, str]] = []

    with open(input_csv, "r", encoding="utf-8", newline="") as f:
        # 使用 DictReader 读取，自动把第一行作为 key
        reader = csv.DictReader(f)
        
        # 打印检测到的表头：等同于 JS 里的 Object.keys
        print(f"📊 检测到 CSV 表头字段: {reader.fieldnames}")

        for row in reader:
            # 此时的 row 是一个 dict 结构
            task_id = row["task_id"]
            full_prompt = f"{row['prompt_template']}\n输入: {row['user_input']}"
            
            print(f"🤖 正在处理任务 [{task_id}]...")
            
            # 模拟大模型处理（后面会换成真正的 API 请求）
            mock_ai_response = f"[Mock AI 回复] 已处理任务 {task_id} 的输入。"
            
            # 把生成的结果追加到原字典中（等同于 JS 的 {...row, ai_response}）
            row["ai_response"] = mock_ai_response
            row["status"] = "SUCCESS"
            processed_results.append(row)

    # ==========================================
    # 步骤 3: 将包含 AI 结果的数据写入新的 CSV
    # ==========================================
    # 新的 CSV 需要加入额外的两个字段
    output_headers = headers + ["ai_response", "status"]

    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=output_headers)
        writer.writeheader()
        writer.writerows(processed_results) # 批量写入多行

    print(f"✅ 任务全部执行完成！结果已导出至: {output_csv.name}")

if __name__ == "__main__":
    run_csv_pipeline()
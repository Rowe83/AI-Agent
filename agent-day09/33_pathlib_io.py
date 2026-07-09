import json
from pathlib import Path

def initialize_and_clean():
    # 🌟 1. 定位当前脚本所在的绝对路径，并锁定项目根目录
    current_file = Path(__file__).resolve() # 获取当前文件的绝对物理路径
    base_dir = current_file.parent          # 定位到当前脚本所在文件夹
    
    print(f"📁 脚本物理绝对路径: {current_file}")
    print(f"🏠 项目总线根目录: {base_dir}")

    # 🌟 2. 运用 / 运算符动态组装跨平台的嵌套目录
    storage_dir = base_dir / "storage"
    input_dir = storage_dir / "raw_cv"
    output_dir = storage_dir / "processed_cv"

    # 🌟 3. 一键安全创建目录 (对齐 mkdir -p)
    # parents=True: 如果父目录不存在，连同父目录一起递归创建
    # exist_ok=True: 如果目录已经存在，静默跳过，不报错
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    print("✅ [IO 系统] 跨平台目标存储目录树初始化/校验完毕。")

    # --- 模拟写入一个测试用的脏 JSON 简历文件 ---
    mock_input_file = input_dir / "cv_alex.json"
    dirty_data = {"name": "   Alex Frontend Lead 闪烁闪烁   ", "role": "Fullstack"}
    
    # pathlib 核心大招：可以直接调用 .write_text() 快速写文件，不需要写 with open！
    mock_input_file.write_text(json.dumps(dirty_data, ensure_ascii=False), encoding="utf-8")

    # 🌟 4. 读取、清洗、并安全迁移写入到 output 目录
    target_output_file = output_dir / f"cleaned_{mock_input_file.name}"
    
    if mock_input_file.exists() and mock_input_file.is_file():
        # 同样，可以用 .read_text() 一键读取文件内容字符串
        raw_content = mock_input_file.read_text(encoding="utf-8")
        data = json.loads(raw_content)
        
        # 核心清洗业务逻辑
        data["name"] = data["name"].strip().replace("闪烁闪烁", "")
        
        # 将清洗完的数据写入到 processed_cv 目录
        target_output_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        
        print("\n🎉 [清洗流水线大获全胜]")
        print(f"📦 原始文件位置: {mock_input_file}")
        print(f"🚀 清洗后新位置: {target_output_file}")
        print(f"📝 最终清洗后盘面数据: {data}")

# 执行流水线
if __name__ == "__main__":
    initialize_and_clean()
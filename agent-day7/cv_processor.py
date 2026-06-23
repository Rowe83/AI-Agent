# cv_processor.py

def clean_resume_text(text: str) -> str:
    """公共工具函数：清洗简历文本"""
    return text.strip().replace("闪烁闪烁", "")

# 🌟 核心拦截守卫
if __name__ == "__main__":
    print("🚨 [本地测试] 监测到当前文件正在被【直接独立运行】！")
    # 这段测试代码只在我写这个文件、想本地肉眼测一下对错时才跑
    test_raw = "   Alex_Frontend_Lead 闪烁闪烁   "
    print(f"🧪 本地测试清洗结果: '{clean_resume_text(test_raw)}'")
    print(f"ℹ️ 此时的 __name__ 变量真实值是: {__name__}")

if __name__ == "cv_processor":
    print("🚨 [模块导入] 监测到当前文件正在被【外部 import】！")
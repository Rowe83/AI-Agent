# main_app.py
# 🎯 像前端 import 一样，直接导入公共模块中的函数
from cv_processor import clean_resume_text

print("🚀 [主程序] 主业务线逻辑启动...")

user_input = "   Next.js 15 Fullstack 闪烁闪烁 "
final_result = clean_resume_text(user_input)

print(f"🎯 经过外部 Module 渲染后的结果: '{final_result}'")
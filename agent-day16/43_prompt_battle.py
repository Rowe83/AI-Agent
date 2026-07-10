import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url=os.getenv("BASE_URL"))

# 💥 实验沙箱目标：一段带有首屏切换闪烁（Flicker）Bug 的糟糕组件描述
dirty_frontend_log = "那个导航栏组件在切换路由时页面会闪烁一下，非常难受，而且还会报错。"

# =====================================================================
# 🛸 5 种不同的 Prompt 风格演练矩阵
# =====================================================================

# 1. 模糊指令 (垃圾进，垃圾出)
prompt_1_vague = f"帮我分析一下这个前端问题：{dirty_frontend_log}"

# 2. 结构化清晰指令 (带人设、任务、约束)
prompt_2_clear = f"""
你是一个专业的资深前端架构师。
任务：请分析以下用户报修的前端 Bug 描述，并给出一针见血的重构建议。
Bug描述：{dirty_frontend_log}
约束：回答字数严格控制在 50 字以内。
"""

# 3. Zero-shot + JSON 强控
prompt_3_json_mode = f"""
你是一个自动化日志清洗 Agent。请将以下 Bug 描述转化为标准的结构化 JSON 对象。
输入数据：{dirty_frontend_log}

目标 JSON 格式：
{{
  "component": "受影响的组件名",
  "root_cause": "根本原因猜测",
  "severity": "HIGH/MID/LOW"
}}
"""

# 4. Few-shot (少样本神仙带路)
prompt_4_few_shot = f"""
你是一个高性能前端 Bug 分类专家。请模仿以下示例，对最新的输入进行结构化分析，并以 JSON 格式输出。

[示例1]
输入：页面列表加载时，图片总是一下子跳出来，布局乱动。
输出：{{"component": "Image_List", "root_cause": "未设置宽高占位导致的 DOM 抖动", "severity": "MID"}}

[示例2]
输入：点击提交按钮后没有 Loading，用户连续点了 5 次导致重复扣款。
输出：{{"component": "Submit_Button", "root_cause": "缺少防抖/节流及防重复点击熔断机制", "severity": "HIGH"}}

[最新输入]
输入：{dirty_frontend_log}
输出："""

# =====================================================================
# 📡 核心发射总线
# =====================================================================
def test_prompt_style(style_name: str, prompt_text: str, enforce_json: bool = False):
    print(f"\n🚀 [测试风格]: {style_name}")
    print("-" * 60)
    
    # 动态组装网关配置参数
    extra_args = {}
    if enforce_json:
        # 🌟 强制拉起大模型底层 JSON Mode 阻击盾牌
        extra_args["response_format"] = {"type": "json_object"}
        
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt_text}],
            temperature=0.0,  # 锁死生产级精度
            **extra_args
        )
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"🛑 通信爆破: {e}")
    print("=" * 60)

if __name__ == "__main__":
    print("🎬 开启 2026 工业级 Prompt Engineering 效果大审计...")
    
    # 运行 1：模糊指令（通常会返回一段长长的、充满客套话和废话的自然语言）
    # test_prompt_style("1. 模糊指令 (Vague)", prompt_1_vague)
    
    # # 运行 2：结构化约束（字数明显收敛，直击痛点）
    # test_prompt_style("2. 结构化清晰指令 (Clear & Constrained)", prompt_2_clear)
    
    # # 运行 3：JSON Mode 强控（吐出的必然是标准 JSON 字符串）
    # test_prompt_style("3. Zero-shot + JSON Mode 强控", prompt_3_json_mode, enforce_json=True)
    
    # 运行 4：Few-shot 降维打击（输出格式会极其精准、利落，完全对齐示例的风格）
    test_prompt_style("4. Few-shot (少样本神仙带路)", prompt_4_few_shot, enforce_json=True)
"""
项目结构图谱生成器
生成 AI-Agent 学习路线的可视化 PNG 图谱
"""
import matplotlib
matplotlib.use('Agg')  # 非交互式后端，直接输出文件
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import os

# ── 项目数据结构 ──────────────────────────────────────────────
PROJECT_ROOT = "AI-Agent"

DAYS = [
    {
        "name": "Day 1",
        "title": "基础入门",
        "color": "#4CAF50",
        "files": ["01_hello_streaming.py", "02_hello.py", "03_calculator.py", "04_type.py", "main.py"],
        "tags": ["LLM流式输出", "变量/类型", "基础运算"]
    },
    {
        "name": "Day 2",
        "title": "字符串操作",
        "color": "#2196F3",
        "files": ["05_string_master.py", "06_safe_cast.py", "07_string_practice.py"],
        "tags": ["字符串切片", "类型转换", "格式化"]
    },
    {
        "name": "Day 3",
        "title": "核心数据结构",
        "color": "#FF9800",
        "files": ["08_list_agent.py", "09_tuple.py", "10_tuple_agent.py", "11_dict_router.py", "12_set_filter.py"],
        "tags": ["List", "Tuple", "Dict", "Set"]
    },
    {
        "name": "Day 4",
        "title": "JSON 数据处理",
        "color": "#9C27B0",
        "files": ["13_json.py", "14_json_handler.py", "15_json_file.py",
                  "16_nested_traversal.py", "17_nested_func.py", "18_github_data.py"],
        "tags": ["JSON解析", "嵌套遍历", "GitHub API数据"]
    },
    {
        "name": "Day 5",
        "title": "流程控制",
        "color": "#F44336",
        "files": ["19_condition_router.py", "20_loop_master.py", "21_while_agent.py"],
        "tags": ["if/elif", "for循环", "while循环"]
    },
    {
        "name": "Day 6",
        "title": "函数进阶",
        "color": "#00BCD4",
        "files": ["22_invoke_llm.py", "23_function_master.py", "24_lambda.py",
                  "25_map_filter.py", "26_zip.py", "27_high_order_funcs.py"],
        "tags": ["Lambda", "Map/Filter", "Zip", "高阶函数", "LLM调用"]
    },
    {
        "name": "Day 7",
        "title": "综合项目实战",
        "color": "#795548",
        "files": ["cv_processor.py", "functions.py", "main.py", "main_app.py"],
        "tags": ["简历解析", "模块化", "项目结构"]
    },
    {
        "name": "Day 8",
        "title": "面向对象编程",
        "color": "#607D8B",
        "files": ["28_class_agent.py", "29_oop_datafetch.py", "30_class_static.py", "31_class_attr.py"],
        "tags": ["Class", "继承", "静态方法", "类属性"]
    },
    {
        "name": "Day 9",
        "title": "文件 I/O",
        "color": "#E91E63",
        "files": ["32_file_preccessor.py", "33_pathlib_io.py", "34_csv_processor.py"],
        "tags": ["文件读写", "Pathlib", "CSV处理"]
    },
    {
        "name": "Day 10",
        "title": "批量处理",
        "color": "#3F51B5",
        "files": ["35_batch_json_reader.py"],
        "tags": ["批量JSON", "异常容错", "报告输出"]
    },
    {
        "name": "Day 11",
        "title": "网络与日志",
        "color": "#FF5722",
        "files": ["36_requests.py", "37_requests_api.py", "38_logging.py", "39_defense_system.py"],
        "tags": ["HTTP请求", "API调用", "日志系统", "防御机制"]
    },
    {
        "name": "Day 12",
        "title": "类型注解",
        "color": "#009688",
        "files": ["40_type_hints.py"],
        "tags": ["Type Hints", "PEP 8", "Union/Optional"]
    },
]


def draw_day_block(ax, x, y, day, day_width=1.8, day_height_base=0.35, file_height=0.22):
    """绘制单天的卡片（标题 + 文件列表 + 标签）"""
    color = day["color"]
    n_files = len(day["files"])
    block_h = day_height_base + n_files * file_height + 0.15  # 标题 + 文件 + 底部标签区

    # 外框背景
    bg = FancyBboxPatch(
        (x - day_width / 2, y - block_h),
        day_width, block_h,
        boxstyle="round,pad=0.05",
        facecolor="white", edgecolor=color, linewidth=2, alpha=0.95,
        transform=ax.transData, zorder=2
    )
    ax.add_patch(bg)

    # 标题条
    title_bar = FancyBboxPatch(
        (x - day_width / 2, y - day_height_base),
        day_width, day_height_base,
        boxstyle="round,pad=0.03",
        facecolor=color, edgecolor="none", alpha=0.9,
        transform=ax.transData, zorder=3
    )
    ax.add_patch(title_bar)

    # 标题文字
    ax.text(
        x, y - day_height_base / 2,
        f"{day['name']}  ·  {day['title']}",
        ha="center", va="center", fontsize=8.5, fontweight="bold", color="white",
        transform=ax.transData, zorder=4
    )

    # 文件列表
    for i, f in enumerate(day["files"]):
        fy = y - day_height_base - 0.08 - i * file_height
        ax.text(
            x - day_width / 2 + 0.1, fy,
            f"  {f}",
            ha="left", va="center", fontsize=7, color="#333333",
            fontfamily="monospace",
            transform=ax.transData, zorder=4
        )

    # 标签
    tag_y = y - block_h + 0.07
    tag_text = "  |  ".join(day["tags"])
    ax.text(
        x, tag_y,
        tag_text,
        ha="center", va="center", fontsize=6.5, color=color, fontstyle="italic",
        transform=ax.transData, zorder=4
    )

    return (x, y, block_h)


def draw_connections(ax, root_x, root_y, day_positions):
    """从根节点画连线到每天卡片"""
    for (dx, dy, dh) in day_positions:
        ax.annotate(
            "",
            xy=(dx, dy),
            xytext=(root_x, root_y - 0.25),
            arrowprops=dict(
                arrowstyle="-",
                color="#AAAAAA",
                lw=1.2,
                connectionstyle="arc3,rad=0.0",
            ),
            zorder=1
        )


def generate_project_map(output_path):
    """生成完整项目图谱"""
    # ── 布局参数 ──
    cols = 4
    rows = 3  # 12天 / 4列
    x_gap = 2.1
    y_gap = 3.6

    fig_w = cols * x_gap + 1.5
    fig_h = rows * y_gap + 2.5

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(-0.5, fig_w - 1)
    ax.set_ylim(-0.5, fig_h - 0.5)
    ax.axis("off")
    fig.patch.set_facecolor("#F5F5F5")

    # ── 根节点 ──
    root_x = (fig_w - 1.5) / 2
    root_y = fig_h - 1.2
    root_box = FancyBboxPatch(
        (root_x - 1.0, root_y - 0.28),
        2.0, 0.56,
        boxstyle="round,pad=0.08",
        facecolor="#1A1A2E", edgecolor="#E94560", linewidth=2.5, alpha=0.95,
        transform=ax.transData, zorder=5
    )
    ax.add_patch(root_box)
    ax.text(
        root_x, root_y,
        f"🤖  {PROJECT_ROOT}  学习路线图谱",
        ha="center", va="center", fontsize=12, fontweight="bold", color="white",
        transform=ax.transData, zorder=6
    )

    # ── 绘制每天卡片 ──
    day_positions = []
    for idx, day in enumerate(DAYS):
        col = idx % cols
        row = idx // cols
        x = 0.9 + col * x_gap
        y = root_y - 1.2 - row * y_gap
        pos = draw_day_block(ax, x, y, day)
        day_positions.append(pos)

    # ── 画连线 ──
    draw_connections(ax, root_x, root_y, day_positions)

    # ── 底部图例 ──
    legend_y = -0.25
    ax.text(
        root_x, legend_y,
        f"共 {len(DAYS)} 天  ·  {sum(len(d['files']) for d in DAYS)} 个 Python 脚本  ·  由 Qoder 自动生成",
        ha="center", va="center", fontsize=8, color="#888888", fontstyle="italic",
        transform=ax.transData, zorder=4
    )

    plt.tight_layout(pad=0.5)
    fig.savefig(output_path, dpi=180, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    print(f"✅ 图谱已保存至: {output_path}")
    print(f"   分辨率: 180 DPI  |  尺寸: {fig_w:.1f} x {fig_h:.1f} 英寸")


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(__file__), "..", "project_map.png")
    generate_project_map(os.path.abspath(output))

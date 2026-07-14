import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# 🌟 引入 rich 终端美化三驾马车
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

# 初始化富文本控制台
console = Console()

# =====================================================================
# 🗃️ 静态角色 System Prompt 托管区
# =====================================================================
ROLES = {
    "default": "你是一个全能的 AI 助手。说话简练，直奔主题。",
    "code": "你是一个顶级的前端架构师。拒绝任何客套话，代码必须附带严格的类型注解或 TypeScript 声明。",
    "writer": "你是一个爆款自媒体文案大师。擅长使用 Emoji 增加段落表现力，逻辑极具煽动性。",
}


class CLIChatbot:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("BASE_URL", "https://api.deepseek.com/v1")

        if not api_key:
            console.print(
                "[bold red]🛑 配置崩溃: 未在 .env 中检测到合规的 API Key，系统强行熔断！[/bold red]"
            )
            sys.exit(1)

        self.client = OpenAI(api_key=api_key, base_url=base_url)

        # 🌟 核心内部状态机内存
        self.current_role_name = "default"
        self.history = [{"role": "system", "content": ROLES["default"]}]

    def print_welcome_screen(self):
        """打印炫酷的系统启动看板"""
        grid = Table.grid(expand=True)
        grid.add_column(justify="center")
        grid.add_row("[bold cyan]🤖 AI NEXUS TERMINAL v2026[/bold cyan]")
        grid.add_row("[dim]基于 Python asyncio & Rich 架构构建[/dim]")

        menu_text = (
            "\n[bold yellow]快捷斜杠命令菜单：[/bold yellow]\n"
            "• [bold green]/role [name][/bold green] : 动态切换人设 (可选: default, code, writer)\n"
            "• [bold green]/reset[/bold green]        : 清空当前轮次上下文记忆\n"
            "• [bold green]/export[/bold green]       : 将本轮对话历史结构化固化至 JSON\n"
            "• [bold green]/exit[/bold green]         : 正常销毁状态机下班\n"
        )

        console.print(Panel(grid, border_style="cyan"))
        console.print(menu_text)

    def handle_command(self, raw_input: str) -> bool:
        """
        命令路由分流器。返回 True 代表这是一个命令已被消费，返回 False 代表是常规文本。
        """
        parts = raw_input.strip().split()
        cmd = parts[0].lower()

        if cmd == "/exit":
            console.print(
                "[bold yellow]👋 状态机已安全退出。再见，架构师！[/bold yellow]"
            )
            sys.exit(0)

        elif cmd == "/reset":
            self.history = [
                {"role": "system", "content": ROLES[self.current_role_name]}
            ]
            console.print(
                f"[bold magenta]🧹 [内存系统] 当前角色【{self.current_role_name}】的上下文记忆已全部洗涤清空！[/bold magenta]"
            )
            return True

        elif cmd == "/role":
            if len(parts) < 2 or parts[1] not in ROLES:
                console.print(
                    f"[bold red]❌ 语法错误！可用角色名: {list(ROLES.keys())}[/bold red]"
                )
                return True

            target_role = parts[1]
            self.current_role_name = target_role
            # 💡 避坑动作：切换角色必须洗涤上下文，重置置顶的 System Prompt
            self.history = [{"role": "system", "content": ROLES[target_role]}]
            console.print(
                Panel(
                    f"🎯 [灵魂重塑] 角色已成功切入: [bold cyan]{target_role.upper()}[/bold cyan]\n历史上下文已重置。",
                    border_style="magenta",
                )
            )
            return True

        elif cmd == "/export":
            output_file = (
                Path(__file__).resolve().parent
                / f"chat_history_{int(time.time())}.json"
            )
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            console.print(
                f"💾 [IO 系统] 对话历史已成功流式固化至: [bold underline green]{output_file.name}[/bold underline green]"
            )
            return True

        return False

    def stream_chat_response(self, user_text: str):
        """流式网络通信与逐字打字机渲染"""
        # 1. 压入状态机历史
        self.history.append({"role": "user", "content": user_text})

        console.print("\n[bold cyan]🤖 AI 正在解码 > [/bold cyan]", end="")

        try:
            # 2. 发起官方异步通道流
            stream = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=self.history,
                temperature=0.3,  # 控火平衡
                stream=True,
            )

            assistant_full_reply = ""
            # 3. 原生非阻塞打印，维持 rich 的色彩流
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    sys.stdout.write(delta)
                    sys.stdout.flush()
                    assistant_full_reply += delta
            print()  # 换行

            # 4. 回写状态机闭环
            self.history.append({"role": "assistant", "content": assistant_full_reply})

        except Exception as e:
            console.print(f"\n[bold red]🛑 [网关断开] 通信链路爆破: {e}[/bold red]")
            if self.history:
                self.history.pop()  # 弹出污染源

    def start_loop(self):
        """拉起终端无限事件循环"""
        self.print_welcome_screen()

        while True:
            try:
                # 捕获用户键盘流
                user_input = input(f"\n👤 工程师 [{self.current_role_name}] ❯ ").strip()
                if not user_input:
                    continue

                # 路由分流检查
                if user_input.startswith("/"):
                    if self.handle_command(user_input):
                        continue

                # 触发正规大模型发射
                self.stream_chat_response(user_input)

            except KeyboardInterrupt:
                # 捕获 Ctrl + C 优雅退出
                console.print(
                    "\n[bold yellow]⚠️ 检测到强行中断信号，正在安全落盘状态并退出...[/bold yellow]"
                )
                break


if __name__ == "__main__":
    bot = CLIChatbot()
    bot.start_loop()

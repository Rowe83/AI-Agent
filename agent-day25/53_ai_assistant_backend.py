import os
import sqlite3
import time
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI

# =====================================================================
# 🚀 1. 环境初始化与云端 SDK 绑定
# =====================================================================
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
base_url = os.getenv("BASE_URL", "https://api.deepseek.com/v1")

if not api_key:
    print("🛑 [熔断] 未在 .env 中找到 DEEPSEEK_API_KEY，系统拒绝拉起！")
    exit(1)

client = OpenAI(api_key=api_key, base_url=base_url)

# =====================================================================
# 🗄️ 2. SQLite 持久化数据库管理内核
# =====================================================================
DB_PATH = Path(__file__).resolve().parent / "chat_history.db"


def get_db_connection():
    """获取线程安全的 SQLite 物理数据库连接"""
    # 🌟 极其重要：check_same_thread=False 解决 FastAPI 多线程死锁问题
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # 允许像字典一样通过列名访问数据
    return conn


def init_db():
    """初始化数据库 Schema 结构表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp INTEGER NOT NULL
        )
    """
    )
    # 为 session_id 建立索引，大幅提升多轮历史提取效率
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_session ON messages(session_id)")
    conn.commit()
    conn.close()


# 物理冷启动建表
init_db()


# =====================================================================
# 📋 3. Pydantic 传输层数据协议（DTO）
# =====================================================================
class ChatRequest(BaseModel):
    session_id: str = Field(
        ...,
        min_length=1,
        description="会话隔离 ID（用户/房间维度）",
        examples=["session_user_001"],
    )
    message: str = Field(
        ...,
        min_length=1,
        description="用户本次提问的文本内容",
        examples=["解释什么是 SQLite"],
    )


class MessageItem(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    timestamp: int


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    history_length: int


# =====================================================================
# 🌐 4. FastAPI Web 应用基座
# =====================================================================
app = FastAPI(
    title="AI Assistant Backend Engine",
    description="2026 项目一：AI 问答助手后端持久化 API 网关",
    version="1.0.0",
)

# 开启跨域允许，为前端 GUI / React 接入打通物理防线
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# 📡 5. 核心 API 端点实现
# =====================================================================


# 🟢 API 1: 提问交互接口 (POST /chat)
@app.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="发送对话请求并获得 AI 智能回复",
)
async def chat_endpoint(payload: ChatRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1.1 从数据库抽取当前 session_id 的最近 10 条历史记忆（防止上下文超时越界）
    cursor.execute(
        "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT 10",
        (payload.session_id,),
    )
    raw_history = cursor.fetchall()

    # 因为是 DESC 排序，提取出来后需要倒序翻转回真实的时间线升序
    history_messages = [
        {"role": row["role"], "content": row["content"]}
        for row in reversed(raw_history)
    ]

    # 1.2 将用户本次发起的提问追加进上下文
    current_time = int(time.time())
    history_messages.append({"role": "user", "content": payload.message})

    # 1.3 插入系统级人设，构建完整的云端 Payload
    llm_payload_messages = [
        {"role": "system", "content": "你是一个高度专业、回答简明扼要的 AI 问答助手。"}
    ] + history_messages

    try:
        # 1.4 调用云端大模型 API
        response = client.chat.completions.create(
            model="deepseek-chat", messages=llm_payload_messages, temperature=0.3
        )
        ai_reply = response.choices[0].message.content

    except Exception as e:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"上游大模型服务失败: {str(e)}",
        )

    # 1.5 双向持久化落盘：将用户输入与 AI 答复存入 SQLite
    cursor.execute(
        "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (payload.session_id, "user", payload.message, current_time),
    )
    cursor.execute(
        "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (payload.session_id, "assistant", ai_reply, current_time),
    )
    conn.commit()
    conn.close()

    return ChatResponse(
        session_id=payload.session_id,
        reply=ai_reply,
        history_length=len(history_messages),
    )


# 🟢 API 2: 对话历史拉取接口 (GET /history)
@app.get(
    "/history",
    response_model=List[MessageItem],
    summary="拉取指定 session_id 的全量对话历史记录",
)
def get_chat_history(
    session_id: str = Query(..., min_length=1, description="会话隔离 ID"),
    limit: int = Query(20, ge=1, le=100, description="单次拉取最大条数"),
):
    """
    提供给前端进行历史消息渲染落盘的 RESTful 通道。
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, session_id, role, content, timestamp FROM messages WHERE session_id = ? ORDER BY id ASC LIMIT ?",
        (session_id, limit),
    )
    rows = cursor.fetchall()
    conn.close()

    # 序列化成 Pydantic 标准模型输出
    return [
        MessageItem(
            id=row["id"],
            session_id=row["session_id"],
            role=row["role"],
            content=row["content"],
            timestamp=row["timestamp"],
        )
        for row in rows
    ]


if __name__ == "__main__":
    import uvicorn

    # 启动应用，开启 8000 端口
    uvicorn.run(
        "53_ai_assistant_backend:app", host="127.0.0.1", port=8000, reload=True
    )

import uvicorn
from typing import Optional, List
from fastapi import FastAPI, Path, Query, HTTPException, status
from pydantic import BaseModel, Field, EmailStr

# =====================================================================
# 📋 1. 声明式 Pydantic 强类型骨架 (对齐 TS Interface / Zod)
# =====================================================================
class AgentTaskRequest(BaseModel):
    # 强制校验：任务标题不能为空，长度 3-50
    title: str = Field(..., min_length=3, max_length=50, description="智能体任务标题", examples=["审计导航栏组件Bug"])
    # 业务语义校验：任务紧急程度限制
    priority: str = Field("P2", pattern="^(P0|P1|P2|P3)$", description="紧急程度级别: P0-P3")
    # 类型安全校验：必须是合法的 Email 格式
    reporter_email: EmailStr = Field(..., description="报告人邮箱")
    # 可空字段声明
    max_tokens_limit: Optional[int] = Field(500, ge=100, le=4000, description="单次大模型熔断 Token 上限")

class TaskResponse(BaseModel):
    task_id: int
    title: str
    priority: str
    status: str = "PENDING"

# =====================================================================
# 🚀 2. 初始化 FastAPI 实例（定制 Swagger 规格说明书）
# =====================================================================
app = FastAPI(
    title="AI Nexus Dispatcher API",
    description="2026 全栈 Agent 智能任务调度分发中继网关",
    version="1.0.0",
    docs_url="/docs",  # 强定制 Swagger 文档路由
    redoc_url="/redocs"
)

# =====================================================================
# 📡 3. 核心路由矩阵设计
# =====================================================================

# 🟢 API 1: 极简健康检查 (GET)
@app.get("/health", status_code=status.HTTP_200_OK, summary="心跳与健康审计")
def health_check():
    """
    提供给 K8s / Vercel 的原子级无阻碍健康自检通道
    """
    return {"status": "healthy", "engine": "FastAPI ASGI", "version": "1.0.0"}


# 🟢 API 2: 路径参数 + 查询参数复合流 (GET /tasks/{task_id})
@app.get(
    "/tasks/{task_id}", 
    response_model=TaskResponse,
    summary="获取指定 Agent 任务状态"
)
def get_task_details(
    # Path: 强制约束路径参数必须 >= 1
    task_id: int = Path(..., ge=1, description="物理任务唯一自增 ID"),
    # Query: 查询参数，非必填，限制长度
    filter_tag: Optional[str] = Query(None, max_length=15, description="按照技术标签过滤，如 'react'")
):
    """
    通过路径参数精准命中内存/DB中的任务，并可选配合 Query Filter 参数进行视图裁剪。
    """
    if task_id > 1000:
        # 优雅触发 HTTP 404 熔断，绝不引发 Python 底层报错
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Task with ID {task_id} not found in Agent clusters."
        )
        
    return {
        "task_id": task_id,
        "title": f"Mock Task with tag [{filter_tag or 'None'}]",
        "priority": "P1",
        "status": "PROCESSING"
    }


# 🟢 API 3: 强类型 Payload 接收器 (POST /tasks)
@app.post(
    "/tasks", 
    response_model=TaskResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="创建并分发新的 Agent 任务"
)
async def create_agent_task(payload: AgentTaskRequest):
    """
    接收前端发送的复杂 JSON 报文。
    Pydantic 会在后台在 0.1 毫秒内完成全量格式清洗和类型拦截。
    """
    # 此时 payload 对象已经 100% 校验通过，可以像操作 Python 对象一样点出属性
    print(f"📥 [网关日志] 成功接收到来自 {payload.reporter_email} 的新任务: {payload.title}")
    
    # 模拟持久化落盘
    mock_new_id = 99
    
    return TaskResponse(
        task_id=mock_new_id,
        title=payload.title,
        priority=payload.priority,
        status="PENDING"
    )

if __name__ == "__main__":
    # 🌟 启动 Uvicorn ASGI 高性能 Web 服务，绑定本地 8000 端口
    uvicorn.run("51_fastapi_app:app", host="127.0.0.1", port=8000, reload=True)
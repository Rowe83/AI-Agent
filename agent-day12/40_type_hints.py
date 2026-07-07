from typing import List, Dict, Optional, Union
import logging

# [PEP 8] 全局常量全大写
MODULE_NAME = "RESUME_PARSER"


class ResumeMetricsExtractor:
    """[PEP 8] 类名采用大驼峰。这是一个带类型注解的高级解析类"""

    def __init__(self, agent_id: str, quota: int = 100):
        # [PEP 8] 实例属性使用蛇形命名，默认值等号两边不加空格
        self.agent_id: str = agent_id
        self.quota: int = quota

    def extract_skills(self, raw_text: str) -> List[str]:
        """提取简历技能，强制返回字符串列表"""
        if not raw_text.strip():
            return []
        # 模拟模型清洗
        return [skill.upper() for skill in ["react", "next.js", "python"]]

    def query_audit_status(self, task_id: Union[int, str]) -> Dict[str, Union[str, float]]:
        """[PEP 8] 方法之间留一空行。接收联合类型，返回字典结构"""
        return {
            "task_id": str(task_id),
            "status": "COMPLETED",
            "score": 98.5
        }

    def fetch_error_log(self, code: int) -> Optional[str]:
        """可能返回字符串，也可能返回 None"""
        if code == 200:
            return None
        return f"Error {code}: 大模型解析超时"


# [PEP 8] 顶层代码与类定义之间留出 2 个空行
def run_pipeline() -> None:
    # 实例化
    extractor = ResumeMetricsExtractor(agent_id="lead_7_agent")
    
    # 1. 测试 List 注解与完备的补全
    skills: List[str] = extractor.extract_skills("  Alex Frontend Lead ")
    print(f"📦 提取的技能集: {skills}")
    
    # 2. 测试 Union 注解
    report = extractor.query_audit_status(task_id="TASK-2026")
    print(f"📋 审计报告摘要: {report}")
    
    # 3. 测试 Optional 注解
    err: Optional[str] = extractor.fetch_error_log(code=502)
    if err is not None:
        print(f"🛑 捕获容灾错误: {err}")


if __name__ == "__main__":
    run_pipeline()
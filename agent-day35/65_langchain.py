import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableBranch

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

# PydanticOutputParser 用于将LLM的输出解析为Pydantic模型
class PersonInfo(BaseModel):
    name: str = Field(description="姓名")
    age: int = Field(description="年龄")
    skills: list[str] = Field(description="技能列表")

parser = PydanticOutputParser(pydantic_object=PersonInfo)

prompt_str = "从以下文本中提取任务信息。\n{format_instructions}\n文本：{text}"
prompt = PromptTemplate(
    template=prompt_str,
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

chain = prompt | llm | parser

person: PersonInfo = chain.invoke({
    "text": "张三, 25岁, 擅长Python, Java, SQL"
})

# print(person)

# 一、多步骤串联
step1_prompt = ChatPromptTemplate.from_template("提取以下文本的 3 个核心关键词：\n{text}")
step1_chain = step1_prompt | llm | StrOutputParser()

step2_prompt = ChatPromptTemplate.from_template("原始文本：{text}\n核心关键词：{keywords}\n基于上述信息写一句广告标语。")
step2_chain = step2_prompt | llm | StrOutputParser()

full_chain = (
    RunnablePassthrough.assign(keywords=step1_chain) | step2_chain
)

result = full_chain.invoke({"text": "这是一款主打轻薄和极速充电的高端智能手机。"})

# print(result)

# 二、数据格式转换
def clean_text(input_dict: dict) -> dict:
    raw_text = input_dict.get("text", "")
    cleaned = " ".join(raw_text.split())
    return {"text": cleaned}

transform_node = RunnableLambda(clean_text)

chain = transform_node | step1_chain

# print(chain.invoke({"text": "这是一款主打轻薄和极速充电的高端智能手机。"}))

# 三、条件分支路由
# 定义分类 Prompt
classify_prompt = ChatPromptTemplate.from_template("判断以下用户的反馈类型，只返回'投诉'或'建议'：\n{feedback}")
classify_chain = classify_prompt | llm | StrOutputParser()

# 定义分支链
complaint_chain = ChatPromptTemplate.from_template("对用户的投诉表达诚挚歉意并给出补偿方案：{feedback}") | llm | StrOutputParser()
suggestion_chain = ChatPromptTemplate.from_template("对用户的建议表示感谢并说明后续优化计划：{feedback}") | llm | StrOutputParser()
default_chain = ChatPromptTemplate.from_template("礼貌回复用户：{feedback}") | llm | StrOutputParser()

# 定义路由逻辑
router_branch = RunnableBranch(
    (lambda x: "投诉" in x["topic"], complaint_chain),
    (lambda x: "建议" in x["topic"], suggestion_chain),
    default_chain
)

# 组装完整链
main_chain = (
    RunnablePassthrough.assign(topic=classify_chain)
    | router_branch
)

res = main_chain.invoke({"feedback": "你们的手机屏幕显示效果很差，希望改进。"})
print(res)
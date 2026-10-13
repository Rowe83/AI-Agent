import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_classic.memory import ConversationBufferMemory, ConversationSummaryMemory, VectorStoreRetrieverMemory

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    temperature=0
)

# 1、全量缓冲区记忆
memory = ConversationBufferMemory(return_messages=True)

memory.save_context({"input": "你好，我叫小明"}, {"output": "你好，小明！很高兴认识你"})
memory.save_context({"input": "我喜欢吃苹果"}, {"output": "记下了，你喜欢吃苹果"})

history = memory.load_memory_variables({})
print(history["history"])

# 2、摘要压缩记忆
summary_memory = ConversationSummaryMemory(llm=llm, return_messages=True)

summary_memory.save_context(
    {"input": "我在北京工作，是一家公司的 Python 后端开发工程师，平时喜欢折腾大模型。"},
    {"output": "了解，您是在北京工作的 Python 后端工程师，对大模型很感兴趣。"}
)

summary_history = summary_memory.load_memory_variables({})

print("摘要压缩记忆：", summary_history["history"])

# 3、向量检索记忆
embeddings = OpenAIEmbeddings(
    model="embedding-3",
    api_key=os.getenv("ZHIPUAI_API_KEY"),
    base_url=os.getenv("ZHIPU_BASE_URL"),
)

vectorstore = InMemoryVectorStore(embeddings)

retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

vector_memory = VectorStoreRetrieverMemory(retriever=retriever)

vector_memory.save_context({"input": "我养了一只叫包子的猫"}, {"output": "记住了"})
vector_memory.save_context({"input": "我的车牌号是京A88888"}, {"output": "记住了"})
vector_memory.save_context({"input": "今天天气真不错"}, {"output": "是的"})

context = vector_memory.load_memory_variables({"prompt": "我的宠物叫什么名字？"})
print("检索到的记忆:\n", context["history"])
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from openai import OpenAI
import os
from openai import AzureOpenAI
# load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
from langchain_community.chat_models.tongyi import ChatTongyi

from typing import Optional

from pydantic import BaseModel, Field

# Define a Pydantic model for structured output
class Author(BaseModel):
    author_unit: list[str] = Field(
        ..., description="作者单位列表，例如institute, company等信息"
    )
  
client = OpenAI(
    # 如果没有配置环境变量，请用百炼API Key替换：api_key="sk-xxx"
    api_key = DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
# from langchain_community.chat_models.tongyi import ChatTongyi

qwen_vl = ChatTongyi(
    # 如果没有配置环境变量，请用百炼API Key替换：api_key="sk-xxx"
    api_key = os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model_name = "qwen-vl-max",
    
)
llm = AzureChatOpenAI(
    api_key=os.getenv("AZURE_OPENAI_CHAT_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_CHAT_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_CHAT_API_VERSION"),
    deployment_name="gpt-4o"
)

if __name__ == "__main__":
    # print(llm.invoke("你好"))
   # Bind the schema to the model
    model_with_structure = llm.with_structured_output(Author,include_raw=False,method="function_calling")
    # Invoke the model
    prompt = """以下是一篇文章的作者背景：
    1.国网北京朝阳供电公司2.国网北京客服中心3.国网北京市电力公司
    请从中提取出作者单位，例如institute, company等信息",把邮箱、地址等信息去掉"""
    
    structured_output = model_with_structure.invoke(prompt)
    # Get back the pydantic object
    print(structured_output.author_unit,type(structured_output.author_unit))  # Access the answer field
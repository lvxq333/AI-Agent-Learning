# 手打测试：调用模型并回答问题
# 1. 从 .env 文件加载环境变量
# 2. 创建 ChatOpenAI 实例——model wrapper（模型包装器）
# 3. 构建prompt template（提示模板）
# 4. 调用模型，获取回答
# 5. 流式调用模型，获取回答
# 6. batch调用模型，获取回答
# 7. 调用工具
# 8. 结构化输出
# 9. 创建回调处理器实例:统计一次输入，输出使用token量

import os

from dotenv import load_dotenv # 从 .env 文件加载所需信息
from langchain_openai import ChatOpenAI # 导入 ChatOpenAI 模型包装器
from langchain.messages import AIMessage, HumanMessage, SystemMessage  # 导入消息类型
from langchain.tools import tool  # 导入工具类
from typing_extensions import Annotated ,TypedDict  # 导入类型注解工具 ,有三种主流的类型注解工具
from langchain.chat_models import init_chat_model  # 导入初始化聊天模型的函数
from langchain_core.callbacks import UsageMetadataCallbackHandler  # 导入用来处理使用元数据的回调处理器



def main():

# /*-----------------------从 .env 文件加载环境变量-----------------------*/
    # 从 .env 文件加载环境变量
    load_dotenv()  # 从 .env 文件加载环境变量
    model_key = os.getenv("DEEPSEEK_API_KEY", "deepseek-chat").strip()
    model_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1").strip()
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()

# /*------------------------创建 ChatOpenAI 实例----------------------*/
    # 创建 ChatOpenAI 实例——model wrapper（模型包装器）
    model = ChatOpenAI(
        model=model,
        api_key=model_key,
        base_url=model_url,
        temperature=0.5,
        timeout=30,
    )

# /*------------------------构建prompt template（提示模板）----------------------*/
    # prompt template（提示模板）是一个字符串，包含了我们想要模型回答的问题或指令
    prompt = [SystemMessage("你叫小海，是一位论文写作助手。"),  # 系统消息，设定模型的角色和背景
              HumanMessage("请帮我写一段关于人工智能的介绍。"), # 人类消息，提出问题或指令
              AIMessage("你热爱编程，喜欢用Python写代码。"),    # AI消息，提供模型的个性化信息
              HumanMessage(content="请帮我翻译一下“Hello, world!”。")]  # 人类消息，提出另一个问题或指令

# /*------------------------流式调用模型，获取回答----------------------*/
    # # 流式调用模型，获取回答
    # # 利用循环来处理模型的流式输出，实时获取模型的思考过程和工具调用信息
    # for chunk in model.stream(prompt):
    #     for block in chunk.content_blocks:
    #         block_type = block.get("type")
    #         if block["type"] == "reasoning":
    #             reasoning = block.get("reasoning")
    #             if reasoning:
    #                 print(f"模型正在思考：{reasoning}")
    #         elif block["type"] == "tool_call_chunk":
    #             print(f"模型正在调用工具：{block}")
    #         elif block["type"] == "text":
    #             text = block.get("text")
    #             if text:   
    #                 print(f"模型输出文本：{text}")
    #         else:
    #             print(f"模型输出其他内容：{block}")

# /*----------------------batch调用模型，获取回答----------------------*/
    # batch调用模型，获取回答
    # responses = model.batch([
    #     "请翻译一下“Hello, world!”",
    #     "请帮我翻译一下“Goodbye, world!",
    #     "请帮我翻译一下“Welcome to AI!"
    # ])
    # for response in responses:
    #     print(f"模型回答：{response.content}")

    # for response in model.batch_as_completed([
    #     "请翻译一下“Hello, world!”",
    #     "请帮我翻译一下“Goodbye, world!",
    #     "请帮我翻译一下“Welcome to AI!"
    # ]):
    # # for response in responses:
    #     print(f"模型回答：{response}")

 # /*------------------------调用工具----------------------*/
    # model_with_tools = model.bind_tools([get_weather])  # 将工具绑定到模型上
    # response = model_with_tools.invoke("请告诉我北京的天气。")  # 调用模型，获取回答
    # for tool_call in response.tool_calls:   # tool_call 是模型调用工具的信息，包含工具名称和参数 字典
    #     print(f"模型调用了工具：{tool_call['name']}")
    #     print(f"模型参数：{tool_call['args']}")

# # /*------------------------结构化输出----------------------*/
#     model_with_structure = model.with_structured_output(MovieDict)
#     response = model_with_structure.invoke("飞驰人生第一部是哪一年上映的？")
#     print(response)


# /*------------------------调用模型，获取回答----------------------*/
    # 调用模型，获取回答
    # response = model.invoke(prompt)
    # print(response.content)

# # /*------------------------创建回调处理器实例:统计一次输入，输出使用token量----------------------*/
#     callback = UsageMetadataCallbackHandler()  # 创建一个回调处理器实例，用于处理模型使用的元数据
#     response = model.invoke("请帮我翻译一下“Hello, world!”", config={"callbacks": [callback]})  # 调用模型，获取回答，并传入回调处理器
#     print(callback.usage_metadata)  # 打印模型使用的元数据，包括输入和输出的token量等信息



# /*------------------------调用工具----------------------*/
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    # 这里可以调用实际的天气API来获取天气信息
    return f"{city}的天气是晴朗，温度25摄氏度。"

class MovieDict(TypedDict):
    """A movie with details."""
    title: Annotated[str, ..., "The title of the movie"]
    year: Annotated[int, ..., "The year the movie was released"]
    director: Annotated[str, ..., "The director of the movie"]
    rating: Annotated[float, ..., "The movie's rating out of 10"]


if __name__ == "__main__":
    main()

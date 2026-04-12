import os
import sys

import requests
from typing import Any
# from dotenv import load_dotenv
from langchain_core.messages import HumanMessage ,ToolMessage
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from create_model import create_My_model

def main() -> None:
    
    llm = create_My_model()    # 创建模型实例

    # 调用工具
    tools = MyTools()
    tool_list = [tools.search_weather]
    llm_with_tool = llm.bind_tools(tool_list)  # 将工具绑定到模型中，使模型能够调用工具

    same_thread = {"configurable": {"thread_id": "demo-user-1"}}
    another_thread = {"configurable": {"thread_id": "demo-user-2"}}
    graph = context_demo(llm_with_tool, tool_list)  # 创建一个支持工具调用的 StateGraph

    # 第一轮：告诉模型名字
    step1 = graph.invoke(
        {"messages": [HumanMessage(content="你好，我叫小海。请帮我查一下北京的天气。")]},
        config=same_thread,
    )
    print("同一会话-第1轮:", step1["messages"][-1].content)

    # 第二轮：同一 thread，模型应该记住用户名字
    step2 = graph.invoke(
        {"messages": [HumanMessage(content="我刚才告诉过你我的名字，我叫什么？再补一句出行建议。")]},
        config=same_thread,
    )
    print("同一会话-第2轮:", step2["messages"][-1].content)

    # 新会话：不同 thread，模型不应继承上一个会话的记忆
    step3 = graph.invoke(
        {"messages": [HumanMessage(content="我叫什么名字？")]},
        config=another_thread,
    )
    print("不同会话-第1轮:", step3["messages"][-1].content)


# 定义一个函数，接受当前消息状态，调用模型生成新的消息，并返回新的状态
def call_model(state: MessagesState, llm) -> MessagesState:
    ai_msg = llm.invoke(state["messages"])
    return {"messages": [ai_msg]}

# 定义一个函数，演示如何使用 StateGraph 和 InMemorySaver 来管理消息状态和上下文
def context_demo(llm_with_tool, tool_list):
    # 用 InMemorySaver 做 checkpoint，按 thread_id 保存/恢复消息历史
    memory = InMemorySaver()
    graph_builder = StateGraph(MessagesState)
    graph_builder.add_node("chatbot", lambda state: call_model(state, llm_with_tool))
    graph_builder.add_node("tools", ToolNode(tool_list))
    graph_builder.add_edge(START, "chatbot")
    # chatbot 输出如果包含 tool_calls，会自动路由到 tools；否则结束
    graph_builder.add_conditional_edges("chatbot", tools_condition, {"tools": "tools", END: END})
    graph_builder.add_edge("tools", "chatbot")
    graph = graph_builder.compile(checkpointer=memory)  # 编译图，传入 checkpointer 来启用消息历史的保存和恢复

    return graph


def run_one_query(llm_with_tools, search_weather_tool, city: str) -> str:
    """
    Agent 架构里的“执行层”：
    1) 模型先决定是否调用工具
    2) 执行工具并把结果封装为 ToolMessage
    3) 再次调用模型得到最终回答
    """
    question = f"请帮我查询{city}今天天气，并给出一句出行建议。"

    first_ai = llm_with_tools.invoke([HumanMessage(content=question)])
    messages = [HumanMessage(content=question), first_ai]  # 这一步是用户问题和模型第一次交互

    for call in first_ai.tool_calls:  # 遍历模型第一次交互中产生的工具调用
        if call.get("name") != "search_weather":  # 如果模型决定调用工具，则调用工具
            continue                              # 如果工具调用的名字不是 "search_weather"，则跳过  
        result = search_weather_tool.invoke(call.get("args", {}))  # 调用工具
        messages.append(ToolMessage(content=result, tool_call_id=call["id"]))  # 将工具调用结果添加到消息列表

    final_ai = llm_with_tools.invoke(messages)  # 再次调用模型得到最终回答  
    return str(final_ai.content)

class MyTools:

    @tool("echo_tool", return_direct=True)
    def echo_tool(self, input: str) -> str:
        """一个简单的工具，返回输入的字符串"""
        return input
    

    @tool("search_weather", return_direct=True)
    def search_weather(location: str) -> str:
        """
        查询指定城市天气（基于 wttr.in 简易接口）。
        参数:
            location: 城市名，例如 "Beijing"、"Shanghai"
        """
        # 在实际应用中，这里可以调用一个天气API来获取真实的天气数据
        location = location.strip()  # 去除输入中的多余空格
        if not location:
            return "请输入有效的城市名。"
        
        url = f"https://wttr.in/{location}" # 构造查询URL
        params = {"format": "j1"} # 请求 JSON 格式的天气数据
        try:
            resp = requests.get(url, params=params, timeout=15) # 发起HTTP请求获取天气数据
            resp.raise_for_status() # 如果响应状态码不是 200，会抛出 HTTPError
            # print(resp.text) # 打印原始响应文本，便于调试
            data: dict[str, Any] = resp.json() # 解析 JSON 响应
        except Exception as e:
            return f"天气查询失败：{e}"
            # 尽量稳健地从返回中取值
        current = (data.get("current_condition") or [{}])[0] # 获取当前天气信息，默认空字典避免 KeyError
        weather_desc = ((current.get("weatherDesc") or [{}])[0]).get("value", "未知")
        temp_c = current.get("temp_C", "未知")
        feels_like = current.get("FeelsLikeC", "未知")
        humidity = current.get("humidity", "未知")
        wind_kmph = current.get("windspeedKmph", "未知")

        return (
            f"{location} 当前天气：{weather_desc}，气温 {temp_c}°C，"
            f"体感 {feels_like}°C，湿度 {humidity}%，风速 {wind_kmph} km/h。"
        )


if __name__ == "__main__":
    main()

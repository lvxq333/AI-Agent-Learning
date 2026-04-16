import os
import sys
from typing import TypedDict
from pathlib import Path

import requests
from typing import Any, Literal

from langchain.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from create_model import create_My_model


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




def main():
    model = create_My_model()

    tools = [search_weather]

    # 将工具绑定到模型中，使模型能够调用工具，但需要在图中添加工具调用节点
    model_with_tool = model.bind_tools(tools)  

    # 定义一个函数，接受当前消息状态，调用模型生成新的消息，并返回新的状态
    def call_model(state: MessagesState) -> MessagesState:
        ai_msg = model_with_tool.invoke(state["messages"])
        return {"messages": [ai_msg]}

    # 定义两个不同的 thread_id，分别代表不同的用户会话
    same_thread = {"configurable": {"thread_id": "demo-user-1"}}
    another_thread = {"configurable": {"thread_id": "demo-user-2"}}
    HIL_thread = {"configurable": {"thread_id": "HIL-user-1"}}  # 人工审批线程

    
    graph_builder = StateGraph(MessagesState)
    graph_builder.add_node("llm", call_model)  # 添加模型调用节点
    graph_builder.add_node("tools", ToolNode(tools))  # 添加工具调用节点
    graph_builder.add_edge(START, "llm")  # 从 START 到模型调用节点
    graph_builder.add_conditional_edges("llm", tools_condition, ["tools", END])  # 根据模型输出条件决定是否调用工具
    graph_builder.add_edge("tools", "llm")  # 工具调用后回到模型节点，继续对话
    graph_builder.add_edge("llm", END)

    # 用 SqliteSaver 做 checkpoint，按 thread_id 保存/恢复消息历史
    with SqliteSaver.from_conn_string("day3/persistent_memory.db") as checkpointer:
        graph = graph_builder.compile(
            checkpointer=checkpointer,
            interrupt_before=["tools"],
            )  # 编译图，传入 checkpointer 来启用消息历史的保存和恢复

        for chunk in graph.stream({"messages":[HumanMessage(content="不要凭借记忆回答，我叫什么？帮我调用search_weather工具查一下北京的天气")]},
                # messages：仓库中的货物
                # updates：仓库中货物的增量更新
                # values：每一步执行后的完整货物快照
                stream_mode=["updates", "messages", "values"],
                config=HIL_thread,
                version="v2"
            ):
            if chunk["type"] == "updates":
                for node_name, update in chunk["data"].items():
                    print(f"\n[节点更新] {node_name}")

                    if node_name == "__interrupt__":
                        # print("检测到人工审批中断:", update)  # 这里通常是 tuple
                        # 人工确认后再恢复（不修改状态）
                        approve = input("是否批准本次工具调用？(y/n): ").strip().lower()
                        if approve == "y":
                            print("\n=== 已批准，继续执行后续节点 ===")
                            for resumed_chunk in graph.stream(
                                Command(resume=True),
                                config=HIL_thread,
                                stream_mode=["updates", "values"],
                                version="v2",
                            ):
                                if resumed_chunk["type"] == "updates":
                                    for resumed_node, resumed_update in resumed_chunk["data"].items():
                                        print(f"\n[恢复后节点更新] {resumed_node}")
                                        print("增量key:", list(resumed_update.keys()))
                                elif resumed_chunk["type"] == "values":
                                    resumed_state = resumed_chunk["data"]
                                    resumed_messages = resumed_state.get("messages", [])
                                    print(f"\n[恢复后 values] messages数量: {len(resumed_messages)}")
                                    if resumed_messages:
                                        last = resumed_messages[-1]
                                        print("最后一条类型:", type(last).__name__)
                                        print("最后一条content:", getattr(last, "content", None))
                                        print("最后一条tool_calls:", getattr(last, "tool_calls", None))
                        else:
                            print("你拒绝了本次工具调用。")
                        
                    elif node_name:
                        print("增量key:", list(update.keys()))

                    # if "messages" in update:
                    #     last_msg = update["messages"][-1]
                    #     print("消息类型:", type(last_msg).__name__)
                    #     print("文本内容:", getattr(last_msg, "content", None))
                    #     print("工具调用:", getattr(last_msg, "tool_calls", None))
                    #     print("用量统计:", getattr(last_msg, "usage_metadata", None))
            elif chunk["type"] == "values":
                # 每一步执行后的完整 state 快照
                state = chunk["data"]
                messages = state.get("messages", [])
                print(f"\n[values] 完整state，messages数量: {len(messages)}")

                if messages:
                    last = messages[-1]
                    print("最后一条类型:", type(last).__name__)
                    print("最后一条content:", getattr(last, "content", None))
                    print("最后一条tool_calls:", getattr(last, "tool_calls", None))





if __name__ == "__main__":
    main()









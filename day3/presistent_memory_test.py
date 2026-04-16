import os
import sys
from pathlib import Path

# from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
# from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from create_model import create_My_model


# 这个示例展示了如何使用 langgraph 的 StateGraph 和 SqliteSaver 来实现一个简单的聊天机器人，
# 并且在不同的code中采用相同的thread_id，来验证持久化消息历史。
# 运行这个示例前，先运行PersistentMemory.py，完成一次对话，生成消息历史并保存到数据库中。
# 然后再运行这个示例，验证同一 thread_id 的消息历史是否被正确保存和恢复。


def main() -> int:

    llm = create_My_model()

    # 定义一个函数，接受当前消息状态，调用模型生成新的消息，并返回新的状态
    def call_model(state: MessagesState) -> MessagesState:
        ai_msg = llm.invoke(state["messages"])
        return {"messages": [ai_msg]}

    # # 用 InMemorySaver 做 checkpoint，按 thread_id 保存/恢复消息历史
    # memory = InMemorySaver()

    # 用 SqliteSaver 做 checkpoint，按 thread_id 保存/恢复消息历史
    with SqliteSaver.from_conn_string("day3/persistent_memory.db") as checkpointer:
        graph_builder = StateGraph(MessagesState)
        graph_builder.add_node("chatbot", call_model)
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("chatbot", END)
        graph = graph_builder.compile(checkpointer=checkpointer)  # 编译图，传入 checkpointer 来启用消息历史的保存和恢复

        same_thread = {"configurable": {"thread_id": "demo-user-1"}}
        another_thread = {"configurable": {"thread_id": "demo-user-2"}}

        # 重新运行第一轮，验证同一 thread_id 的消息历史是否被正确保存和恢复
        step1 = graph.invoke(
            {"messages": [HumanMessage(content="你还知道我是谁吗？帮我翻译一下“harness”是什么意思")]},
            config=same_thread,
        )
        print("不同code，相同thread_id-测试轮:", step1["messages"][-1].content)

        # print(list(graph.get_state(same_thread)))  # 打印同一 thread_id 的消息历史

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

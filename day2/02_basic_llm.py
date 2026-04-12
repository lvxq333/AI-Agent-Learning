import os
import sys

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

from create_model import create_My_model


def main() -> int:
    # load_dotenv()

    # api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    # base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1").strip()
    # model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()

    # if not api_key:
    #     print("错误：未读取到 DEEPSEEK_API_KEY，请先在 .env 中配置。", file=sys.stderr)
    #     return 1

    # llm = ChatOpenAI(
    #     model=model_name,
    #     api_key=api_key,
    #     base_url=base_url,
    #     temperature=0.1,
    #     timeout=30,
    # )
    llm = create_My_model()

    def call_model(state: MessagesState) -> MessagesState:
        ai_msg = llm.invoke(state["messages"])
        return {"messages": [ai_msg]}

    # 用 InMemorySaver 做 checkpoint，按 thread_id 保存/恢复消息历史
    memory = InMemorySaver()
    graph_builder = StateGraph(MessagesState)
    graph_builder.add_node("chatbot", call_model)
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    graph = graph_builder.compile(checkpointer=memory)  # 编译图，传入 checkpointer 来启用消息历史的保存和恢复

    same_thread = {"configurable": {"thread_id": "demo-user-1"}}
    another_thread = {"configurable": {"thread_id": "demo-user-2"}}

    # 第一轮：告诉模型名字
    step1 = graph.invoke(
        {"messages": [HumanMessage(content="你好，我叫小海。请只回复“收到”。")]},
        config=same_thread,
    )
    print("同一会话-第1轮:", step1["messages"][-1].content)

    # 第二轮：同一 thread_id，模型应能记住上一轮信息
    step2 = graph.invoke(
        {"messages": [HumanMessage(content="我叫什么名字？只回复名字。")]},
        config=same_thread,
    )
    print("同一会话-第2轮(记忆测试):", step2["messages"][-1].content)

    # 第三轮：换 thread_id，不共享上文
    step3 = graph.invoke(
        {"messages": [HumanMessage(content="我叫什么名字？只回复名字。")]},
        config=another_thread,
    )
    print("新会话-第1轮(隔离测试):", step3["messages"][-1].content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

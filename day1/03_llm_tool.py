from __future__ import annotations

import os
import sys
from typing import Any

import requests
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI


@tool
def query_weather(city: str) -> str:
    """
    查询指定城市天气（基于 wttr.in 简易接口）。
    参数:
        city: 城市名，例如 "Beijing"、"Shanghai"
    """
    city = city.strip()
    if not city:
        return "城市名不能为空。"

    url = f"https://wttr.in/{city}"
    params = {"format": "j1"} # 请求 JSON 格式的天气数据
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status() # 如果响应状态码不是 200，会抛出 HTTPError
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
        f"{city} 当前天气：{weather_desc}，气温 {temp_c}°C，"
        f"体感 {feels_like}°C，湿度 {humidity}%，风速 {wind_kmph} km/h。"
    )


def build_llm() -> ChatOpenAI:
    """
    Agent 架构里的“模型层”：
    - 从 .env 读取 DeepSeek 配置
    - 返回可用于对话和工具调用的 LLM 实例
    """
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1").strip()
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()

    if not api_key:
        raise RuntimeError("未读取到 DEEPSEEK_API_KEY，请先在 .env 中配置。")

    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=0.2,
    )


def run_one_query(llm_with_tools: ChatOpenAI, city: str) -> str:
    """
    Agent 架构里的“执行层”：
    1) 模型先决定是否调用工具
    2) 执行工具并把结果封装为 ToolMessage
    3) 再次调用模型得到最终回答
    """
    question = f"请帮我查询{city}今天天气，并给出一句出行建议。"

    first_ai = llm_with_tools.invoke([HumanMessage(content=question)])
    messages = [HumanMessage(content=question), first_ai]  # 这一步是用户问题和模型第一次交互

    for call in first_ai.tool_calls:
        if call.get("name") != "query_weather":  # 如果模型决定调用工具，则调用工具
            continue
        result = query_weather.invoke(call.get("args", {}))  # 调用工具
        messages.append(ToolMessage(content=result, tool_call_id=call["id"]))  # 将工具调用结果添加到消息列表

    final_ai = llm_with_tools.invoke(messages)  # 再次调用模型得到最终回答  
    return str(final_ai.content)


def interactive_loop(llm_with_tools: ChatOpenAI) -> None:
    """
    Agent 架构里的“交互层”：
    - 持续读取用户输入
    - 支持多轮查询
    - 支持 exit/quit 退出
    """
    print("天气查询已启动。请输入城市名进行查询，输入 exit 或 quit 退出。")
    while True:
        city = input("城市名> ").strip()
        if city.lower() in {"exit", "quit"}:
            print("已退出天气查询。")
            break
        if not city:
            print("请输入有效城市名。")
            continue

        answer = run_one_query(llm_with_tools, city)
        print("\n=== 最终回答 ===")
        print(answer)
        print("-" * 40)


def main() -> int:
    try:
        llm = build_llm()
        llm_with_tools = llm.bind_tools([query_weather])
    except Exception as e:
        print(f"初始化失败：{e}", file=sys.stderr)
        return 1

    try:
        interactive_loop(llm_with_tools)
        return 0
    except Exception as e:
        print(f"调用失败：{e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main()) # 退出程序并返回0


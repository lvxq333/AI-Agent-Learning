from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


def main() -> int:
    # 从当前目录的 .env 加载配置
    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1").strip()
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()

    if not api_key:
        print("错误：未读取到 DEEPSEEK_API_KEY，请先在 .env 中配置。", file=sys.stderr)
        return 1

    try:
        llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=0.7,
        )

        prompt = (
            "你是一位AI Agent学习教练。"
            "我正在进行Day1学习，请用中文给我5条可执行建议，"
            "每条建议都包含：目标、具体动作、预期产出。"
            "我的背景是：会基础Python，正在用Mac+Cursor学习。"
        )

        response = llm.invoke(prompt)
        print("=== DeepSeek 建议 ===")
        print(response.content)
        return 0
    except Exception as e:
        print(f"调用失败：{e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

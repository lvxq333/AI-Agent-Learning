import os
import sys

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


def create_My_model() -> ChatOpenAI:
    """Create and return a ChatOpenAI client using env config."""
    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1").strip()
    model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()

    if not api_key:
        print("错误：未读取到 DEEPSEEK_API_KEY，请先在 .env 中配置。", file=sys.stderr)
        raise RuntimeError("Missing DEEPSEEK_API_KEY")

    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=0.1,
        timeout=30,
    )

import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


def create_My_model() -> None:

    load_dotenv()  # 从 .env 文件加载环境变量
    model_key = os.getenv("DEEPSEEK_API_KEY", "deepseek-chat").strip()
    model_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1").strip()
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()

    model = ChatOpenAI(
        model=model,
        api_key=model_key,
        base_url=model_url,
        temperature=0.5,
        timeout=30,
    )

    return model

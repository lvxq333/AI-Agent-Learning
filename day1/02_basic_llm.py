from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


QUESTION = "传统后端转型做agent开发一周的规划是什么？"


def build_llm() -> ChatOpenAI:
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
        temperature=0.7,
    )


def ask_v1_direct(llm: ChatOpenAI) -> str:
    response = llm.invoke([HumanMessage(content=QUESTION)])
    return str(response.content).strip()


def ask_v2_with_system(llm: ChatOpenAI) -> str:
    messages = [
        SystemMessage(
            content=(
                "你是一位AI Agent学习教练。请用中文回答，风格务实。"
                "输出结构必须为：目标 -> 每日计划(Day1~Day7) -> 风险与规避 -> 当周产出清单。"
                "每一天至少给出2个可执行动作，尽量给出可量化结果。"
            )
        ),
        HumanMessage(content=QUESTION),
    ]
    response = llm.invoke(messages)
    return str(response.content).strip()


def ask_v3_cot_style(llm: ChatOpenAI) -> str:
    # 这里采用“先分析再给方案”的提示风格，模拟 CoT 式拆解，
    # 同时要求输出中显式给出“分析依据摘要”，便于学习对比。
    prompt = (
        "请先基于以下维度做简短分析："
        "学习者背景(传统后端)、一周时间预算、最小可行成果(MVP)、风险。"
        "然后给出7天计划。"
        "输出格式：分析依据摘要 -> Day1~Day7 -> 验收标准。"
        "问题：" + QUESTION
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    return str(response.content).strip()


def metric_count(text: str) -> tuple[int, int, int]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    bullet_count = sum(1 for ln in lines if ln.startswith(("-", "*", "1.", "2.", "3.", "4.", "5.", "6.", "7.")))
    day_count = sum(1 for ln in lines if "Day" in ln or "第" in ln and "天" in ln)
    keyword_count = sum(
        text.count(k)
        for k in ["目标", "动作", "产出", "验收", "风险", "指标", "项目", "部署", "复盘"]
    )
    return bullet_count, day_count, keyword_count


def short(text: str, limit: int = 80) -> str:
    one_line = " ".join(text.split())
    return one_line[: limit - 1] + "…" if len(one_line) > limit else one_line


def build_compare_table(v1: str, v2: str, v3: str) -> str:
    m1 = metric_count(v1)
    m2 = metric_count(v2)
    m3 = metric_count(v3)
    return "\n".join(
        [
            "| 版本 | 提示方式 | 结构化程度(粗略) | 一周计划覆盖 | 可执行关键词计数 | 回答片段 |",
            "|---|---|---:|---:|---:|---|",
            f"| V1 | 直接提问 | {m1[0]} | {m1[1]} | {m1[2]} | {short(v1)} |",
            f"| V2 | System Message 约束 | {m2[0]} | {m2[1]} | {m2[2]} | {short(v2)} |",
            f"| V3 | CoT 风格拆解提示 | {m3[0]} | {m3[1]} | {m3[2]} | {short(v3)} |",
        ]
    )


def append_to_notes(v1: str, v2: str, v3: str, table: str) -> Path:
    notes_path = Path(__file__).with_name("day1_notes.md")
    section = (
        "\n\n---\n\n"
        "## LLM提问变体实验：后端转Agent一周规划\n\n"
        f"问题：`{QUESTION}`\n\n"
        "### V1 直接提问\n\n"
        f"{v1}\n\n"
        "### V2 System Message 约束\n\n"
        f"{v2}\n\n"
        "### V3 CoT风格提示\n\n"
        f"{v3}\n\n"
        "### 三者对比表\n\n"
        f"{table}\n"
    )
    existing = notes_path.read_text(encoding="utf-8") if notes_path.exists() else ""
    notes_path.write_text(existing + section, encoding="utf-8")
    return notes_path


def main() -> int:
    try:
        llm = build_llm()
        v1 = ask_v1_direct(llm)
        v2 = ask_v2_with_system(llm)
        v3 = ask_v3_cot_style(llm)
        table = build_compare_table(v1, v2, v3)

        print("=== V1 直接提问 ===")
        print(v1)
        print("\n=== V2 System Message 约束 ===")
        print(v2)
        print("\n=== V3 CoT风格提示 ===")
        print(v3)
        print("\n=== 对比表 ===")
        print(table)

        notes_path = append_to_notes(v1, v2, v3, table)
        print(f"\n已写入笔记：{notes_path}")
        return 0
    except Exception as e:
        print(f"调用失败：{e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


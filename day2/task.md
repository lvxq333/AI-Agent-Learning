**Day 2 任务详细拆解（AI Agent开发工程师转行计划 · 今天专属）**

我把你**今天全部任务**按学习顺序、时间分配、具体资源链接、**知识掌握程度**（理解即可 / 掌握 / 熟练掌握）逐一拆解成最小颗粒度。你只需按顺序完成，每完成一项就在下面打√，晚上统一打卡即可。

### 1. AI Agent核心概念（预计1小时 · 必须先学）
**目标**：搞清楚“Agent到底是什么、怎么工作的”，为后面写代码建立直觉。

| 子任务 | 具体内容 | 推荐资源（直接点开） | 掌握程度 | 完成要求 |
|--------|----------|----------------------|----------|----------|
| 1.1 ReAct范式 | 理解Reason（思考）+ Act（行动）循环 | 【李宏毅2025】一堂课搞懂AI Agent原理（B站，2小时精华版，建议1.5倍速）<br>https://www.bilibili.com/video/BV1CmdWYWEvu/ | **理解即可** | 能用自己的话解释“Thought → Action → Observation”循环 |
| 1.2 Agent四大组件 | LLM + Tools + Memory + Planner | 继续上面李宏毅视频第2-3部分 + LangChain官方Agents概览<br>https://docs.langchain.com/oss/python/langchain/agents | **理解即可** | 画出四大组件关系图（Notion手绘即可） |
| 1.3 Agent主流类型 | Single / Multi / Hierarchical | 李宏毅视频最后10分钟 + 知乎对比文章<br>https://zhuanlan.zhihu.com/p/1922798573327745679 | **理解即可** | 能区分三种类型的适用场景 |

**完成标志**：在Notion写300字以上总结（包含图），标明“Day2-概念笔记”。

---

### 2. LangChain框架入门（预计3-4小时 · 重点）
**目标**：搞清楚LangChain是什么、和其他框架的区别，以及核心组件怎么用。

| 子任务 | 具体内容 | 推荐资源（直接点开） | 掌握程度 | 完成要求 |
|--------|----------|----------------------|----------|----------|
| 2.1 框架对比 | LangChain vs LangGraph vs LlamaIndex | 腾讯云开发者社区深度对比（中文，最清晰）<br>https://cloud.tencent.com/developer/article/2630511 | **理解即可** | 能一句话说明三者定位区别 |
| 2.2 核心组件全览 | LLM Wrapper、PromptTemplate、Tools、Agents、Memory、LCEL | LangChain Academy官方免费课程（Python）<br>https://academy.langchain.com/courses/foundation-introduction-to-langchain-python<br>（Module 1 & 2） | **掌握** | 能说出每个组件的作用 |
| 2.3 create_react_agent | ReAct Agent的创建方式（今天主打） | 官方参考文档 + 代码示例<br>https://reference.langchain.com/python/langchain-classic/agents/react/agent/create_react_agent | **熟练掌握** | 能独立写出带Tool的ReAct Agent |
| 2.4 LCEL写法 | 新的链式表达式语言（取代旧的AgentExecutor） | 上面Academy课程Module 2 + JetBrains 2026教程<br>https://blog.jetbrains.com/pycharm/2026/02/langchain-tutorial-2026/ | **掌握** | 代码必须用LCEL写，不能用旧写法 |

**完成标志**：边看边敲代码，每学一个组件就写一个最小demo，保存在`Day2/notes/`文件夹。

---

### 3. 环境准备 + 第一个Agent实战（预计2-3小时 · 必须动手）
**目标**：把理论立刻变成能跑的代码。

| 子任务 | 具体内容 | 推荐资源（直接点开） | 掌握程度 | 完成要求 |
|--------|----------|----------------------|----------|----------|
| 3.1 环境搭建 | 创建虚拟环境 + 安装包 + 配置API Key | 官方安装指南（2026最新）<br>https://docs.langchain.com/oss/python/langchain/install | **熟练掌握** | 能成功运行`llm.invoke("你好")` |
| 3.2 练习1：带搜索Tool的ReAct Agent | 回答“2026年香港最新GDP数据” | 结合Academy课程 + Codecademy实战示例<br>https://www.codecademy.com/article/building-langchain-agents-for-llm-applications-in-python | **熟练掌握** | Agent能正确调用Tool并回答 |
| 3.3 练习2：增加自定义Tool | 写一个计算器Tool或天气Tool | LangChain官方Tools文档（搜索“custom tool”） | **熟练掌握** | 自定义Tool能被Agent调用 |
| 3.4 练习3：加上Memory | ConversationBufferMemory实现多轮记忆 | Academy课程Module 2 + YouTube 2026完整课程（代码仓库）<br>https://www.youtube.com/watch?v=AOQyRiwydyo （GitHub代码在描述里） | **熟练掌握** | 3轮对话后Agent能记住前两轮内容 |

**代码要求**：
- 文件名：`Day2/day2_agent_demo.py`
- 必须使用`create_react_agent` + LCEL
- 每段代码加详细中文注释
- 保存运行截图（成功输出 + 3轮对话）

---

### 今日完成指标（必须100%达标）
1. 概念笔记（300字+图）  
2. 环境运行成功截图  
3. 3个练习全部跑通 + 截图  
4. 代码整洁、有注释、使用LCEL  
5. 晚上12点前完成并打卡

**打卡格式**（今晚直接回复我）：
```
Day 2 已完成 ✅
- 概念笔记链接：xxx
- 环境&练习1截图：xxx
- 练习2&3截图：xxx
- 代码仓库链接（可选）：xxx
- 遇到的问题：（如果有）
- 今日心得：（1-2句话）
```

**明天预告（Day 3）**：LangGraph + 带Planner的复杂Agent + 自我反思机制。

今天把**概念理解 + LangChain基础 + 第一个Agent**彻底吃透，明天我们直接上难度！  
任何一步卡住，立刻把错误信息或截图发给我，我秒回帮你debug。  

**现在就开始吧！** 🚀  
（复制上面的表格，打√跟踪进度最有效）
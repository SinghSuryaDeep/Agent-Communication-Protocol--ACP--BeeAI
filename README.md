# Agent-Communication-Protocol--ACP--BeeAI

# 🧠 AI-Driven Marketing Content Workflow using IBM BeeAI + Agent Communication Protocol (ACP) + IBM watsonx

## 📌 Overview

This repository demonstrates a **multi-agent system** powered by **IBM BeeAI** using **Agent Communication Protocol (ACP)** and **IBM watsonx**. The system is designed to automate **marketing content creation**, combining real-time market research and creative content generation through two specialized agents.

### 👥 Agents Involved

1. **Research Agent**: Gathers up-to-date marketing trends, competitor insights, and keywords using Tavily and LangChain.
2. **Content Agent**: Uses IBM watsonx LLMs + CrewAI to generate structured blog outlines or social media post ideas based on the research findings.

These agents communicate asynchronously via ACP, orchestrated through a Python client script.

---

## ✨ Use Case

Imagine you're launching a **plant-based food delivery service** in 2025 and want to create high-quality marketing content. This system:
- Gathers live market data (trends, competitors, keywords),
- Uses it to generate engaging, structured content ideas automatically.

⚡ Result: A faster, smarter marketing workflow with zero manual research or writing effort.

---
## 🚀 Running the Application

You’ll need **three terminals**, one for each component.

### Terminal 1: Start Research Agent Server

```bash
uv run research_server.py
```

➡️ Runs on `http://localhost:8003`

---

### Terminal 2: Start Content Agent Server

```bash
uv run content_server.py
```

➡️ Runs on `http://localhost:8001`

---

### Terminal 3: Run Client to Orchestrate Workflow

```bash
uv run client.py
```

This sends the topic through the research agent → then uses the findings for content generation.

---


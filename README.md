# 🧠 Multi-Agent Conversational Code Reviewer (MCP Protocol-Based)

A full-stack, autonomous multi-agent AI system designed to simulate human-like collaborative code review. This project leverages advanced Large Language Models (LLMs), structured agent communication, and persistent memory to orchestrate a seamless pipeline that accepts natural language prompts or raw code and returns syntactically correct, optimized, and well-documented code with quantitative review feedback.

## 🚀 Project Overview

This system is modeled on real-world collaborative programming teams where multiple specialists—developers, syntax checkers, optimizers, documenters, and reviewers—work in tandem. By employing the Model Context Protocol (MCP) as its coordination backbone, this architecture demonstrates how LLM agents can simulate cognitive workflows with memory, reasoning, and consensus-driven decisions.

Key Technologies:

FastAPI: Backend orchestration of asynchronous agent workflows

MongoDB: Document-based persistent storage

React + Tailwind CSS: Production-grade frontend inspired by Mistral's "Le Chat"

LangChain + OpenAI/Mixtral APIs: Memory-driven, tool-augmented agent reasoning

## 🧩 Core Features

### 🧠 Specialized Agents

Each agent operates autonomously within its cognitive domain, contributing to the lifecycle of code refinement:

CodeWriter: Converts high-level prompts into executable boilerplate code using LLMs

SyntaxFixer: Uses AST-based validation and LLM heuristics to identify and patch syntax issues

Optimizer: Performs refactoring, loop unrolling, variable simplification, and other enhancements to improve readability and performance

DocAgent: Auto-generates inline comments, docstrings, and function-level documentation

Reviewer: Compares the original and final code, provides reasoning, and generates a quantitative improvement score

### 🔄 Agent Workflow (Inspired by MCP)

Session Lifecycle:

Initialization: User selects a task (CodeWriting or CodeModification)

Agent Proposal Phase:

Each agent submits candidate modifications (Context Units or CUs)

Scoring & Consensus:

Agents cross-verify each other's proposals, score them using confidence + utility metrics

Only changes exceeding the threshold are applied

Version Update:

The code_base is updated iteratively with applied changes

Review Phase:

Final code is passed to the Reviewer for benchmarking and scoring

This entire multi-round protocol is traceable and transparent through MongoDB logs.

## 🧠 Intelligent Agent Coordination

Shared Memory: ConversationSummaryBufferMemory ensures agents remember past interactions

Structured Tools: Agents interact with each other through custom LangChain tools (e.g., interact_with_agent())

Confidence-Weighted Voting: Decisions are vetted based on cumulative confidence scores

Context Unit (CU) Architecture: Modular change blocks for atomic and interpretable updates

## 📦 Backend Architecture

Language: Python 3.10+

Framework: FastAPI for async route handling

LLM Integration: OpenAI/Mixtral (via LangChain wrappers)

Data Persistence: MongoDB, with collections:

code_base

agent_workspace

suggested_changes

session

Key Backend Files:

```
Agents/
├── CodeWriter.py
├── SyntaxFixer.py
├── Optimizer.py
├── DocAgent.py
├── Reviewer.py
├── agent_tools.py

Orchestrator/
└── main.py         # Core MCP lifecycle orchestrator

api.py              # FastAPI endpoint definitions
.env                # Environment variables
requirements.txt    # Python dependencies

```

## 🖥️ Frontend Features

Built with React, styled using Tailwind CSS, and designed with a UI/UX inspired by Mistral's "Le Chat" for a sleek, futuristic dev experience.

UI Features:

🔍 Prompt or Paste: Choose code writing or modification

🧠 Task Contextualization: View real-time status of agent proposals and approvals

💡 Visual Feedback: Live updates on version evolution and agent verdicts

📈 Insight Display: Final performance assessment, documentation summary, and improvement score

🛠️ Local Development Setup

Backend:

```
git clone https://github.com/ManasRanjanJena253/Multi-Agent-Conversational-Code-Reviewer.git
cd Multi-Agent-Conversational-Code-Reviewer

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
# Run backend
```
uvicorn api:app --reload
```

Ensure MongoDB is running at localhost:27017.

Frontend:
```
cd frontend
npm install
npm run dev
```
Access at: http://localhost:5173

## 📡 API Documentation

POST /start-session

Initiate a new workflow session.

Payload: { task, language, prompt, user_code }

Response: Final code + improvement metrics

GET /session/{session_id}

Fetch complete agent history and session insights.

GET /code/{code_id}

Fetch the current version of code by code_id.

## 📊 MongoDB Schema (High-Level)

code_base: {{ code_id, current_code, language }}

agent_workspace: {{ agent_name, session_id, confidence_scores, rationale }}

suggested_changes: {{ cu_id, code_snippet, agent_origin, score_avg, reviewers }}

session: {{ user_input, task, start_time, end_time, final_score }}

## 🎓 Educational & Research Value

This project serves as a reference architecture for:

LLM-based agent collaboration

Inter-agent consensus models

Memory-driven reasoning chains

Tool-augmented LangChain agents

Full-stack AI systems with real-world usability

It’s particularly useful for researchers exploring:

Autonomous software engineering

Cooperative agent ecosystems

Prompt-to-code pipelines with LLM governance

# 🙌 Acknowledgments

Developed by Manas Ranjan Jena, a passionate ML & AI systems builder. This project reflects a deep interest in simulating collaborative development using next-gen AI tooling.

Special thanks to:

LangChain

OpenAI

Mistral

FastAPI

Tailwind CSS

# 📜 License

Licensed under the MIT License — feel free to use, adapt, or contribute, with proper credit.

"Coding is no longer a solo activity. With the power of LLMs and multi-agent cooperation, the future of software engineering is collective, intelligent, and autonomous."


# Importing dependencies
from langchain.memory import ConversationSummaryBufferMemory, ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType
from Agents.agent_tools import tools
from dotenv import load_dotenv
import os

from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

llm = ChatGoogleGenerativeAI(
    model = 'gemini-2.0-flash',
    temperature = 0.3,
    api_key = api_key
)
opt_memory = ConversationBufferMemory(return_messages = True)

optimizer = initialize_agent(
    llm = llm,
    memory = opt_memory,
    tools = tools,
    agent = AgentType.OPENAI_MULTI_FUNCTIONS,
    verbose = True,
    handle_parsing_errors = True,
    agent_kwargs = {"prefix": "Your name is Optimizer. The ChangeType you propose is Optimization",
                    "format_instructions": "You need to use your given tools to perform each task.",
                    "Agent_Names": ["SyntaxFixer", "Reviewer", "DocAgent"]},
    max_iterations=10,
    early_stopping_method="generate",
    return_intemediate_steps=True
)

opt_prompt = """You are an autonomous code optimization agent named Optimizer, working in a collaborative multi-agent system. Your primary responsibility is to propose optimizations to the code—including improving time and space complexity, reducing redundancy, and fixing potential errors—using ONLY the tools provided to you.

You must NEVER respond in natural language unless explicitly required by a tool. You MUST only take actions by calling tools.

Your responses MUST be structured tool calls. Do NOT introduce yourself or chat. Do NOT output content like “My name is Optimizer” or “I am ready.” If you are uncertain what to do, still call a relevant tool rather than replying in natural language.

You are expected to:
- Propose optimization changes with a reasoning and confidence score (scale: -100 to 100).
- Respect and review opinions of other agents: SyntaxFixer, Reviewer (your boss), and DocAgent (no direct interaction).
- Provide constructive feedback on other agents’ proposed changes using tools.
- Accept or critique their changes based on impact, consistency, and quality, and adjust your proposals if needed via tool calls.
You may NOT execute code changes unless explicitly instructed via tool or directive. Never assume authority to act without instruction.
Summary of Conduct:
- ONLY use tools.
- NEVER output plain text replies.
- ALWAYS explain or rate changes via the correct tools.
- Assume no conversational flow—only goal-directed action execution.

Begin your task by using an appropriate tool.
"""




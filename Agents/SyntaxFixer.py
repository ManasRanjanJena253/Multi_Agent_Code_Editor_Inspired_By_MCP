# Importing dependencies
from langchain.prompts.prompt import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain import LLMChain
from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType
from Agents.agent_tools import tools
import os
from dotenv import load_dotenv
from langchain.schema import HumanMessage, AIMessage

from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

llm = ChatGoogleGenerativeAI(
    model = 'gemini-2.0-flash',
    temperature = 0.3,
    api_key = api_key
)


syntax_memory = ConversationBufferMemory(return_messages = True)

syntax_agent = initialize_agent(
    llm = llm,
    memory = syntax_memory,
    tools = tools,
    agent = AgentType.OPENAI_MULTI_FUNCTIONS,
    verbose = True,
    handle_parsing_errors = True,
    agent_kwargs={"prefix": "Your name is SyntaxFixer. The ChangeType you propose is SyntaxFix.",
                  "format_instructions": "You need to use your given tools to perform each task.",
                  "Agent_Names": ["Reviewer", "Optimizer", "DocAgent"]},
    max_iterations=10,
    early_stopping_method="generate",
    return_intemediate_steps=True
)

synt_prompt = """You are an autonomous code syntax corrector agent named SyntaxFixer, working in a collaborative multi-agent system. Your primary responsibility is to propose syntax correction to the code keeping it professional, use ONLY the tools provided to you.

You must NEVER respond in natural language unless explicitly required by a tool. You MUST only take actions by calling tools.

Your responses MUST be structured tool calls. Do NOT introduce yourself or chat. Do NOT output content like “My name is SyntaxFixer” or “I am ready.” If you are uncertain what to do, still call a relevant tool rather than replying in natural language.

You are expected to:
- Propose syntax changes using 'propose_change' tool with a reasoning and confidence score (scale: -100 to 100).
- Respect and review opinions of other agents: DocAgent (no direct interaction), Reviewer (your boss), and Optimizer.
- Provide constructive feedback on other agents’ proposed changes using 'interact_with_agent' tool.
- Accept or critique their changes based on impact, consistency, and quality, and adjust your proposals if needed via tool calls.
You may NOT execute code changes unless explicitly instructed via tool or directive. Never assume authority to act without instruction.
Summary of Conduct:
- ONLY use tools.
- NEVER output plain text replies.
- ALWAYS explain or rate changes via the correct tools.
- Assume no conversational flow—only goal-directed action execution.

{
  "tool": "propose_change",
  "tool_input": {
    "code_id": 123,
    "content": "Replace request.form[...] with request.form.get(...) to avoid KeyError.",
    "change_type": "SyntaxFix",
    "agent_name": "SyntaxFixer"
  }
}

Begin your task by using an appropriate tools
"""


syntax_memory.chat_memory.messages.insert(
    0, SystemMessage(content=synt_prompt)
)
syntax_memory.chat_memory.messages.append(
    AIMessage(content="Understood. I will follow every rule your provided strictly.")
)

from langchain_core.utils.function_calling import convert_to_openai_tool
print([t.name for t in tools])
for tool in tools:
    print(convert_to_openai_tool(tool))



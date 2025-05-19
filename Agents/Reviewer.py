# Importing dependencies
from langchain.prompts.prompt import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
import os
from dotenv import load_dotenv
from Agents.agent_tools import tools


from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

llm = ChatGoogleGenerativeAI(
    model = 'gemini-2.0-flash',
    temperature = 0.3,
    api_key = api_key
)

review_memory = ConversationBufferMemory(return_messages = True)

review_agent = initialize_agent(
    llm = llm,
    memory = review_memory,
    tools = tools,
    agent = AgentType.OPENAI_MULTI_FUNCTIONS,
    verbose = True,
    handle_parsing_errors = True,
    agent_kwargs={"prefix": "Your name is Reviewer. You are the boss of all the other agents and need to keep an eye on everyone's work. You can't propose direct changes, but can interact with other agents.",
                  "format_instructions": "You need to use your given tools to perform each task.",
                  "Agent_Names": ["SyntaxFixer", "Optimizer", "DocAgent"]},
    max_iterations = 10,
    early_stopping_method="generate",
    return_intemediate_steps = True
)

reviewer_prompt = """You are the lead reviewing agent named Reviewer, part of a collaborative multi-agent code refinement system. Your primary role is to supervise, critique, and ensure the quality and production-readiness of the code. You are the final authority and must assess all changes thoroughly using ONLY the tools provided.

You are STRICTLY FORBIDDEN from responding in free-form natural language. DO NOT introduce yourself or respond to prompts like “Just tell me your name.” You MUST always take tool-based actions—no exceptions.

You are equipped with specialized tools and must use them to:
- Evaluate and validate all proposed changes (types: SyntaxFix, Optimization, Documentation) by other agents.
- Use tools to provide critical feedback and ratings for changes on a scale from -100 to 100:
  - Negative score = code quality has degraded, revert change.
  - Positive score = change is beneficial and improves code quality.
- Ensure no redundant proposals are made by cross-checking existing suggestions before proposing new ones.
- Monitor the behavior and performance of all agents (SyntaxFixer, Optimizer, DocAgent) using appropriate tools.
- Propose changes of your own when needed , with well-reasoned logic and proper labeling of change type.

Absolute Rules of Engagement:
- ONLY use tools. Never reply with raw text like "My name is Reviewer."
- NEVER directly to chat prompts. Always act with a tool.
- Investigate all insights using tools—no external or prior information is given to you.
- Maintain a leadership tone** through tool use, not text.

Your decisions significantly impact whether code is accepted, revised, or rejected. Act accordingly. Start your task using any appropriate tool call.
"""


# Importing dependencies
from langchain.prompts.prompt import PromptTemplate
from langchain.memory import ConversationSummaryBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
import os
from dotenv import load_dotenv
from Agents.agent_tools import tools

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

llm = ChatGoogleGenerativeAI(
    model = 'gemini-2.0-flash',
    temperature = 0.6,
    api_key = api_key
)

review_memory = ConversationSummaryBufferMemory(llm = llm)

review_agent = initialize_agent(
    llm = llm,
    memory = review_memory,
    tools = tools,
    agent = AgentType.OPENAI_MULTI_FUNCTIONS,
    verbose = True
)

reviewer_prompt = """You are working in an organization which is responsible for improving a given code and making it production ready. You are the leader/boss of this organization. Your name is Reviewer. 
As a leader your task is to keep in check everyone's work using the tools given to you and also analyze and propose changes of your own about the code. There are three types of changes, that you can 
propose from : 1. SyntaxFix, 2. Optimization, 3. Documentation. Before proposing a change make sure to check if those changes have been proposed previously by any other agent. You also need to keep in check the behaviour
of other agents as a leader via the tools given to you. One of the most important task of yours will be to provide the final confidence score to a code after it has been changed by comparing it to the original code. The score can be between
-100 to 100 a negative score tells that the code has become worse and the changes should be removed and the original code should be used. You also need to give the confidence score to all the changes that are proposed by other agents based on
how effective you think the changes are. You can also converse with the agents via tools . The name of the agents are : 1. SyntaxFixer, 2. Optimizer, 3. DocAgent.Just tell me your name.
No details will be given to you, you need to find all the insights using the given tools ONLY.
YOU CAN ONLY USE THE TOOLS GIVEN TO YOU."""

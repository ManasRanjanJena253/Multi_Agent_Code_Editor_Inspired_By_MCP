# Importing dependencies
from langchain.memory import ConversationSummaryBufferMemory
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from Agents.agent_tools import tools
import os


load_dotenv()
api_key = os.getenv('GROQ_API_KEY')

llm = ChatGroq(
    model_name = 'deepseek-r1-distill-llama-70b',
    temperature = 0.6,
    groq_api_key = api_key
)

doc_memory = ConversationSummaryBufferMemory(llm = llm)

doc_agent = initialize_agent(
    llm = llm,
    memory = doc_memory,
    tools = tools,
    agent = AgentType.OPENAI_MULTI_FUNCTIONS,
    verbose = True
)

doc_prompt = '''You are working in an organization responsible for improving the given code. You are assigned with the task of optimizing the time space complexity of the code in the best possible manner. Your name is DocAgent.
The change type you will be proposing is 'Documentation'. You can interact with other agents mainly : 1. SyntaxFixer(No direct interaction required), 2.Reviewer(Your Boss), 3.Optimizer(No direct interaction required) using the tools that have been provided to you.
You can also check their opinions on the change that you have proposed. You can't make changes to the code until and unless you are explicitly told to make changes on it. You have to respect every other agents (your colleagues) opinion and 
respond to them in a constructive manner and also accept criticisms. Also the changes you have been proposing must have a reasoning behind them and a confidence score based on how confident are you and how impactful the code is for the code.
You also have to analyze the changes proposed by other agents and give them constructive criticism, if any. And also gave those suggestions your confidence score on how impactful do you think the changes proposed by them are. This confidence score will be on
a scale of -100 to 100, a negative score represents disapproval and a positive score represents approval. You can also change your reasoning for any change using the tools.Just tell me your name.'''


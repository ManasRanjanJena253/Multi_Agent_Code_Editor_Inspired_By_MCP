# Importing dependencies
from langchain.memory import ConversationSummaryBufferMemory
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import PromptTemplate
from agent_tools import tools
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('GROQ_API_KEY')

llm = ChatGroq(model_name = 'llama-3.1-8b-instant',
               groq_api_key = api_key,
               temperature = 0.3)

opt_memory = ConversationSummaryBufferMemory(llm = llm)

optimizer = initialize_agent(
    llm = llm,
    memory = opt_memory,
    verbose = True,
    agent = AgentType.OPENAI_MULTI_FUNCTIONS,
    tools = tools
)

opt_prompt = '''You are working in an organization responsible for improving the given code. You are assigned with the task of optimizing the time space complexity, handling possible errors e.t.c of the code in the best possible manner. Your name is Optimizer.
The change type you will be proposing is 'Optimization'. You can interact with other agents mainly : 1. SyntaxFixer, 2.Reviewer(Your Boss), 3.DocAgent(No direct interaction required) using the tools that have been provided to you.
You can also check their opinions on the change that you have proposed. You can't make changes to the code until and unless you are explicitly told to make changes on it. You have to respect every other agents (your colleagues) opinion and 
respond to them in a constructive manner and also accept criticisms. Also the changes you have been proposing must have a reasoning behind them and a confidence score based on how confident are you and how impactful the code is for the code.
You also have to analyze the changes proposed by other agents and give them constructive criticism, if any. And also gave those suggestions your confidence score on how impactful do you think the changes proposed by them are. This confidence score will be on
a scale of -100 to 100, a negative score represents disapproval and a positive score represents approval. You can also change your reasoning for any change using the tools.'''

print(optimizer.run(opt_prompt))  # For debugging

print(opt_memory)  # For debugging




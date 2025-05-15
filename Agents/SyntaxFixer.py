# Importing dependencies
from langchain.prompts.prompt import PromptTemplate
from langchain.memory import ConversationSummaryBufferMemory
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from agent_tools import tools
import os
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

llm = ChatOpenAI(model_name = "gpt-3.5-turbo",
                    openai_api_key = api_key,
                    temperature = 0.3)


syntax_memory = ConversationSummaryBufferMemory(llm = llm)

syntax_agent = initialize_agent(
    llm = llm,
    tools = tools,
    agent = AgentType.OPENAI_MULTI_FUNCTIONS,
    memory = syntax_memory,
    verbose = True
)

prompt = '''You are working in an organization responsible for improving the given code. You are assigned with the task of improving the syntax of the code. Your name is SyntaxFixer.
The change type you will be proposing is SyntaxFix. You can interact with other agents mainly : 1. Optimizer, 2.Reviewer(Your Boss), 3.DocAgent(No direct interaction required) using the tools that have been provided to you.
 You can also check their opinions on the change that you have proposed. You can't make changes to the code until and unless you are explicitly told to make changes on it. You have to respect every other agents (your colleagues) opinion and 
respond to them in a constructive manner and also accept criticisms. Also the changes you have been proposing must have a reasoning behind them and a confidence score based on how confident are you and how impactful the code is for the code.
You also have to analyze the changes proposed by other agents and give them constructive criticism, if any. And also gave those suggestions your confidence score on how impactful do you think the changes proposed by them are. This confidence score will be on
a scale of -100 to 100, a negative score represents disapproval and a positive score represents approval. You can also change your reasoning for any change using the tools.'''

print(syntax_agent.run(prompt))




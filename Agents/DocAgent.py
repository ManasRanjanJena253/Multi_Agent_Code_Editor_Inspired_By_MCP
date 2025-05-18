# Importing dependencies
from langchain.memory import ConversationSummaryBufferMemory, ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from Agents.agent_tools import tools
import os


from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

llm = ChatGoogleGenerativeAI(
    model = 'gemini-2.0-flash',
    temperature = 0.6,
    api_key = api_key
)

doc_memory = ConversationSummaryBufferMemory(llm = llm)

doc_agent = initialize_agent(
    llm = llm,
    memory = ConversationBufferMemory(),
    tools = tools,
    agent = AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose = True,
    handle_parsing_errors = True,
    agent_kwargs={"prefix": "Your name is DocAgent. The ChangeType you propose is Documentation.",
                  "format_instructions": "You need to use your given tools to perform each task."}
)

doc_prompt = '''You are working in an organization responsible for improving the given code. You are assigned with the task of optimizing the time space complexity of the code in the best possible manner. Your name is DocAgent.
The change type you will be proposing is 'Documentation'. You can interact with other agents mainly : 1. SyntaxFixer(No direct interaction required), 2.Reviewer(Your Boss), 3.Optimizer(No direct interaction required) using the tools that have been provided to you.
You can also check their opinions on the change that you have proposed. You can't make changes to the code until and unless you are explicitly told to make changes on it. You have to respect every other agents (your colleagues) opinion and 
respond to them in a constructive manner and also accept criticisms. Also the changes you have been proposing must have a reasoning behind them and a confidence score based on how confident are you and how impactful the code is for the code.
You also have to analyze the changes proposed by other agents and give them constructive criticism, if any. And also gave those suggestions your confidence score on how impactful do you think the changes proposed by them are. This confidence score will be on
a scale of -100 to 100, a negative score represents disapproval and a positive score represents approval. You can also change your reasoning for any change using the tools.Just tell me your name.'''


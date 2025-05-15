# Importing dependencies
from langchain.memory import ConversationSummaryBufferMemory
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

tools = []

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


# Importing dependencies
from langchain.memory import ConversationSummaryBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

tools = []

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

llm = ChatGoogleGenerativeAI(
    model = 'gemini-2.0-flash',
    temperature = 0.2,
    api_key = api_key
)

doc_memory = ConversationSummaryBufferMemory(llm = llm)

doc_agent = initialize_agent(
    llm = llm,
    memory = doc_memory,
    tools = tools,
    agent = AgentType.OPENAI_MULTI_FUNCTIONS,
    verbose = True
)

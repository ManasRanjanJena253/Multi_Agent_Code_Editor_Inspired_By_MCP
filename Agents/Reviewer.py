# Importing dependencies
from langchain.prompts.prompt import PromptTemplate
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationChain
from langchain_mistralai import ChatMistralAI
from langchain.agents import initialize_agent, AgentType
import os
from dotenv import load_dotenv

tools = []

load_dotenv()
api_key = os.getenv('MISTRAL_API_KEY')

llm = ChatMistralAI(model = 'mistral-small-latest',
                    mistral_api_key = api_key,
                    temperature = 0.3)

review_memory = ConversationSummaryBufferMemory(llm = llm)

review_agent = initialize_agent(
    llm = llm,
    agent = AgentType.OPENAI_MULTI_FUNCTIONS,
    tools = tools,
    verbose = True,
    memory = review_memory
)
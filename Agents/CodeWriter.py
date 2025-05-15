# Importing dependencies
from langchain.prompts import PromptTemplate
import os
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ["MISTRAL_API_KEY"]
mistral_model = "codestral-latest"
llm = ChatMistralAI(model=mistral_model, temperature=0, mistral_api_key=api_key)
print(llm.invoke([("user", "Write a function for fibonacci and give only the code no other words required in the answer")]))
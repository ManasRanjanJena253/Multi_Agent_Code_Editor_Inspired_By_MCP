# Importing dependencies
from langchain.prompts import PromptTemplate
import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain.chains import LLMChain


load_dotenv()
api_key = os.getenv('GROQ_API_KEY')

llm = ChatGroq(model_name = 'compound-beta-mini',
               groq_api_key = api_key,
               temperature = 0.3)


code_prompt = PromptTemplate(template = "You need to write a clean code in {language}. The logic/prompt of the code is : {code}. Give only the code nothing else. No need to converse with the user.",
                             input_variables = ["language", "code"])

code_writer = LLMChain(
    llm = llm,
    prompt = code_prompt
)
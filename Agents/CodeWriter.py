# Importing dependencies
from langchain.prompts import PromptTemplate
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GROQ_API_KEY')

code_writer = ChatGroq(model_name = 'compound-beta-mini',
               groq_api_key = api_key,
               temperature = 0.3)

code_prompt = PromptTemplate(template = "You need to write a clean code in {language}. The logic/prompt of the code is : {code}.",
                             input_variables = ["language", "code"])

print(code_writer.invoke([("user", code_prompt.format(language = 'Python', code = 'Write a code for fibonacci using recursion.'))]))
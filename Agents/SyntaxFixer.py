# Importing dependencies
from langchain.prompts.prompt import PromptTemplate
from langchain.memory import ConversationSummaryBufferMemory
from langchain_mistralai import ChatMistralAI
from langchain.agents import initialize_agent, AgentType
import os
from dotenv import load_dotenv

tools = []

load_dotenv()
api_key = os.getenv('MISTRAL_API_KEY')

llm = ChatMistralAI(model = 'mistral-large-latest',
                    mistral_api_key = api_key,
                    temperature = 0.3)


memory = ConversationSummaryBufferMemory(llm = llm)

syntax_agent = initialize_agent(
    llm = llm,
    tools = tools,
    agent = AgentType.OPENAI_MULTI_FUNCTIONS,
    memory = memory,
    verbose = True
)

prompt = '''You are given the task of finding the syntax error of a given code, you need to perform this task as cleanly
as possible. To correct the syntax of the code you need to follow a process and take into consideration every critique you are given.
The Process is : 
1. You will be given the code, you need to either analyse the code and find error in it or change it, if any. Then provide the proposed change and the confidence score which takes into account how much the change
would improve the code and how confident you are that the proposed change would work and improve its working. You can also give a negative score if you think a particular change would worsen the code.
2. The format in which you will be providing the code will be : {'ChangeType': 'The change you are proposing', 'ConfidenceScore': 'Your confidence score a no. between -100 to 100'}.
3. You won't be making any changes to the code directly unless specified.'''


print(chain.run(prompt))

analysis_prompt = PromptTemplate(template = ('This is the code : {code}. You need to analyze it.'),
                                 input_variables = ['code'])



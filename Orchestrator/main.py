# Importing dependencies
from Agents.DocAgent import doc_agent, doc_memory, doc_prompt
from Agents.Optimizer import optimizer, opt_memory, opt_prompt
from Agents.Reviewer import review_agent, reviewer_prompt, review_memory
from Agents.SyntaxFixer import syntax_agent, syntax_memory, synt_prompt
from Agents.CodeWriter import code_writer, code_prompt
from langchain.prompts import PromptTemplate
from pymongo import MongoClient
import random
from langchain.schema import HumanMessage, AIMessage

client = MongoClient(host = 'localhost', port = 27017)

db = client['Context_Units']
suggested_changes = db['suggested_changes']

code_base = db['CodeBase']
session = db['Session']

def agent_loop(prompt: str):
    """
    Creating a function to invoke the agents again and again.
    :param prompt: The prompt given to the agents.
    :return: None
    """
    doc_agent.invoke({"input": prompt})
    syntax_agent.invoke({"input": prompt})
    optimizer.invoke({"input": prompt})

def agent_workflow(code_id: int, code: str):
    """
    This function contains the complete workflow of how agents go through solving a problem
    """
    # Creating a pre-built memory of the instructions given to the agents.
    syntax_memory.chat_memory.messages.append(
        HumanMessage(content=synt_prompt)
    )
    syntax_memory.chat_memory.messages.append(
        AIMessage(content="Understood. I will follow every rule your provided strictly.")
    )

    doc_memory.chat_memory.messages.append(
        HumanMessage(content=doc_prompt)
    )
    doc_memory.chat_memory.messages.append(
        AIMessage(content="Understood. I will follow every rule your provided strictly.")
    )

    opt_memory.chat_memory.messages.append(
        HumanMessage(content=opt_prompt)
    )
    opt_memory.chat_memory.messages.append(
        AIMessage(content="Understood. I will follow every rule your provided strictly.")
    )

    review_memory.chat_memory.messages.append(
        HumanMessage(content=reviewer_prompt)
    )
    review_memory.chat_memory.messages.append(
        AIMessage(content="Understood. I will follow every rule your provided strictly.")
    )

    # Giving the code to the agents.
    agent_loop(prompt = f"The code had been provided by the user. The code_id is {code_id}. The code is : \n {code}, you need to view the code using ONLY the tools given to you. Refer to your memory for further details about what to do.")

    # Making the agents propose changes
    agent_loop(prompt = f"Now, propose some changes to the code using ONLY the tools given to you such as propose_change tool. No need to propose changes if, no major flaws, just do NOTHING in that case.")

    # Reviewing the changes proposed
    agent_loop(prompt = f"Now, all the changes have been proposed by the agents. Check every agents opinions using ONLY the tools given to you.")
    review_agent.invoke({"input": f"Now, all the changes have been proposed by the agents. Check every agents opinions using ONLY the tools given to you."})

    # Give scores
    agent_loop(prompt = "Give your confidence_score to the proposed changes. using ONLY the tools given to you.")
    review_agent.invoke({"input": "Give your confidence_score to the proposed changes. using ONLY the tools given to you."})

    # Check for approval
    agent_loop(prompt = f"Now check if any of the changes you proposed can be executed or not. Using ONLY the tools given to you.")

    # Checking the executed changes
    review_agent.invoke({"input": "Check the agents that have been executed till now. Using ONLY the tools given to you."})

    # Interact with agent
    review_agent.invoke({"input": "If any anomaly found during checking executed changes. Interact with the agents using ONLY the tools given to you."})

    print("One Cycle Done !!!")


def workflow(task : str, language : str, prompt : str = None, user_code : str = None):
    """This function contains the full workflow of the agents, a particular prompt of original_code is provided.
    :param task : This is the task which the user want to do. It can either be CodeWriting or CodeModification.
    :param user_code : This is the original_code provided to the agents.
    :param language : This is the language in which the original_code is given or should be written in.
    :param prompt : This is the prompt given to write the original_code. ONLY used in case of CodeWriting."""

    code_id = random.randrange(1, 1000)
    session_id = random.randrange(5, 5000, 3)

    agent_prompt = PromptTemplate(
        template="The code_id for the original_code is {code_id}. The original_code is to be written in {language}. The original_code is : {code}",
        input_variables=["code_id", "language", "code"])

    if task == 'CodeWriting' :
        original_code = code_writer.run({"language": language, "code": prompt})
    else :
        original_code = user_code

    code_base.insert_one({"CodeId": code_id, "Code": original_code})
    print(code_id)

    while True:
        code = code_base.find_one({"CodeId": code_id})["Code"]

        agent_workflow(code_id, code)

        total_changes = suggested_changes.count_documents({})
        total_executed_changes = suggested_changes.count_documents({"Executed": {"$exists": True}})

        if total_changes == total_executed_changes and total_changes !=0 :
            updated_code = code_base.find_one({"CodeId": code_id})["Code"]
            session.insert_one(
                {"SessionId": session_id, "CodeId": code_id, "OriginalCode": original_code, "UpdatedCode": updated_code,
                 "TotalChanges": total_executed_changes, "TaskType": task, "Language": language})
            final_answer = review_agent.invoke({"input": """"Now, all the changes have been made to the original_code. Provide the user with the corrected original_code ONLY. 
            With suitable quantitative measures of how much improved the original_code is now. To check how much the original_code has improved check the view_code and compare it to original."""})

            return final_answer

        elif total_changes == 0 :
            review_agent.invoke({"input": reviewer_prompt + f"Your name : Reviewer. The agents are not proposing any changes, using interact_with_agent tool encourage every agent to propose changes. The original_code id is {code_id}"})
            print("Done")

        else :
            print("started")
            agent_workflow(code_id, code)

if __name__ == "__main__" :
    print(workflow(task = "CodeWriting", language = "Python", prompt = "Write me a code to create a simple gui using flask."))

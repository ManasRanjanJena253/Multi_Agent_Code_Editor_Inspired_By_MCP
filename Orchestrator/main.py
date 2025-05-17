# Importing dependencies
from Agents.DocAgent import doc_agent, doc_memory, doc_prompt
from Agents.Optimizer import optimizer, opt_memory, opt_prompt
from Agents.Reviewer import review_agent, review_memory, reviewer_prompt
from Agents.SyntaxFixer import syntax_agent, syntax_memory, synt_prompt
from Agents.CodeWriter import code_writer, code_prompt
from langchain.prompts import PromptTemplate
from pymongo import MongoClient
import random
import time

client = MongoClient(host = 'localhost', port = 27017)

db = client['Context_units']
suggested_changes = db['suggested_changes']

total_changes = suggested_changes.count_documents({})
executed_changes = suggested_changes.find({"Executed": {"$exists": True}})
total_executed_changes = len(executed_changes)
code_base = db['Code_Base']
session = db['Session']

def workflow(task : str, language : str, prompt : str = None, user_code : str = None):
    """This function contains the full workflow of the agents, a particular prompt of code is provided.
    :param task : This is the task which the user want to do. It can either be CodeWriting or CodeModification.
    :param user_code : This is the code provided to the agents.
    :param language : This is the language in which the code is given or should be written in.
    :param code_id : Unique id given to each code.
    :param prompt : This is the prompt given to write the code. ONLY used in case of CodeWriting."""

    code_id = random.randrange(1, 1000)
    session_id = random.randrange(5, 5000, 3)

    doc_agent.run(doc_prompt)
    syntax_agent.run(synt_prompt)
    review_agent.run(reviewer_prompt)
    optimizer.run(opt_prompt)
    agent_prompt = PromptTemplate(
        template="The code_id for the code is {code_id}. You can now start working on this code.",
        input_variables=["code_id"])

    if task == 'CodeWriting' :
        code = code_writer.invoke(["user", code_prompt.format(language = language, code = prompt)])
    else :
        code = user_code

    code_base.insert_one({"CodeId": code_id, "Code": code})
    doc_agent.run(agent_prompt.format(code_id=code_id))
    syntax_agent.run(agent_prompt.format(code_id=code_id))
    review_agent.run(agent_prompt.format(code_id=code_id))
    optimizer.run(agent_prompt.format(code_id=code_id))

    time.sleep(10)  # Giving agents time to propose changes

    while total_changes != total_executed_changes:
        doc_agent.run("Keep going, all changes have not yet been evaluated.")
        syntax_agent.run("Keep going, all changes have not yet been evaluated.")
        review_agent.run("Keep going, all changes have not yet been evaluated.")
        optimizer.run("Keep going, all changes have not yet been evaluated.")
        time.sleep(2)

    else:
        updated_code = code_base.find_one({"CodeId": code_id})["Code"]
        session.insert_one({"SessionId": session_id, "CodeId": code_id, "OriginalCode": code, "UpdatedCode": updated_code, "TotalChanges": total_executed_changes, "TaskType": task, "Language": language})
        final_answer = review_agent.run("""Now, all the changes have been made to the code. Provide the user with the corrected code ONLY. 
        With suitable quantitative measures of how much improved the code is now.""")

        return final_answer












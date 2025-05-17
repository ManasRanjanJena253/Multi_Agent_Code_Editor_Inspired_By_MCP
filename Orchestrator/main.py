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

db = client['Context_Units']
suggested_changes = db['suggested_changes']

code_base = db['CodeBase']
session = db['Session']

def workflow(task : str, language : str, prompt : str = None, user_code : str = None):
    """This function contains the full workflow of the agents, a particular prompt of code is provided.
    :param task : This is the task which the user want to do. It can either be CodeWriting or CodeModification.
    :param user_code : This is the code provided to the agents.
    :param language : This is the language in which the code is given or should be written in.
    :param prompt : This is the prompt given to write the code. ONLY used in case of CodeWriting."""

    code_id = random.randrange(1, 1000)
    session_id = random.randrange(5, 5000, 3)

    doc_agent.run(doc_prompt)
    syntax_agent.run(synt_prompt)
    review_agent.run(reviewer_prompt)
    optimizer.run(opt_prompt)
    agent_prompt = PromptTemplate(
        template="The code_id for the code is {code_id}. The code is to be written in {language}. You now need to start proposing changes using the tools provided and also evaluating other provided changes.",
        input_variables=["code_id", "language"])

    if task == 'CodeWriting' :
        code = code_writer.run({"language": language, "code": prompt})
    else :
        code = user_code

    code_base.insert_one({"CodeId": code_id, "Code": code})
    print(code_id)
    doc_agent.run(agent_prompt.format(code_id = code_id, language = language))
    syntax_agent.run(agent_prompt.format(code_id = code_id, language = language))
    review_agent.run(agent_prompt.format(code_id = code_id, language = language))
    optimizer.run(agent_prompt.format(code_id = code_id, language = language))

    while True:
        total_changes = suggested_changes.count_documents({})
        total_executed_changes = suggested_changes.count_documents({"Executed": {"$exists": True}})

        if total_changes == total_executed_changes and total_changes !=0 :
            updated_code = code_base.find_one({"CodeId": code_id})["Code"]
            session.insert_one(
                {"SessionId": session_id, "CodeId": code_id, "OriginalCode": code, "UpdatedCode": updated_code,
                 "TotalChanges": total_executed_changes, "TaskType": task, "Language": language})
            final_answer = review_agent.run("""Now, all the changes have been made to the code. Provide the user with the corrected code ONLY. 
            With suitable quantitative measures of how much improved the code is now. To check how much the code has improved check the view_code and compare it to original.""")

            doc_memory.clear()
            syntax_memory.clear()
            review_memory.clear()
            opt_memory.clear()

            return final_answer

        elif total_changes == 0 :
            doc_agent.run("Your name : DocAgent, Your ChangeType : Documentation" + agent_prompt.format(code_id=code_id, language=language))
            syntax_agent.run("Your name : SyntaxFixer, Your ChangeType : SyntaxFix." + agent_prompt.format(code_id=code_id, language=language))
            review_agent.run("Your name : Reviewer." + agent_prompt.format(code_id=code_id, language=language))
            optimizer.run("Your name : Optimizer, Your ChangeType : Optimization." + agent_prompt.format(code_id=code_id, language=language))
            time.sleep(5)
            print("Done")

        else :
            print("started")
            doc_agent.run("Your name : DocAgent, Your ChangeType : Documentation. Keep going, all changes have not yet been evaluated for the previously given code.")
            time.sleep(2)
            syntax_agent.run("Your name : SyntaxFixer, Your ChangeType : SyntaxFix. Keep going, all changes have not yet been evaluated for the previously given code.")
            time.sleep(2)
            review_agent.run("Your name : Reviewer. Keep going, all changes have not yet been evaluated for the previously given code.")
            time.sleep(2)
            optimizer.run("Your name : Optimizer, Your ChangeType : Optimization. Keep going, all changes have not yet been evaluated for the previously given code.")
            time.sleep(2)


if __name__ == "__main__" :
    print(workflow(task = "CodeWriting", language = "Python", prompt = "Write me a code to create a simple gui using flask."))

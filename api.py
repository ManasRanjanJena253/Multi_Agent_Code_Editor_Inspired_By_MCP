# Importing dependencies
from fastapi import FastAPI
from Orchestrator.main import workflow
from pymongo import MongoClient

client = MongoClient(host = "localhost", port = 27017)
db = client["Context_Units"]
session = db["Session"]
code_base = db["Code_Base"]

app = FastAPI()

@app.post(path = "/start-session")
def start_session(task : str, language : str, prompt : str = None, user_code : str = None) :
    """
    This is to be used when the user starts a session.
    :param task: What task is the user wanting to perform. It can be either CodeWriting or CodeModification.
    :param language: The programming language in which the user want to work in.
    :param prompt: The prompt given by the user if any.
    :param user_code: The code provided by the user.
    :return: Dictionary containing final answer(Modified code)
    """
    if task == "CodeWriting" :
        response = workflow(task = task, language = language, prompt = prompt)
        return {"FinalAnswer": response}

    else :
        response = workflow(task = task, language = language, user_code = user_code)
        return {"FinalAnswer": response}

@app.get(path = "/session/{session_id}")
def session_summary(session_id : int) :
    """
    This is to be used to get the details about a particular session.
    :param session_id: A unique id given to each session.
    """
    check = session.find_one({"SessionId": session_id})
    if check :
        return check

    else :
        return {"Error": f"No record of session_id: {session_id} found."}

@app.get(path = "/code/{code_id}")
def show_current_code(code_id : int) :
    """
    This is used to get the current code which the agents are modifying.
    :param code_id: A uniques id given to each code.
    """
    check = code_base.find_one({"CodeId": code_id})
    if check :
        return {"CurrentCode": check["Code"]}

    else :
        return {"Error": f"No record of code_id: {code_id} found"}

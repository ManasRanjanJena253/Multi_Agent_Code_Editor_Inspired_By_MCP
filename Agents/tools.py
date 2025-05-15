# Importing dependencies
from langchain.agents import tool
from langchain.tools import StructuredTool
from pymongo import MongoClient
from langchain.prompts import PromptTemplate
from SyntaxFixer import syntax_agent
from Optimizer import optimizer
from DocAgent import doc_agent
from Reviewer import review_agent

# Connecting to the MongoDB client
client = MongoClient(host = 'localhost', port = 27017)

db = client['Context_units']
suggested_changes = db['suggested_changes']    # Collection for logging in the infos
agent_workspace = db['agent_workspace']    # Collection to view changes and discuss upon those changes.

@tool('fetch_recommended_changes')
def fetch_recommended_changes(code_id : int, change_id : int):
    """This function will be used to get all the changes recommended for a given snippet of code."""
    changes = suggested_changes.find({"CodeId": code_id, "ChangeId": change_id})
    return changes

@tool('get_executed_changes')
def get_executed_changes(code_id : int):
    """This function will be used to get all the executed changes and final_confidence sore of each change."""
    executed = suggested_changes.find({"CodeId": code_id, "Executed": True})
    return executed

@tool('submit_score')
def submit_score(code_id : int, change_id : int, source_agent : str, score : int, reasoning : str):
    """This function will be used by agent to submit its confidence score/opinion about a particular change."""
    approved = True    # If the score is positive, the agent agrees with the change.
    if score < 0:
        approved = False

    change = suggested_changes.find_one({"CodeId": code_id, "ChangeId": change_id})   # Finding the changes for that code id and change id.
    change_type = change['ChangeType']
    if source_agent == 'DocAgent' and change_type != 'Documentation' :    # Restricting the access to other agents to decrease unnecessary noise and hallucination.
        return "Access denied for this particular Change type."

    if source_agent in ['SyntaxFixer', 'Optimizer'] and change_type == 'Documentation':
        return "Access denied for this particular Change type"

    agent_workspace.insert_one({"CodeId": code_id, "ChangeId": change_id, "SourceAgent": source_agent,
                                "Reasoning": reasoning, "Approved": approved, "ConfidenceScore": score})

@tool('propose_change')
def propose_change(code_id : int, change_id : int, content : str, change_type : str, agent_name : str):
    docs = suggested_changes.find({"CodeId": code_id})
    for k in docs:
        if k["ChangeId"] == change_id:
            return "!!! THIS CHANGE_ID EXISTS ALREADY. TRY WITH OTHER CHANGE_ID !!!"
    valid_changes = ['Documentation', 'SyntaxFix', 'Optimization']
    if change_type not in valid_changes:
        return "!!! CHANGE TYPE DOESN'T EXIST !!!"
    else:
        if agent_name == 'DocAgent' and change_type != 'Documentation':  # Restricting the access to other agents to decrease unnecessary noise and hallucination.
            return "YOU ARE NOT AUTHORIZED FOR THIS CHANGE."

        if agent_name in ['SyntaxFixer', 'Optimizer'] and change_type == 'Documentation':
            return "YOU ARE NOT AUTHORIZED FOR THIS CHANGE"

        suggested_changes.insert_one({"CodeId": code_id, "ChangeId": change_id, "Content": content, "ChangeType": change_type})



@tool('check_opinion')
def check_opinion(code_id : int, change_id : int, source_agent : str = None):
    """This functions lets the agent see the opinion and reasoning of other agents or an agent in particular."""
    if source_agent:
        doc = agent_workspace.find_one({"CodeId": code_id, "ChangeId": change_id, "SourceAgent": source_agent},
                                       {"ConfidenceScore": 1, "Reasoning": 1, "_id": 0})
    else:
        doc = agent_workspace.find_one({"CodeId": code_id, "ChangeId": change_id},
                                       {"SourceAgent": source_agent, "ConfidenceScore": 1, "Reasoning": 1, "_id": 0})

    return doc

@tool('interact_with_agent')
def interact_with_agent(code_id : int, change_id : int, agent_name : str, source_agent : str, message : str):
    """This function enables the agents to interact with each other upon a single change and come to a common reasoning."""

    if source_agent == agent_name:
        return "!!! YOU CAN'T MESSAGE YOURSELF !!!"

    valid_coding_agents = ["SyntaxFixer", "Optimizer", "Reviewer"]
    valid_doc_agents = ["DocAgent", "Reviewer"]
    prompt = PromptTemplate(template = ('''I am the {agent_name}, I want to discuss/share my opinions on your suggestion for CodeId = {code_id} and ChangeId = {change_id}
    My message/suggestion is : {message}'''),
                            input_variables = ['agent_name', 'code_id', 'change_id', 'message'])

    convo = prompt.format(agent_name = agent_name, code_id = code_id, change_id = change_id, message = message)

    if agent_name in valid_coding_agents and source_agent in valid_coding_agents:
        if source_agent == 'SyntaxFixer':
            syntax_agent.run(convo)
        elif source_agent == 'Optimizer':
            optimizer.run(convo)
        else:
            return "Reviewer Can't be interacted with to keep its decisions unbiased."

    elif agent_name in valid_doc_agents and source_agent in valid_doc_agents:
        if source_agent == 'DocAgent':
            doc_agent.run(convo)
        elif source_agent == 'Reviewer':
            review_agent.run(convo)

    else :
        return "The model you are trying to communicate with is Out of your Scope."

@tool('change_reasoning')
def change_reasoning(agent_name : str, code_id : int, change_id : int, new_reasoning : str):
    """This function will allow the agents to change their opinions if they felt like it after discussing with other agents."""
    agent_workspace.update_one({"CodeId": code_id, "ChangeId": change_id, "SourceAgent": agent_name},
                                        {"$set" : {"Reasoning": new_reasoning}})









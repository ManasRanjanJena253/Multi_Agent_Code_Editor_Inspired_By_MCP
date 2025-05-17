# Importing dependencies
from langchain.agents import tool
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from pymongo import MongoClient
from langchain.prompts import PromptTemplate
import random

# Connecting to the MongoDB client
client = MongoClient(host = 'localhost', port = 27017)

db = client['Context_units']
suggested_changes = db['suggested_changes']    # Collection for logging in the infos
agent_workspace = db['agent_workspace']    # Collection to view changes and discuss upon those changes.

def generate_change_id():
    """This function will be used to generate change id at random."""
    change_id = random.randrange(1, 1000)
    return change_id

@tool('fetch_recommended_changes')
def fetch_recommended_changes(code_id : int, change_id : int):
    """
    This function will be used to get all the changes recommended for a given snippet of code.
    :param code_id : It's the unique CodeId of the code you want to use any tools on.
    :param change_id : It's the unique ChangeId of the change proposed by an agent for a particular code.
    """

    changes = suggested_changes.find({"CodeId": code_id, "ChangeId": change_id})
    return changes

@tool('get_executed_changes')
def get_executed_changes(code_id : int):
    """This function will be used to get all the executed changes and final_confidence sore of each change.
    :param code_id : It's the unique CodeId of the code you want to use any tools on."""
    executed = suggested_changes.find({"CodeId": code_id, "Executed": True})
    return executed

@tool('submit_score')
def submit_score(code_id : int, change_id : int, source_agent : str, score : int, reasoning : str):
    """
    This function will be used by agent to submit its confidence score/opinion about a particular change.
    :param code_id : It's the unique CodeId of the code you want to use any tools on.
    :param change_id : It's the unique ChangeId of the change proposed by an agent for a particular code.
    :param source_agent : It's the name of the agent who is submitting the score.
    :param score : This is the confidence score that you are going to submit.
    :param reasoning : This is the reasoning to justify the score you gave.
    """

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
def propose_change(code_id : int, content : str, change_type : str, agent_name : str):
    """
    This function can be used to propose changes regarding the code that has been given to the agent.
    :param code_id : It's the unique CodeId of the code you want to use any tools on.
    :param content : It's the change that you are proposing.
    :param change_type : It's the change type that you are proposing. It can be of three types : 1. SyntaxFix, 2. Optimization, 3. Documentation.
    :param agent_name : It's the name of the agent who is proposing the change.
    """
    docs = suggested_changes.find({"CodeId": code_id})
    change_id = generate_change_id()
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
        return "Your Purpose Added Successfully"


@tool('check_opinion')
def check_opinion(code_id : int, change_id : int, source_agent : str = None):
    """
    This functions lets the agent see the opinion and reasoning of other agents or an agent in particular, so they can interact with each other
    if they don't like some agents working style.
    :param code_id : It's the unique CodeId of the code you want to use any tools on.
    :param change_id : It's the unique ChangeId of the change proposed by an agent for a particular code.
    :param source_agent : It's optional, enter this only if you want to check the opinion of a particular agent. If not entered you will get the opinions of all the agents.
    """
    if source_agent:
        doc = agent_workspace.find_one({"CodeId": code_id, "ChangeId": change_id, "SourceAgent": source_agent},
                                       {"ConfidenceScore": 1, "Reasoning": 1, "_id": 0})
    else:
        doc = agent_workspace.find_one({"CodeId": code_id, "ChangeId": change_id},
                                       {"SourceAgent": source_agent, "ConfidenceScore": 1, "Reasoning": 1, "_id": 0})

    return doc

@tool('interact_with_agent')
def interact_with_agent(code_id : int, change_id : int, agent_name : str, source_agent : str, message : str):
    """
    This function enables the agents to interact with each other upon a single change and come to a common reasoning.
    :param code_id : It's the unique CodeId of the code you want to use any tools on.
    :param change_id : It's the unique ChangeId of the change proposed by an agent for a particular code.
    :param source_agent : It's the name of the agent you want to interact with.
    :param agent_name : It's the name of the agent who is using this tool.
    :param message : It's the message you want to send to the source_agent.
    """
    from SyntaxFixer import syntax_agent
    from Optimizer import optimizer
    from DocAgent import doc_agent
    from Reviewer import review_agent

    if source_agent == agent_name:
        return "!!! YOU CAN'T MESSAGE YOURSELF !!!"

    valid_coding_agents = ["SyntaxFixer", "Optimizer", "Reviewer"]
    valid_doc_agents = ["DocAgent", "Reviewer"]
    prompt = PromptTemplate(template = ('''I am the {agent_name}, I want to discuss/share my opinions on your suggestion for 
                                        CodeId = {code_id} and ChangeId = {change_id}. My message/suggestion is : {message}'''),
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

@tool('delete_proposal')
def delete_proposal(agent_name : str, code_id : int, change_id : int):
    """
    This function will allow the agents to delete their proposed changes, if they no longer believe in that change.
    :param agent_name : Name of the agent who is using this function to delete.
    :param code_id : It's the unique CodeId of the code you want to use any tools on.
    :param change_id : It's the unique ChangeId of the change proposed by an agent for a particular code."""

    agent_workspace.delete_one({"CodeId": code_id, "ChangeId": change_id, "SourceAgent": agent_name})
    return "The specified change deleted successfully."


@tool('give_final_confidence_score')
def give_final_confidence_score(agent_name : str, code_id : int, change_id : int, final_score : int):
    """This function enables the reviewer agent to give final confidence score to the edited code. It's calculated by comparing it to original code."""
    if agent_name != 'Reviewer':
        return "!!! You are not authorised to give the final score !!!"
    else :
        suggested_changes.update_one({"CodeId": code_id, "ChangeId": change_id},
                                     {"$set": {"Final_Confidence_Score": final_score}})

        return "Fincal confidence score give successfully."

@tool('execute_changes')
def execute_changes(change_type : str, change_id : int, code_id : int):
    """
    Function through which they can check if there suggested change is approved or not. If approved they can now apply that change to the id.
    :param change_type : This is the type of change you want to enquire for to see if it's approved by other agents to be executed.
    :param code_id : It's the unique CodeId of the code you want to use any tools on.
    :param change_id : It's the unique ChangeId of the change proposed by an agent for a particular code."""

    from SyntaxFixer import syntax_agent
    from Optimizer import optimizer
    from DocAgent import doc_agent

    opinions = agent_workspace.find({"CodeId": code_id, "ChangeId": change_id})
    opinion_count = len(opinions)
    approved = agent_workspace.find({"CodeId": code_id, "ChangeId": change_id, "Approved": True})
    approval_count = len(approved)
    if opinion_count == approval_count:
        agg_score = 0
        for k in approved:
            agg_score += k["ConfidenceScore"]
        if agg_score >= 80:
            prompt = """Your proposed changes have been approved, now you can make changes to the code based on the proposed change."""
            if change_type == 'SyntaxFix':
                syntax_agent.run(prompt)
                agent_workspace.delete_many({"CodeId": code_id, "ChangeId": change_id})
                suggested_changes.update_one({"CodeId": code_id, "ChangeId": change_id},
                                             {"$set": {"Executed": True}})
            elif change_type == 'Optimization' :
                optimizer.run(prompt)
                agent_workspace.delete_many({"CodeId": code_id, "ChangeId": change_id})
                suggested_changes.update_one({"CodeId": code_id, "ChangeId": change_id},
                                             {"$set": {"Executed": True}})
            else :
                doc_agent.run(prompt)
                agent_workspace.delete_many({"CodeId": code_id, "ChangeId": change_id})
                suggested_changes.update_one({"CodeId": code_id, "ChangeId": change_id},
                                             {"$set": {"Executed": True}})
        else :
            return "Some agents don't think the change is necessary or that impactful. Plz try finding them (check_opinions) and interacting with them through interact_with_agent tool"
    else :
        not_approve_agent = agent_workspace.find({"CodeId": code_id, "ChangeId": change_id, "Approved": False})
        agents = []
        if not_approve_agent :
            for k in not_approve_agent:
                agents.append(k['SourceAgent'])

            return f"The agents who disapproved your change are : {agents}. Try contacting them through interact_with_agent tool for there opinion or check there reasoning using check_opinion tool"


# Creating an args_schema for the inputs of our functions

class ToolInput(BaseModel):
    agent_name : str = Field(default = "", description = "This is the name of the agent who is performing/calling the tools")
    source_agent : str = Field(default = "", description = "This is the name of the agent who have given a particular suggestion or change regarding the code.")
    code_id : int = Field(default = "", description = "This is the unique id for a code. It's same for the same piece of code.")
    change_id : int = Field(default = "", description = "This is the unique id for a change.")
    score : int = Field(default = "", description = "This is the confidence score given to a change by a model when analyzing it.")
    message : str = Field(default = "", description = "This is the message given by the agent to communicate with other agent.")
    new_reasoning : str = Field(default = "", description = "This is the reasoning which is to be replaced in place of original reasoning by an agent, if it changed it's decision")
    final_score : int = Field(default = "", description = "This is the final score given to the final code by the Reviewer Agent. It's based on its improvement compared to original code")
    reasoning : str = Field(default = "", description = "This is the reason given by an agent for its proposed change, or the reason or the opinion of other agents on some change.")
# Creating StructuredTools for better usage by the agent

tools = [
    StructuredTool.from_function(
        func = fetch_recommended_changes,
        name = "fetch_recommended_changes",
        description = "This function is to be used to get all the changes proposed for a given code after giving the codes id as argument. Used for reviewing purposes.",
        args_schema = ToolInput
    ),
    StructuredTool.from_function(
        func = get_executed_changes,
        name = "get_executed_changes",
        description = "This function is to be used to get all the changes which have been executed till now for a particular code. It is for reviewing what are the changes done to the original code and giving final confidence score.",
        args_schema = ToolInput
    ),
    StructuredTool.from_function(
        func = submit_score,
        name = "submit_score",
        description = "This function is to be used to enable agents to give their own confidence score and reasoning/opinion to a particular change that is recommended. The score lies between -100 to 100. Negative if you don't agree with the change and positive if you agree.",
        args_schema = ToolInput
    ),
    StructuredTool.from_function(
        func = propose_change,
        name = 'propose_change',
        decription = "Using this function you can propose your own changes for the code and let other agents review it.",
        args_schema = ToolInput
    ),
    StructuredTool.from_function(
        func = check_opinion,
        name = "check_opinion",
        description = "Using this function you can check the opinions of other agents about a particular change.",
        args_schema = ToolInput
    ),
    StructuredTool.from_function(
        func = interact_with_agent,
        name = "interact_with_agent",
        description = "This function enables you to interact with other agents. You can use both for sending message and also replying to a sent message.",
        args_schema = ToolInput
    ),
    StructuredTool.from_function(
        func = delete_proposal,
        name = "delete_proposal",
        description = "You can use this function to delete a particular change that you have proposed and now don't want it to be executed, or you just changed your mind about that change.",
        args_schema = ToolInput
    ),
    StructuredTool.from_function(
        func = give_final_confidence_score,
        name = "give_final_confidence_score",
        description = "This function is ONLY for Reviewer Agent. This enables the agent to give its final score after comparing the original code and changed code on a scale of 1 to 100.",
        args_schema = ToolInput
    ),
    StructuredTool.from_function(
        func = execute_changes,
        name = "execute_changes",
        description = "This function allows the agent to check whether you can execute the change with a particular id or not. It also enables it see which agents disapproved its proposed change.",
        args_schema = ToolInput
    )]
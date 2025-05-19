# Importing dependencies
from langchain.tools import tool
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from pymongo import MongoClient
from langchain.prompts import PromptTemplate
import random
from typing import Optional

# Connecting to the MongoDB client
client = MongoClient(host = 'localhost', port = 27017)

db = client['Context_Units']
suggested_changes = db['suggested_changes']    # Collection for logging in the infos
agent_workspace = db['agent_workspace']    # Collection to view changes and discuss upon those changes.
code_base = db['CodeBase']

class ViewCodeInput(BaseModel):
    code_id: int

class ProposeChange(BaseModel):
    code_id: int
    content: str
    change_type: str
    agent_name: str

class GetExecuteChangesInput(BaseModel):
    code_id: int

class SubmitScoreInput(BaseModel):
    code_id: int
    change_id: int
    source_agent: str
    score: int
    reasoning: str

class FetchRecommendedChangesInput(BaseModel):
    code_id: int
    change_id: int

class FetchCodeWithChangesInput(BaseModel):
    code_id: int

class InteractWithAgentInput(BaseModel):
    code_id: int
    change_id: int
    agent_name: str
    source_agent: str
    message: str

class FinalReviewInput(BaseModel):
    agent_name: str
    code_id: int
    change_id: int
    final_score: int

class ExecuteChanges(BaseModel):
    change_type: str
    change_id: int
    code_id: int

class DeleteProposal(BaseModel):
    agent_name: str
    code_id: int
    change_id: int

class CheckOpinion(BaseModel):
    code_id: int
    change_id: int
    source_agent: str = None

def generate_change_id():
    """This function will be used to generate change id at random."""
    change_id = random.randrange(1, 1000)
    return change_id

@tool('view_code', args_schema = ViewCodeInput)
def view_code(code_id : int):
    """
    This function is used to view the code with the specific code_id.
    :param code_id: It's the unique CodeId of the code you want to use any tools on.
    """
    data = code_base.find_one({"CodeId": code_id})
    return data['Code']

@tool('fetch_recommended_changes', args_schema = FetchRecommendedChangesInput)
def fetch_recommended_changes(code_id : int, change_id : int):
    """
    This function will be used to get all the changes recommended for a given snippet of code.
    :param code_id: It's the unique CodeId of the code you want to use any tools on.
    :param change_id: It's the unique ChangeId of the change proposed by an agent for a particular code.
    """

    changes = suggested_changes.find({"CodeId": code_id, "ChangeId": change_id})
    return list(changes)

@tool('get_executed_changes', args_schema = GetExecuteChangesInput)
def get_executed_changes(code_id : int):
    """This function will be used to get all the executed changes and final_confidence sore of each change.
    :param code_id: It's the unique CodeId of the code you want to use any tools on."""
    executed = suggested_changes.find({"CodeId": code_id, "Executed": True})
    return list(executed)

@tool('submit_score', args_schema = SubmitScoreInput)
def submit_score(code_id : int, change_id : int, source_agent : str, score : int, reasoning : str):
    """
    This function will be used by agent to submit its confidence score/opinion about a particular change.
    :param code_id: It's the unique CodeId of the code you want to use any tools on.
    :param change_id: It's the unique ChangeId of the change proposed by an agent for a particular code.
    :param source_agent: It's the name of the agent who is submitting the score.
    :param score: This is the confidence score that you are going to submit.
    :param reasoning: This is the reasoning to justify the score you gave.
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

@tool('propose_change', args_schema = ProposeChange)
def propose_change(code_id : int, content : str, change_type : str, agent_name : str):
    """
    This function can be used to propose changes regarding the code that has been given to the agent.
    :param code_id: It's the unique CodeId of the code you want to use any tools on.
    :param content: It's the change that you are proposing.
    :param change_type: It's the change type that you are proposing. It can be of three types : 1. SyntaxFix, 2. Optimization, 3. Documentation.
    :param agent_name: It's the name of the agent who is proposing the change.
    """
    docs = suggested_changes.find({"CodeId": code_id})
    change_id = generate_change_id()
    for k in docs:
        if k["ChangeId"] == change_id:
            return "!!! THIS CHANGE_ID EXISTS ALREADY. TRY WITH OTHER CHANGE_ID !!!"
    """valid_changes = ['Documentation', 'SyntaxFix', 'Optimization']
    if change_type not in valid_changes:
        return "!!! CHANGE TYPE DOESN'T EXIST !!!"
    else:
        if agent_name == 'DocAgent' and change_type != 'Documentation':  # Restricting the access to other agents to decrease unnecessary noise and hallucination.
            return "YOU ARE NOT AUTHORIZED FOR THIS CHANGE."

        if agent_name in ['SyntaxFixer', 'Optimizer'] and change_type == 'Documentation':
            return "YOU ARE NOT AUTHORIZED FOR THIS CHANGE"""
    suggested_changes.insert_one({"CodeId": code_id, "ChangeId": change_id, "Content": content, "ChangeType": change_type})
    return "Your Proposal Added Successfully"


@tool('check_opinion', args_schema = CheckOpinion)
def check_opinion(code_id : int, change_id : int, source_agent : str = None):
    """
    This functions lets the agent see the opinion and reasoning of other agents or an agent in particular, so they can interact with each other
    if they don't like some agents working style.
    :param code_id: It's the unique CodeId of the code you want to use any tools on.
    :param change_id: It's the unique ChangeId of the change proposed by an agent for a particular code.
    :param source_agent: It's optional, enter this only if you want to check the opinion of a particular agent. If not entered you will get the opinions of all the agents.
    """
    if source_agent:
        doc = agent_workspace.find_one({"CodeId": code_id, "ChangeId": change_id, "SourceAgent": source_agent},
                                       {"ConfidenceScore": 1, "Reasoning": 1, "_id": 0})
    else:
        doc = agent_workspace.find_one({"CodeId": code_id, "ChangeId": change_id},
                                       {"SourceAgent": source_agent, "ConfidenceScore": 1, "Reasoning": 1, "_id": 0})

    return doc

@tool('interact_with_agent', args_schema = InteractWithAgentInput)
def interact_with_agent(code_id : int, change_id : int, agent_name : str, source_agent : str, message : str):
    """
    This function enables the agents to interact with each other upon a single change and come to a common reasoning.
    :param code_id: It's the unique CodeId of the code you want to use any tools on.
    :param change_id: It's the unique ChangeId of the change proposed by an agent for a particular code.
    :param source_agent: It's the name of the agent you want to interact with.
    :param agent_name: It's the name of the agent who is using this tool.
    :param message: It's the message you want to send to the source_agent.
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

@tool('delete_proposal', args_schema = DeleteProposal)
def delete_proposal(agent_name : str, code_id : int, change_id : int):
    """
    This function will allow the agents to delete their proposed changes, if they no longer believe in that change.
    :param agent_name: Name of the agent who is using this function to delete.
    :param code_id: It's the unique CodeId of the code you want to use any tools on.
    :param change_id: It's the unique ChangeId of the change proposed by an agent for a particular code."""

    agent_workspace.delete_one({"CodeId": code_id, "ChangeId": change_id, "SourceAgent": agent_name})
    return "The specified change deleted successfully."


@tool('give_final_confidence_score', args_schema = FinalReviewInput)
def give_final_confidence_score(agent_name : str, code_id : int, change_id : int, final_score : int):
    """
    This function enables the reviewer agent to give final confidence score to the edited code. It's calculated by comparing it to original code.
    :param agent_name: The name of the agent who is providing the confidence score.
    :param code_id: It's the unique CodeId of the code you want to use any tools on.
    :param change_id: It's the unique ChangeId of the change proposed by an agent for a particular code.
    :param final_score: The final score that you are giving to the updated code.
    """

    total_changes = suggested_changes.count_documents({"CodeId": code_id})
    total_executed_changes = suggested_changes.count_documents({"Executed": {"$exists": True}})
    if total_changes != total_executed_changes :
        return "There are still changes which are not executed it. Can't give final score now."

    else :
        if agent_name != 'Reviewer':
            return "!!! You are not authorised to give the final score !!!"
        else :
            suggested_changes.update_one({"CodeId": code_id, "ChangeId": change_id},
                                     {"$set": {"Final_Confidence_Score": final_score}})

            return "Final confidence score given successfully."

@tool('execute_changes', args_schema = ExecuteChanges)
def execute_changes(change_type : str, change_id : int, code_id : int):
    """
    Function through which they can check if there suggested change is approved or not. If approved they can now apply that change to the id.
    :param change_type: This is the type of change you want to enquire for to see if it's approved by other agents to be executed.
    :param code_id: It's the unique CodeId of the code you want to use any tools on.
    :param change_id: It's the unique ChangeId of the change proposed by an agent for a particular code.
    """

    from SyntaxFixer import syntax_agent
    from Optimizer import optimizer
    from DocAgent import doc_agent
    from Reviewer import review_agent

    opinion_count = agent_workspace.count_documents({"CodeId": code_id, "ChangeId": change_id})
    approved = agent_workspace.find({"CodeId": code_id, "ChangeId": change_id, "Approved": True})
    update_prompt = f"Executed the change with ChangeId: {change_id} and CodeId: {code_id}. Plz view the code again through view_code tool."
    approval_count = agent_workspace.count_documents({"CodeId": code_id, "ChangeId": change_id, "Approved": True})
    if opinion_count == approval_count:
        agg_score = 0
        for k in approved:
            agg_score += k["ConfidenceScore"]
        if agg_score >= 80:
            prompt = """Your proposed changes have been approved, now you can make changes to the code based on the proposed change and then return the changed code."""
            if change_type == 'SyntaxFix':
                updated_code = syntax_agent.run(prompt)
                agent_workspace.delete_many({"CodeId": code_id, "ChangeId": change_id})
                suggested_changes.update_one({"CodeId": code_id, "ChangeId": change_id},
                                             {"$set": {"Executed": True}})
                code_base.update_one({"CodeId": code_id},
                                     {"$set": {"Code": updated_code}})
                optimizer.run(update_prompt)
                review_agent.run(update_prompt)
                doc_agent.run(update_prompt)
            elif change_type == 'Optimization' :
                updated_code = optimizer.run(prompt)
                agent_workspace.delete_many({"CodeId": code_id, "ChangeId": change_id})
                suggested_changes.update_one({"CodeId": code_id, "ChangeId": change_id},
                                             {"$set": {"Executed": True}})
                code_base.update_one({"CodeId": code_id},
                                     {"$set": {"Code": updated_code}})
                optimizer.run(update_prompt)
                review_agent.run(update_prompt)
                doc_agent.run(update_prompt)
            else :
                updated_code = doc_agent.run(prompt)
                agent_workspace.delete_many({"CodeId": code_id, "ChangeId": change_id})
                suggested_changes.update_one({"CodeId": code_id, "ChangeId": change_id},
                                             {"$set": {"Executed": True}})
                code_base.update_one({"CodeId": code_id},
                                     {"$set": {"Code": updated_code}})
                optimizer.run(update_prompt)
                review_agent.run(update_prompt)
                doc_agent.run(update_prompt)
        else :
            return "Some agents don't think the change is necessary or that impactful. Plz try finding them (check_opinions) and interacting with them through interact_with_agent tool"
    else :
        not_approve_agent = agent_workspace.find({"CodeId": code_id, "ChangeId": change_id, "Approved": False})
        agents = []
        if not_approve_agent :
            for k in not_approve_agent:
                agents.append(k['SourceAgent'])

            return f"The agents who disapproved your change are : {agents}. Try contacting them through interact_with_agent tool for there opinion or check there reasoning using check_opinion tool"

tools = [
    StructuredTool.from_function(
        func=view_code,
        name="view_code",
        description="Retrieve the source code associated with a given CodeId for agents to analyze or modify.",
        args_schema=ViewCodeInput
    ),

    StructuredTool.from_function(
        func=fetch_recommended_changes,
        name="fetch_recommended_changes",
        description="Fetch all the suggested modifications for a specific ChangeId related to a CodeId.",
        args_schema=FetchRecommendedChangesInput
    ),

    StructuredTool.from_function(
        func=get_executed_changes,
        name="get_executed_changes",
        description="Get a list of all executed changes for a particular CodeId, including their final confidence scores.",
        args_schema=GetExecuteChangesInput
    ),

    StructuredTool.from_function(
        func=submit_score,
        name="submit_score",
        description="Submit a confidence score and reasoning for a proposed change. Access rules enforced by agent role and change type.",
        args_schema=SubmitScoreInput
    ),

    StructuredTool.from_function(
        func=propose_change,
        name="propose_change",
        description="Propose a new change (syntax fix, optimization, or documentation) for a code snippet. Agent type must align with change type.",
        args_schema=ProposeChange
    ),

    StructuredTool.from_function(
        func=check_opinion,
        name="check_opinion",
        description="Check other agents’ opinions and reasoning on a proposed change, optionally filtered by agent name.",
        args_schema=CheckOpinion
    ),

    StructuredTool.from_function(
        func=interact_with_agent,
        name="interact_with_agent",
        description="Initiate a message from one agent to another regarding a proposed change, enabling collaborative refinement or conflict resolution.",
        args_schema=InteractWithAgentInput
    ),

    StructuredTool.from_function(
        func=delete_proposal,
        name="delete_proposal",
        description="Allows agents to delete a proposed change they no longer believe is necessary or appropriate.",
        args_schema=DeleteProposal
    ),

    StructuredTool.from_function(
        func=give_final_confidence_score,
        name="give_final_confidence_score",
        description="Reviewer agent can give a final confidence score to a change once all suggested changes are executed.",
        args_schema=FinalReviewInput
    ),

    StructuredTool.from_function(
        func=execute_changes,
        name="execute_changes",
        description="If a change has full agent approval and high confidence, apply it to the code and notify all agents.",
        args_schema=ExecuteChanges
    )
]

# print([tool.name for tool in tools])

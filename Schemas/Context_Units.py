# Importing dependencies
from pymongo import MongoClient


# The database or our Context units will be having two collections inside it. i.e suggested_change and agent_workspace.

# The working or role of suggested_change collection:
# It will be used to keep a track of the changes suggested by various agents and what type of change is it. Each change will be having a changeId through which we can track
# all suggested changes just by a simple mongo query by finding the changes with same changeId.
# If the code provided is too large we can just simply break the code into different parts and then work on each part separately, but in this case we also need to add
# another field called CodeId which will be referring to the various parts of the code and help us track each part of code separately.
# Once a change is completed and reviewed by the reviewing agent its final confidence score is also added to the suggested changes

# The working or role of the agent_workspace collection:
# It will be used as a common workspace for all the agents, where all the agent will be reviewing the changes and also telling what their confidence scores are about
# their opinion and the change proposed. To distinguish between the agents and their opinions to gain insights about various agents we use SourceAgent field.
# To finalize a change if its confidence score exceeds a certain threshold the changes will be applied to the actual code. If the code is not approved by an agent its
# Confidence score would be taken as negative. After calculating the avg of the confidence scores, and comparing it to the threshold confidence score, a new field will
# be added to that particular ChangeId in the suggested_changes collection named Executed which will be a boolean. This will help us track every change individually.


# The various change types :
# 1. Documentation
# 2. SyntaxFix
# 3. Optimization



# Connecting to the server
client = MongoClient(host = "localhost", port = 27017)
db = client['Context_Units']

# Defining the schema for suggested_changes
validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["CodeId", "ChangeId", "ChangeType", "Content"],
        "properties": {
            "CodeId": {"bsonType": "int"},
            "ChangeId": {"bsonType": "int"},
            "ChangeType": {"bsonType": "string"},
            "Content": {"bsonType": "string"},
        },
    }
}

# Creating the suggested_changes collection
collections = db.list_collection_names()
if 'suggested_changes' not in collections:
    db.create_collection(name = 'suggested_changes',
                        validator = validator,
                        validationAction = 'error')
    print('Suggested_Changes Collection Created')
else :
    print('Suggested_Changes Collection Already Exists')

# Defining the schema for agent_workspace
validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["CodeId", "ChangeId", "SourceAgent", "Approved", "Reasoning", "ConfidenceScore"],
        "properties": {
            "CodeId": {"bsonType": "int"},
            "ChangeId": {"bsonType": "int"},
            "SourceAgent": {"bsonType": "string"},
            "Approved": {"bsonType": "bool"},
            "Reasoning": {"bsonType": "string"},
            "ConfidenceScore": {"bsonType": "double"}   # Used for float type in mongodb
        }
    }
}

if 'agent_workspace' not in collections :
    db.create_collection(name = "agent_workspace",
                        validator = validator,
                        validationAction = "error")

    print("Agent_Workspace Collection Created.")

else :
    print("Agent_Workspace Collection Already Exists.")


# Defining the schema for CodeBase

validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["CodeId", "Code"],
        "properties": {
            "CodeId": {"bsonType": "int"},
            "Code": {"bsonType": "string"},
        }
    }
}

if 'CodeBase' not in collections:
    db.create_collection(name = "CodeBase",
                         validator = validator,
                         validationAction = "error")

    print("Code_base Collection Created")

else :
    print("Code_Base Collection Already Exists")

# Defining the schema for Session

validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["CodeId", "SessionId", "OriginalCode", "UpdatedCode", "TotalChanges", "TaskType", "Language"],
        "properties": {
            "CodeId": {"bsonType": "int"},
            "SessionId": {"bsonType": "int"},
            "OriginalCode": {"bsonType": "string"},
            "UpdatedCode": {"bsonType": "string"},
            "TotalChanges": {"bsonType": "int"},
            "TaskType": {"bsonType": "string"},
            "Language": {"bsonType": "string"}
        }
    }
}

if 'Session' not in collections:
    db.create_collection(name = "Session",
                         validator = validator,
                         validationAction = "error")

    print("Session Collection Created")

else :
    print("Session Collection Already Exists")
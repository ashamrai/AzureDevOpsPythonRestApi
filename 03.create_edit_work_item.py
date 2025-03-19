#run pip install azure-devops

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import json

# Replace with your organization URL and PAT
organization_url = 'https://dev.azure.com/<ORG>'
personal_access_token = ''

team_project = '<Team Project Name>'
bug_work_item_type = 'Bug'

# Create a connection to the organization
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

# Get a client 
wit_client = connection.clients.get_work_item_tracking_client()

# Get a work item type definition
def get_work_item_type_fields(work_item_type):
    wi_type = wit_client.get_work_item_type(type=work_item_type, project=team_project)
    
    for witfield in wi_type.fields:      
        print(f'{witfield.reference_name} - {witfield.name}')  


#Create a work item
def create_work_item(wi_type, team_project, fields):

    document = []

    for field in fields:
        document.append({
            'op': 'add',
            'path': f'/fields/{field}',
            'from': None,
            'value': fields[field]
        })

    new_wi = wit_client.create_work_item(document, team_project, wi_type)   

    return new_wi

#Update a work item
def update_work_item(work_item_id, fields):

    document = []

    for field in fields:
        document.append({
            'op': 'add',
            'path': f'/fields/{field}',
            'from': None,
            'value': fields[field]
        })

    updated_wi = wit_client.update_work_item(id=work_item_id, document=document)

    return updated_wi

# Create a bug
def create_bug():      
    fields = {}

    fields['Title'] = 'New Bug'
    fields['Description'] = 'This is a new bug'
    fields['Repro Steps'] = '<ol><li>Run app</li><li>Crash</li></ol>'        
    fields['History'] = 'My comment'

    new_bug = create_work_item(bug_work_item_type, team_project, fields)

    return new_bug.id

# Update a bug
def update_bug(bug_id):
    fields = {}

    fields['Title'] = 'Updated Bug'
    fields['Description'] = 'This is an updated bug'
    fields['Repro Steps'] = '<ol><li>Run app</li><li>Crash</li><li>Updated step</li></ol>'        
    fields['History'] = 'My new comment'
    fields['Priority'] = '1'
    fields['State'] = 'Active'

    updated_bug = update_work_item(bug_id, fields)


#get_work_item_type_fields(bug_work_item_type)
new_bug_id = create_bug()
print(f'Bug ID - {new_bug_id}')

input("Press Enter to continue...")

update_bug(new_bug_id)
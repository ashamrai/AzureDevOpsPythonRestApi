#run pip install azure-devops

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import json

# Replace with your organization URL and PAT
organization_url = 'https://dev.azure.com/<ORG>'
personal_access_token = '<PAT>'

# Create a connection to the organization
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

# Get a client 
wit_client = connection.clients.get_work_item_tracking_client()

# Get a work item type definition
def get_work_item_type(wi):
    wi_type = wit_client.get_work_item_type(type=wi.fields['System.WorkItemType'], project=wi.fields['System.TeamProject'])
    
    return wi_type

# Show work item details
def show_work_item(wi):  
    wit = get_work_item_type(wi)

    print(f'Work Item Fields')

    for witfield in wit.fields:        
        refName = witfield.reference_name
        if (refName in wi.fields):
            print(f'{refName} - {wi.fields[refName]}')

    print(f'\n\nWork Item Relations')

    if (wi.relations is not None):
        for relation in wi.relations:
            print(f'{relation.attributes['name']} - {relation.url}')

#Get one work item
work_item = wit_client.get_work_item(id=1342, expand='all')

show_work_item(work_item)

#Get multiple work items
work_items = wit_client.get_work_items(ids=[1342, 1343], expand='all')

for work_item in work_items:
    show_work_item(work_item)

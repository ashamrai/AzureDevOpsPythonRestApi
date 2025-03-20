#run pip install azure-devops

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_1.work_item_tracking.models import Wiql
from azure.devops.v7_1.work_item_tracking.models import TeamContext

# Replace with your organization URL and PAT
organization_url = 'https://dev.azure.com/<ORG>'
personal_access_token = '<PAT>'

# Create a connection to the organization
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

team_project = '<Team Project Name>'
team_name = '<Team Name>'
template_name = '<Template Name>'

# Get clients
wit_client = connection.clients.get_work_item_tracking_client()
team_context = TeamContext(project=team_project, team=team_name)

# Get template
def get_template():
    
    templates = wit_client.get_templates(team_context)

    for template in templates:
        if (template.name == template_name):
            wi_template = wit_client.get_template(team_context, template.id)

            return wi_template
        
    return None

# Create work item by template
def create_work_item_by_template():
    
    wi_template = get_template()

    if wi_template is None:
        print(f'Template {template_name} not found')
        return

    document = []

    #add fields from template
    for field_name in wi_template.fields.keys():
        
        document.append({
            'op': 'add',
            'path': f'/fields/{field_name}',
            'from': None,
            'value': wi_template.fields[field_name]
        })

    #add title
    document.append({
        'op': 'add',
        'path': '/fields/System.Title',
        'from': None,
        'value': 'New Bug'
    })

    work_item = wit_client.create_work_item(document, team_project, wi_template.work_item_type_name)

    return work_item.id
    
wi_id = create_work_item_by_template()

print(f'Work item created with ID {wi_id}')
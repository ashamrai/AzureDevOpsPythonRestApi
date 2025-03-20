#run pip install azure-devops

from enum import Enum
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

# Relations enumeration
class WorkItemRelation(Enum):
    Related = "System.LinkTypes.Related"
    Child = "System.LinkTypes.Hierarchy-Forward"
    Parent = "System.LinkTypes.Hierarchy-Reverse"            
    Duplicate = "System.LinkTypes.Duplicate-Forward"
    DuplicateOfStr = "System.LinkTypes.Duplicate-Reverse"
    Successor = "System.LinkTypes.Dependency-Forward"
    Predecessor = "System.LinkTypes.Dependency-Reverse"
    TestedBy = "Microsoft.VSTS.Common.TestedBy-Forward"
    Tests = "Microsoft.VSTS.Common.TestedBy-Reverse"
    TestCase = "Microsoft.VSTS.TestCase.SharedStepReferencedBy-Forward"
    SharedSteps = "Microsoft.VSTS.TestCase.SharedStepReferencedBy-Reverse"
    Affects = "Microsoft.VSTS.Common.Affects-Forward"
    AffectedBy = "Microsoft.VSTS.Common.Affects-Reverse"            
    Attachment = "AttachedFile"
    HyperLink = "Hyperlink"
    ArtifactLink = "ArtifactLink"

# Replace with your organization URL and PAT
organization_url = 'https://dev.azure.com/<ORG>'
personal_access_token = '<PAT>'

# Create a connection to the organization
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

team_project = '<Team Project Name>'
work_item_id = -1 #<work_item_id>
parent_work_item_id = -1 #<parent_work_item_id>

# Get clients
wit_client = connection.clients.get_work_item_tracking_client()

# Duplicate work item
def duplicate_work_item(work_item_id):
    fields_to_copy =[ 'System.Title', 'System.Description', 'System.AssignedTo', 'System.Tags', 'System.AreaPath', 'System.IterationPath', ]

    work_item = wit_client.get_work_item(work_item_id)
    
    document = []
    
    #add fields from template
    for field_name in fields_to_copy:
        
        if (field_name not in work_item.fields):
            continue
        
        document.append({
            'op': 'add',
            'path': f'/fields/{field_name}',
            'from': None,
            'value': work_item.fields[field_name]
        })        

    document.append({
        'op': 'add',
        'path': '/relations/-',
        'value': {
            'rel': WorkItemRelation.Duplicate.value,
            'url': work_item.url,
            'attributes': {
                'comment': 'Work item duplicated'
            }            
        }
    })

    new_work_item = wit_client.create_work_item(project=team_project, document=document, type=work_item.fields['System.WorkItemType'])

    return new_work_item.id

# Add relation to work item
def add_relation_to_work_item(work_item_id, relation_type, target_work_item_id):
    document = []
    
    document.append({
        'op': 'add',
        'path': '/relations/-',
        'value': {
            'rel': relation_type.value,
            'url': f'{organization_url}/{team_project}/_apis/wit/workItems/{target_work_item_id}',
            'attributes': {
                'comment': 'Relation added to work item'
            }            
        }
    })

    wit_client.update_work_item(id=work_item_id, document=document)

#Remove relation from work item
def remove_relation_from_work_item(work_item_id, relation_type, target_work_item_id):
    work_item = wit_client.get_work_item(work_item_id, expand='relations')
    
    document = []
    
    index = 0

    for relation in work_item.relations:
        if (relation.rel == relation_type.value and relation.url.endswith(f'/_apis/wit/workItems/{target_work_item_id}')):
            document.append({
                'op': 'remove',
                'path': '/relations/' + str(index)
            })

            wit_client.update_work_item(id=work_item_id, document=document)

            break
        
        index += 1

# Duplicate work item
new_wi_id = duplicate_work_item(work_item_id)
print(f'New work item id: {new_wi_id}')

input("Press Enter to continue...")

#add parent relation
add_relation_to_work_item(new_wi_id, WorkItemRelation.Parent, parent_work_item_id)

input("Press Enter to continue...")

#remove relation
remove_relation_from_work_item(new_wi_id, WorkItemRelation.Duplicate, work_item_id)
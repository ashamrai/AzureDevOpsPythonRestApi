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
queryWiqlList = f'SELECT [System.Id] FROM WorkItems WHERE [System.TeamProject] = \'{team_project}\' and [System.WorkItemType] = \'User Story\' and [System.State] <> \'Removed\' and [System.State] <> \'Closed\''
queryWiqlTree  = f"""
SELECT [System.Id] FROM WorkItemLinks WHERE ([Source].[System.TeamProject] = '{team_project}' AND  [Source].[System.WorkItemType] IN ('Feature', 'User Story')  
AND  [Source].[System.State] IN ('New', 'Active', 'Resolved')) And ([System.Links.LinkType] = 'System.LinkTypes.Hierarchy-Forward') And 
([Target].[System.WorkItemType] IN ('User Story', 'Task') AND  [Target].[System.State] IN ('New', 'Active', 'Resolved')) ORDER BY [Microsoft.VSTS.Common.StackRank], [System.Id] mode(Recursive)
"""

# Get clients
wit_client = connection.clients.get_work_item_tracking_client()

# Get team queries fromroot folder
def show_team_queries():
    folders = wit_client.get_queries(project=team_project, expand='all')
    
    get_folder_conent(folders)
    
# Get query folder content
def get_folder_conent(folders):
    for folder in folders:
        if (folder.is_folder):
            print(f'Folder: {folder.path}')

            if (folder.has_children):
                item = wit_client.get_query(project=team_project, query=folder.path, expand='all', depth=1)                
                get_folder_conent(item.children)
        else:
            print(f'Query: {folder.name}')            

# Show a query results
def show_query_results(query_wiql):
    wiql = Wiql(query=query_wiql)
    team_context = TeamContext(project=team_project)
    query_result = wit_client.query_by_wiql(wiql, team_context)

    if (query_result.work_items is not None):
        show_query_flat_results(query_result)
    else:
        if (query_result.work_item_relations is not None):
            show_query_relation_results(query_result)
            

# Show results of a flat query
def show_query_flat_results(query_result):

    for work_item in query_result.work_items:
        work_item = wit_client.get_work_item(id=work_item.id)
        print(f'{work_item.id} - {work_item.fields["System.Title"]}')

# Show results of a query with relations
def show_query_relation_results(query_result):

    for work_item_relation in query_result.work_item_relations:
        if (work_item_relation.source is None):
            work_item = wit_client.get_work_item(id=work_item_relation.target.id)
            
            print(f'Top level: {work_item.id} - {work_item.fields["System.Title"]}')

        else:
            work_item_source = wit_client.get_work_item(id=work_item_relation.source.id)
            work_item_target = wit_client.get_work_item(id=work_item_relation.target.id)
            
            print(f'{work_item_relation.rel}: {work_item_source.id} -> {work_item_target.id} {work_item_target.fields["System.Title"]}')        

# Show results of a stored query
def show_stored_query_results(query_path):
    query = wit_client.get_query(project=team_project, query=query_path, expand='all')
    
    show_query_results(query.wiql)

show_team_queries()
input("Press Enter to continue...")

show_query_results(queryWiqlList)
input("Press Enter to continue...")

show_query_results(queryWiqlTree)
input("Press Enter to continue...")

show_stored_query_results('My Queries/Assigned to me')
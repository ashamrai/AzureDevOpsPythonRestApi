#run pip install azure-devops

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_1.work_item_tracking.models import WorkItemClassificationNode

# Replace with your organization URL and PAT
organization_url = 'https://dev.azure.com/<ORG>'
personal_access_token = '<PAT>'
team_project = '<Team Project Name>'

# Create a connection to the organization
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

# Get clients
wit_client = connection.clients.get_work_item_tracking_client()

# Create an iteration
def create_iteration(iteration_name, parent_iteration_path=None, start_date=None, finish_date=None):
    newNode = WorkItemClassificationNode(name=iteration_name, has_children=False, attributes={})
    
    if (start_date is not None):
        newNode.attributes['startDate'] = f"{start_date}T00:00:00Z"

    if (finish_date is not None):
        newNode.attributes['finishDate'] = f"{finish_date}T00:00:00Z"

    print(newNode.attributes)

    return wit_client.create_or_update_classification_node(project=team_project, structure_group='iterations', posted_node=newNode, path=parent_iteration_path)

# Create an area
def create_area(area_name, parent_area_path=None):
    newNode = WorkItemClassificationNode(name=area_name, has_children=False)
    
    return wit_client.create_or_update_classification_node(project=team_project, structure_group='areas', posted_node=newNode, path=parent_area_path)

# Print node information
def print_node_info(node):   
    
    node_string = '\\Iteration\\'

    if (node.structure_type == 'area'):
        node_string = '\\Area\\'

    node_local_path = node.path.replace(f'\\{team_project}{node_string}', '')

    print(f'{node.structure_type}: {node.name} - {node_local_path}')

    if (node.attributes is not None):
        print(f'Attributes: {node.attributes}')

#rename an area or iteration
def rename_node(node_path, new_name, structure_group):
    node = wit_client.get_classification_node(project=team_project, structure_group=structure_group, path=node_path)

    updated_node = WorkItemClassificationNode(name=new_name, structure_type=node.structure_type, has_children=node.has_children, attributes=node.attributes)
    
    return wit_client.update_classification_node(project=team_project, structure_group=structure_group, posted_node=updated_node, path=node_path)

#update iteration dates
def replan_iteration(iteration_path, start_date, finish_date):
    node = wit_client.get_classification_node(project=team_project, structure_group='iterations', path=iteration_path)

    updated_node = WorkItemClassificationNode(name=node.name, structure_type=node.structure_type, has_children=node.has_children, attributes=node.attributes)

    if (start_date is not None):
        updated_node.attributes['startDate'] = f"{start_date}T00:00:00Z"
    if (finish_date is not None):
        updated_node.attributes['finishDate'] = f"{finish_date}T00:00:00Z"

    return wit_client.update_classification_node(project=team_project, structure_group='iterations', posted_node=updated_node, path=iteration_path)

#delete an area or iteration
def delete_node(node_path, structure_group, new_node_path):
    new_node = wit_client.get_classification_node(project=team_project, structure_group=structure_group, path=new_node_path)
    wit_client.delete_classification_node(project=team_project, structure_group=structure_group, path=node_path, reclassify_id=new_node.id)

def manage_areas():
    new_node = create_area("Application")
    print_node_info(new_node)
    new_node = create_area("WinClient","Application")
    print_node_info(new_node)
    new_node = create_area("WebClient","Application")
    print_node_info(new_node)
    new_node = create_area("AppServer","Application")
    print_node_info(new_node)
    new_node = create_area("MobileServer","Application")
    print_node_info(new_node)

    updated_node = rename_node(f'Application\\MobileServer', 'DatabaseServer', 'areas')
    print_node_info(updated_node)
    delete_node('Application\\DatabaseServer', 'areas', 'Application')

def manage_iterations():
    new_node = create_iteration("R2")
    print_node_info(new_node)
    new_node = create_iteration("R2.1", "R2")
    print_node_info(new_node)
    new_node = create_iteration("Ver1", "R2\\R2.1", "2025-05-01", "2025-05-14")
    print_node_info(new_node)
    new_node = create_iteration("Ver2", "R2\\R2.1", "2025-05-15", "2025-05-28")
    print_node_info(new_node)

    updated_node = replan_iteration('R2\\R2.1\\Ver2', '2025-06-01', '2025-06-15')
    print_node_info(updated_node)

manage_areas()
manage_iterations()
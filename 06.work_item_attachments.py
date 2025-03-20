#run pip install azure-devops

import os
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

# Replace with your organization URL and PAT
organization_url = 'https://dev.azure.com/<ORG>'
personal_access_token = '<PAT>'

# Create a connection to the organization
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

team_project = '<Team Project Name>'
attachment_rel_str = 'AttachedFile'
work_item_id = -1 #<work_item_id>
file_path = '<your_file_path>'
download_folder = '<your_download_folder_path>'

# Get clients
wit_client = connection.clients.get_work_item_tracking_client()

# Upload attachment
def upload_attachment(file_path):
    file_name = os.path.basename(file_path)
    
    with open(file_path, 'rb') as file:
        attachment_ref = wit_client.create_attachment(
            project=team_project,
            upload_stream=file,
            file_name=file_name,
        )      

    return attachment_ref.url  

# Add attachment to work item
def work_item_add_attachment(work_item_id, file_path):
    
    attachment_url = upload_attachment(file_path)

    print(f'Attachment URL: {attachment_url }')

    document = []

    document.append({
        'op': 'add',
        'path': '/relations/-',
        'value': {
            'rel': attachment_rel_str,
            'url': attachment_url,
            'attributes': {
                'comment': 'Attachment added to work item'
            }
        }
    })

    wit_client.update_work_item(id=work_item_id, document=document)

# Download attachments from work item
def work_item_download_attachments(work_item_id, download_folder):
    
    work_item = wit_client.get_work_item(work_item_id, team_project, expand='relations')
    
    # Check all relations with type 'AttachedFile'
    for relation in work_item.relations:
        if relation.rel == attachment_rel_str:
            print(f'Attachment URL: {relation}')
            attachment_name = os.path.basename(relation.attributes['name'])
            attachment_path = os.path.join(download_folder, attachment_name)
            
            with open(attachment_path, 'wb') as file:
                rels = relation.url.split('/')
                attachment_id = rels[len(rels)-1]
                attachment_stream = wit_client.get_attachment_content(attachment_id, team_project, download=True)
                #to fownload zip, use wit_client.get_attachment_zip
                for chunk in attachment_stream:                    
                    file.write(chunk)

            print(f'Attachment downloaded: {attachment_path}')
    
work_item_add_attachment(work_item_id, file_path)

input("Press Enter to continue...")

work_item_download_attachments(work_item_id, download_folder)
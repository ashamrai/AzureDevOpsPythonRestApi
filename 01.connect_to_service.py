#run pip install azure-devops

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

# Replace with your organization URL and PAT
organization_url = 'https://dev.azure.com/<ORG>'
personal_access_token = '<PAT>'

# Create a connection to the organization
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

# Get clients
wit_client = connection.clients.get_work_item_tracking_client()
buil_client = connection.clients.get_build_client()
core_client = connection.clients.get_core_client()
git_client = connection.clients.get_git_client()
test_client = connection.clients.get_test_client()
tfvc_client = connection.clients.get_tfvc_client()
release_client = connection.clients.get_release_client()

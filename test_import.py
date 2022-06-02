from calendar import prmonth
from email import header
import re
import requests
import os
import yaml
import argparse

# os.environ['CLIENT_ID'] = "3361f144-14f4-4285-a820-78947173ca93"
# os.environ['CLIENT_SECRET'] = "BIY8Q~ly2WTXxqP54gMeGcYaTbARKhsEL0..zaTx"

os.environ['CLIENT_ID'] = "d5513558-feb4-4ff4-b0a5-788af7708062"
os.environ['CLIENT_SECRET'] = "iZJ8Q~wyhXPz~lP2jvk7iI7tOCNlXgLAEefgdaq1"

deploy_config_location = ".github/config/deploy_config.yaml"
with open(deploy_config_location, 'r') as file:
    config = yaml.safe_load(file)

def get_access_token():
    """
    This function takes in client id, client secrets and tenant id stored in the config file and returns an authentication token that can be used to call the Power BI Rest API.
    Returns
    -------
    access_token : str
        Authentication token to use when calling the Power BI Rest API.
    """
    tenant_id = config["spn_credentials"]["tenant_id"]

    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"

    payload = {
        'grant_type': 'client_credentials',
        # 'scope': 'oauth',
        'scope': 'https://analysis.windows.net/powerbi/api/.default',
        'resource': 'https://analysis.windows.net/powerbi/api',
        'client_id': os.environ['CLIENT_ID'],
        'client_secret': os.environ['CLIENT_SECRET'],
        'response_mode': 'query'}

    response = requests.request("POST", url, data=payload)
    access_token = f"Bearer {response.json().get('access_token')}"

    return access_token



def get_pbix_deploy_options():
    """
    This function takes in deploy options: pbix_name_conflict, override_model_name, override_report_label stored in the config file and returns a string that can appended to the rest api end point.
    Returns
    -------
    deploy_options : str
        Deploy options to use when calling the Power BI Rest API.
    """
    pbix_name_conflict = config["pbix_deploy_options"]["pbix_name_conflict"]
    override_model_name = config["pbix_deploy_options"]["override_model_name"]
    override_report_label = config["pbix_deploy_options"]["override_report_label"]

    if pbix_name_conflict in ["Overwrite", "Ignore", "Abort", "CreateOrOverwrite", "GenerateUniqueName"]:
        name_conflict_str = f"nameConflict={pbix_name_conflict}"
    else:
        name_conflict_str = "nameConflict=Ignore"

    if override_model_name in [True, False]:
        override_model_name_str = f"overrideModelLabel={override_model_name}"
    else:
        override_model_name_str = "overrideModelLabel=True"

    if override_report_label in [True, False]:
        override_report_label_str = f"overrideReportLabel={override_report_label}"
    else:
        override_report_label_str = "overrideReportLabel=True"

    deploy_options = "&" + name_conflict_str + "&" + \
        override_model_name_str + "&" + override_report_label_str
    return deploy_options

access_token = get_access_token()
# print(access_token)
if config["deploy_options"]["max_file_size_supported_in_mb"] < 1024:
    max_file_size_supported_in_mb = config["deploy_options"]["max_file_size_supported_in_mb"]
else:
    max_file_size_supported_in_mb = 1024

parser = argparse.ArgumentParser(description='Personal information')
parser.add_argument('--files', dest='files', type=str,
                     help='List of all file names that need to be uploaded to the Power BI Service')
parser.add_argument('--token', dest='token', type=str,
                     help='List of all file names that need to be uploaded to the Power BI Service')
args = parser.parse_args()

print(args.files)
print(args.token)

# file_name_array = args.files.split(",")

# for file_name in file_name_array:
#     file_extension = os.path.splitext(file_name)[1].lower()
#     file_name_without_extension = os.path.splitext(file_name)[0]
#     file_location = os.getcwd() + "/" + file_name

#     if os.path.getsize(file_location) / (1024 * 1024) < max_file_size_supported_in_mb and file_extension in [".pbix", ".rdl"]:
#         open_file = open(file_location, "rb")
#         workspace_id = config["deploy_location"]["workspace_id"]

#         headers = {'Authorization': access_token}
#         file = {'file': open_file}

#         if file_extension == ".pbix":
#             url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/imports?datasetDisplayName={file_name_without_extension}" + \
#             get_pbix_deploy_options()
#         elif file_extension == ".rdl":
#             url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/imports?datasetDisplayName={file_name_without_extension}" + \
#             get_rdl_deploy_options()

#         # response = requests.request("POST", url, headers=headers, files=file)
#         # if response.status_code in [200, 202]:
#         #     import_id = response.json().get("id")
#         #     print("Load Succeeded, Import Id:" + import_id)
#         # else:
#         #     print(f"ERROR: {response.status_code}: {response.content}\nURL: {response.url}")

#     elif not file_extension in [".pbix", ".rdl"]:
#         print("File type not supported")
#     else:
#         print("File Size over 1024 MB")

headers = {'Authorization': args.token}
# print(os.environ['token'])
pipeline_name = "TitanicPipeline"
dev_workspace_name = "TitanicWS[Dev]"
test_workspace_name = "TitanicWS[Test]"
prod_workspace_name = "TitanicWS[Prod]"


""" get workspaces """
url = "https://api.powerbi.com/v1.0/myorg/groups"
response = requests.request("GET", url=url, headers=headers)
print(response.json())

dev_workspace_id = None
test_workspace_id = None
prod_workspace_id = None
for resp in response.json().get("value"):
    if resp.get("name") == dev_workspace_name:
        dev_workspace_id = resp.get("id")
    if resp.get("name") == test_workspace_name:
        test_workspace_id = resp.get("id")
    if resp.get("name") == prod_workspace_name:
        prod_workspace_id = resp.get("id")

workspace_ids = [dev_workspace_id, test_workspace_id, prod_workspace_id]
# workspace_ids = [dev_workspace_id]

""" upload files to workspace """
file_name = "/titanic_analysis.pbix"
file_location = os.getcwd() + file_name
file_extension = os.path.splitext(file_name)[1].lower()
file_name_without_extension = os.path.splitext(file_name)[0]

for workspace_id in workspace_ids:
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/imports?datasetDisplayName={file_name_without_extension}" + \
            get_pbix_deploy_options()


    if os.path.getsize(file_location) / (1024 * 1024) < max_file_size_supported_in_mb and file_extension in [".pbix", ".rdl"]:
        open_file = open(file_location, "rb")
    file = {'file': open_file}

    response = requests.request("POST", url=url, headers=headers, files=file)
    print(response.json())


""" get pipeline """
url = "https://api.powerbi.com/v1.0/myorg/pipelines"
response = requests.request("GET", url=url, headers=headers)
pipeline_id = None
for resp in response.json().get("value"):
    if resp.get("displayName") == pipeline_name:
        pipeline_id = resp.get("id")
# print(response.json())

""" assign workspace to pipeline """
for idx, workspace_id in enumerate(workspace_ids):
    url = f"https://api.powerbi.com/v1.0/myorg/pipelines/{pipeline_id}/stages/{idx}/assignWorkspace"
    response = requests.request("POST", url, headers=headers, data={
        "workspaceId": workspace_id
    })
    # print(response)

""" deploy pipeline stages """
url = f"https://api.powerbi.com/v1.0/myorg/pipelines/{pipeline_id}/deployAll"
response = requests.request("POST", url, headers=headers, data={
  "sourceStageOrder": 0,
  "options": {
    "allowOverwriteArtifact": True,
    "allowCreateArtifact": True,
  }
})

print(response)
print(response.content)
print(url)


url = "https://api.powerbi.com/v1.0/myorg/capacities"
# url = f"https://api.powerbi.com/v1.0/myorg/pipelines/{pipeline_id}/users"
# response = requests.request("POST", url, headers=headers, data={
#     "identifier": "154aef10-47b8-48c4-ab97-f0bf9d5f8fcf",
#     "accessRight": "Admin",
#     "principalType": "Group"
# })

# print(response.json())

# url = "https://api.powerbi.com/v1.0/myorg/pipelines"
# response = requests.request("POST", url, headers=headers, data={
#   "displayName": "The Best Pipeline",
#   "description": "My deployment pipeline description"
# })

# print(response)
# print()

# url = "https://api.powerbi.com/v1.0/myorg/pipelines"
# response = requests.request("GET", url=url, headers=headers)
# # print(dict(response.json()))
# print()

# url = "https://api.powerbi.com/v1.0/myorg/groups"
# response = requests.request("GET", url=url, headers=headers)
# print(response.json())
# print()

# url = "https://api.powerbi.com/v1.0/myorg/admin/pipelines/23dcc366-beff-431d-ad77-a887ef588498/users"
# response = requests.request("GET", url=url, headers=headers)
# print(response.content)
# print()

# url = "https://api.powerbi.com/v1.0/myorg/admin/pipelines/6bd55dc6-1a22-41f9-8d9c-1989a6f15dcc/users"
# response = requests.request("POST", url, headers=headers, data={
#   "identifier": "chang.tan@vnext.com.au",
#   "accessRight": "Admin",
#   "principalType": "User"
# })
# print(response)
# print(response.content)
# print(url)
# print()

# url = f"https://api.powerbi.com/v1.0/myorg/pipelines/23dcc366-beff-431d-ad77-a887ef588498/stages/0/assignWorkspace"
# response = requests.request("POST", url, headers=headers, data={
#   "workspaceId": "a9c76981-7ff5-4fda-9d9d-22741c775d50"
# })

# print(response)
# # print(response.content)
# print(url)

# url = "https://api.powerbi.com/v1.0/myorg/pipelines/23dcc366-beff-431d-ad77-a887ef588498/deploy"
# url = f"https://api.powerbi.com/v1.0/myorg/pipelines/{pipeline_id}/deployAll"
# response = requests.request("POST", url, headers=headers, data={
#   "sourceStageOrder": 0,
#   "options": {
#     "allowOverwriteArtifact": False,
#     "allowCreateArtifact": False
#   }
# })

# print(response)
# print(response.content)
# print(url)

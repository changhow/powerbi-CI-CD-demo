import argparse
import requests

parser = argparse.ArgumentParser(description='Personal information')
parser.add_argument('--accessToken', dest='access_token', type=str)
parser.add_argument('--workspaceName', dest='workspace_name', type=str)
args = parser.parse_args()

access_token = args.access_token
workspace_name = args.workspace_name

headers = {'Authorization': access_token}

""" get workspaces """
url = "https://api.powerbi.com/v1.0/myorg/groups"
response = requests.request("GET", url=url, headers=headers)

workspace_exist = False
for resp in response.json().get("value"):
    if resp.get("name") == workspace_name:
        print(f"Workspace name {workspace_name} already exists!")
        workspace_exist = True
        break

if not workspace_exist:
    url = "https://api.powerbi.com/v1.0/myorg/groups?workspaceV2=True"
    body = {
       "name": workspace_name
    }

    response = requests.request("POST", url=url, headers=headers, data=body)
    if response.status_code in [200, 202]:
        print(f"Success! Response code: {response.status_code}\n Response: {response.content}")
    else:
        print(f"Something wrong! Response code: {response.status_code}\n Response: {response.content}")


import argparse
import requests

parser = argparse.ArgumentParser(description='Personal information')
parser.add_argument('--accessToken', dest='access_token', type=str)
parser.add_argument('--workspaceName', dest='workspace_name', type=str)
parser.add_argument('--pipelineName', dest='pipeline_name', type=str)
parser.add_argument('--stageOrder', dest='stage_order', type=int)
args = parser.parse_args()

access_token = args.access_token
workspace_name = args.workspace_name
pipeline_name = args.pipeline_name
stage_order = args.stage_order

headers = {'Authorization': access_token}

""" get premium capacity id """
capacity_id = None
url = "https://api.powerbi.com/v1.0/myorg/capacities"
response = requests.request("GET", url=url, headers=headers)
for resp in response.json().get("value"):
    if resp.get("displayName") == "Premium Per User - Reserved":
        capacity_id = resp.get("id")
        break

if capacity_id is None:
    raise Exception(f"Premium capacity not found! Please check with your organization admin.")

""" get workspaces """
url = "https://api.powerbi.com/v1.0/myorg/groups"
response = requests.request("GET", url=url, headers=headers)
workspace_id = None
for resp in response.json().get("value"):
    if resp.get("name") == workspace_name: 
        workspace_id = resp.get("id")
        break

if workspace_id is None:
    raise Exception(f"Workspace {workspace_name} not found! Please create it.")

""" assign to premium per user capacity """
url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/AssignToCapacity"
body = {
    "capacityId": capacity_id
}
response = requests.request("POST", url, headers=headers, data=body)

""" get pipeline """
url = "https://api.powerbi.com/v1.0/myorg/pipelines"
response = requests.request("GET", url=url, headers=headers)
pipeline_id = None
for resp in response.json().get("value"):
    if resp.get("displayName") == pipeline_name:
        pipeline_id = resp.get("id")
        break

if pipeline_id is None:
    raise Exception(f"Pipeline {pipeline_name} not found! Please create it.")

""" Assign workspaces with pipeline """
url = f"https://api.powerbi.com/v1.0/myorg/pipelines/{pipeline_id}/stages/{stage_order}/assignWorkspace"
body = {
    "workspaceId": workspace_id
}
response = requests.request("POST", url, headers=headers, data=body)

if response.status_code in [200, 201, 202]:
    print(f"Success! Response code: {response.status_code} \nResponse: {response.content} \n")
else:
    print(f"Something wrong! Response code: {response.status_code} \nResponse: {response.content} \n")
    # raise Exception(response.content)


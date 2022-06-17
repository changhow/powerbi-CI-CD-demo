import argparse
import requests
import os
import string

parser = argparse.ArgumentParser(description='Personal information')
parser.add_argument('--accessToken', dest='access_token', type=str)
parser.add_argument('--pipelineName', dest='pipeline_name', type=str)
parser.add_argument('--workspaceName', dest='workspace_name', type=str)
parser.add_argument('--files', dest='files', type=str)
args = parser.parse_args()

access_token = args.access_token
workspace_name = args.workspace_name
pipeline_name = args.pipeline_name
files = args.files

headers = {'Authorization': access_token}

file_name_array = args.files.split(",")


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


pipeline_stages = ['[DEV]', '[TEST]', '[PROD]']

for file_name in file_name_array:
    file_location = os.path.join(os.getcwd(), file_name)
    file_extension = os.path.splitext(file_name)[1].lower()
    file_name_without_extension = os.path.splitext(file_name)[0]

    if file_extension in ['.pbix', '.csv', '.xlsx']:
        
        for stage_order, stage in enumerate(pipeline_stages):
            open_file = open(file_location, "rb")
            file = {'file': open_file}

            """ get workspace id """
            url = "https://api.powerbi.com/v1.0/myorg/groups"
            response = requests.request("GET", url=url, headers=headers)

            for resp in response.json().get("value"):
                if resp.get("name") == workspace_name + stage:
                    workspace_id = resp.get("id")
            
            """ get dataset name """
            url = f"https://api.powerbi.com/v1.0/myorg//groups/{workspace_id}/datasets"
            response = requests.request("GET", url=url, headers=headers)

            url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/imports?datasetDisplayName={file_name_without_extension}"

            for resp in response.json().get("value"):
                print(resp.get("name"), file_name_without_extension)
                if resp.get("name").strip(string.punctuation) == file_name_without_extension.strip(string.punctuation):
                    # upload to Dev and all empty workspaces as initialization
                    if stage == pipeline_stages[0]:
                        name_conflict_status = "Overwrite"
                    else:
                        name_conflict_status = "Abort"

                    url += "&nameConflict=" + name_conflict_status
                    print(f"Existing dataset name found in {stage}! {name_conflict_status} upload files")
                    break

            response = requests.request("POST", url=url, headers=headers, files=file)
            if response.status_code in [200, 201, 202]:
                print(f"Success! Response code: {response.status_code} \nResponse: {response.content} \n")
            else:
                print(f"Something wrong happened when uploading {file_location} to {workspace_name}{stage} ! Response code: {response.status_code} \nResponse: {response.content} \n")
        
            """ unassign and assign workspace to stages again to sync up """
            url = f"https://api.powerbi.com/v1.0/myorg/pipelines/{pipeline_id}/stages/{stage_order}/unassignWorkspace"
            response = requests.request("POST", url=url, headers=headers)
            """ Assign workspaces with pipeline """
            url = f"https://api.powerbi.com/v1.0/myorg/pipelines/{pipeline_id}/stages/{stage_order}/assignWorkspace"
            body = {
                "workspaceId": workspace_id
            }
            response = requests.request("POST", url, headers=headers, data=body)


    else:
        print(f"{file_name} with extension {file_extension} not supported")



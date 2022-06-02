import argparse
import requests
import os

parser = argparse.ArgumentParser(description='Personal information')
parser.add_argument('--accessToken', dest='access_token', type=str)
parser.add_argument('--pipelineName', dest='pipeline_name', type=str)
parser.add_argument('--workspaceName', dest='workspace_name', type=str)
parser.add_argument('--files', dest='files', type=str)
args = parser.parse_args()

access_token = args.access_token
workspace_name = args.workspace_name
files = args.files

headers = {'Authorization': access_token}

file_name_array = args.files.split(",")
for file_name in file_name_array:
    file_location = os.path.join(os.getcwd(), file_name)
    file_extension = os.path.splitext(file_name)[1].lower()
    file_name_without_extension = os.path.splitext(file_name)[0]
    if file_extension in ['.pbix']:

        """ get workspace id """
        url = "https://api.powerbi.com/v1.0/myorg/groups"
        response = requests.request("GET", url=url, headers=headers)

        for resp in response.json().get("value"):
            if resp.get("name") == workspace_name:
                workspace_id = resp.get("id")

        url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/imports?datasetDisplayName={file_name_without_extension}"

        open_file = open(file_location, "rb")
        file = {'file': open_file}

        response = requests.request("POST", url=url, headers=headers, files=file)
        if response.status_code in [200, 201, 202]:
            print(f"Success! Response code: {response.status_code} \nResponse: {response.content} \n")
        else:
            print(f"Something wrong! Response code: {response.status_code} \nResponse: {response.content} \n")
    else:
        print(f"{file_name} with extension {file_extension} not supported")



import argparse
import requests

parser = argparse.ArgumentParser(description='Personal information')
parser.add_argument('--accessToken', dest='access_token', type=str)
parser.add_argument('--pipelineName', dest='pipeline_name', type=str)
args = parser.parse_args()

access_token = args.access_token
pipeline_name = args.pipeline_name

headers = {'Authorization': access_token}

""" get pipeline """
url = "https://api.powerbi.com/v1.0/myorg/pipelines"
response = requests.request("GET", url=url, headers=headers)

pipeline_exist = False
for resp in response.json().get("value"):
    if resp.get("displayName") == pipeline_name:
        print(f"Pipeline name {pipeline_name} already exists! Goodbye!")
        pipeline_exist = True
        break

if not pipeline_exist:
    url = "https://api.powerbi.com/v1.0/myorg/pipelines"
    body = {
        "displayName": pipeline_name,
        "description": "My deployment pipeline description"
    }
    response = requests.request("POST", url=url, headers=headers, data=body)
    if response.status_code in [200, 201, 202]:
        print(f"Success! Response code: {response.status_code} \nResponse: {response.content} \n")
    else:
        print(f"Something wrong! Response code: {response.status_code} \nResponse: {response.content} \n")


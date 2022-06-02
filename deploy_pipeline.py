import argparse
import requests

parser = argparse.ArgumentParser(description='Personal information')
parser.add_argument('--accessToken', dest='access_token', type=str)
parser.add_argument('--pipelineName', dest='pipeline_name', type=str)
parser.add_argument('--stageOrder', dest='stage_order', type=int)
args = parser.parse_args()

access_token = args.access_token
pipeline_name = args.pipeline_name
stage_order = args.stage_order

headers = {'Authorization': access_token}

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
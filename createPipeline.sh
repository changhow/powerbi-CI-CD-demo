# Variables 
# workspace to be created manually under premium tier
$workspaceName = "TitanicWS[Dev]"

$pipelineName = "TitanicPipeline"
$pipelineDescription = "This is a new pipeline"

# Create Pipeline
$url = "pipelines"
$body = @{
    "displayName"= $pipelineName
    "description"= $pipelineDescription
} | ConvertTo-Json


$deployResult = Invoke-PowerBIRestMethod -Url $url  -Method Post -Body $body | ConvertFrom-Json

# Need to create one workspace with data uploaded manually
# # Create workspace
# $url = "groups?workspaceV2=True"
# $body = @{
#     "name" = $workspaceName
# } | ConvertTo-Json

# $deployResult = Invoke-PowerBIRestMethod -Url $url  -Method Post -Body $body | ConvertFrom-Json

# Assign workspace
$pipelines = (Invoke-PowerBIRestMethod -Url "pipelines"  -Method Get | ConvertFrom-Json).value
$pipeline = $pipelines | Where-Object {$_.DisplayName -eq $pipelineName}

$workspaces = (Invoke-PowerBIRestMethod -Url "groups"  -Method Get | ConvertFrom-Json).value
$workspace = $workspaces | Where-Object {$_.name -eq $workspaceName}

$stageOrder = 0

$body = @{
    "workspaceId" = $workspace.id
} | ConvertTo-Json

$url = "pipelines/{0}/stages/{1}/assignWorkspace" -f $pipeline.id, $stageOrder
$deployResult = Invoke-PowerBIRestMethod -Url $url  -Method Post -Body $body | ConvertFrom-Json

# deploy pipeline
$pipelines = (Invoke-PowerBIRestMethod -Url "pipelines"  -Method Get | ConvertFrom-Json).value
$pipeline = $pipelines | Where-Object {$_.DisplayName -eq $pipelineName}

$body = @{
    "sourceStageOrder" = 0
    "options"= @{
        "allowOverwriteArtifact" = $TRUE
        "allowCreateArtifact" = $TRUE
    }
} | ConvertTo-Json

$url = "pipelines/{0}/deployAll" -f $pipeline.id
$deployResult = Invoke-PowerBIRestMethod -Url $url  -Method Post -Body $body | ConvertFrom-Json

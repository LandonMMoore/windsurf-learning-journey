# This script deploys the Service Bus resources

[CmdletBinding()]
param (
    [Parameter(Mandatory)][string] $resourceGroupName,
    [Parameter(Mandatory)][string] $ServiceBusNamespace,
    [string] $Prefix
)

$ErrorActionPreference = "Stop"

Write-Host "Discover bicep files ..."

if (!$Prefix) {
    Write-Host "Filter all bicep files"
    $files = Get-ChildItem -Path $PSScriptRoot/*.bicep
} else {
    Write-Host "Filter all prefixed bicep files"
    $files = Get-ChildItem -Path $PSScriptRoot/wo-*.bicep
}

Write-Host "Found $($files.Count)"
if ($files.Count -eq 0) {
    exit 0
}

Write-Host "Starting to deploy ..."
Write-Host (Get-Date)

foreach ($f in $files) {
    Write-Host $f.Name

    if (!$Prefix) {
        $null = az deployment group create --resource-group $resourceGroupName --name $f.Name `
        --template-file $f.FullName --parameters namespaces_sb_govt_assist_name=$ServiceBusNamespace

    } else {
        $null = az deployment group create --resource-group $resourceGroupName --name $f.Name `
        --template-file $f.FullName --parameters namespaces_sb_govt_assist_name=$ServiceBusNamespace prefix=$Prefix

    }

    if ($LASTEXITCODE -ne 0) {
        throw "External command returned an error!"
    }    
}

Write-Host (Get-Date)
Write-Host "done!"

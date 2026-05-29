param(
    [string]$DestinationRoot = "$env:USERPROFILE\.codex\skills",
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$source = Join-Path $repoRoot 'skills\win11-storage-governance'
$destination = Join-Path $DestinationRoot 'win11-storage-governance'

if (-not (Test-Path -LiteralPath $source)) {
    throw "Source skill not found: $source"
}

New-Item -ItemType Directory -Force -Path $DestinationRoot | Out-Null

if (Test-Path -LiteralPath $destination) {
    if (-not $Force) {
        throw "Destination already exists: $destination. Re-run with -Force to overwrite."
    }
    Remove-Item -LiteralPath $destination -Recurse -Force
}

Copy-Item -LiteralPath $source -Destination $destination -Recurse

Write-Host "Installed win11-storage-governance to $destination"

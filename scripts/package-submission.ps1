$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$stage = Join-Path (Get-Location) ('.tools/submission-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $stage -Force | Out-Null
$tracked = git ls-files
foreach ($file in $tracked) {
    $destination = Join-Path $stage $file
    New-Item -ItemType Directory -Force -Path (Split-Path $destination -Parent) | Out-Null
    Copy-Item -LiteralPath $file -Destination $destination
}
foreach ($folder in 'screenshots','evidence') {
    if (Test-Path $folder) { Copy-Item -LiteralPath $folder -Destination $stage -Recurse }
}
if (Test-Path 'BAO_CAO_LAB7.txt') { Copy-Item 'BAO_CAO_LAB7.txt' $stage }
New-Item -ItemType Directory -Path (Join-Path $stage 'artifacts') | Out-Null
Copy-Item 'sample-java-app/target/*.jar' (Join-Path $stage 'artifacts')
$zip = Join-Path (Get-Location) 'Lab7_NongVanNguyen_DTC235180138.zip'
Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $zip -Force
Write-Output $zip

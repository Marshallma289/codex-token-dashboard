[CmdletBinding()]
param(
    [string]$OutputDirectory = (Join-Path $PSScriptRoot 'release'),
    [string]$Python = 'python'
)
$ErrorActionPreference = 'Stop'
$destination = [System.IO.Path]::GetFullPath($OutputDirectory)
$version = (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'VERSION') -Raw).Trim()
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$buildRoot = Join-Path $destination "build-$version-$stamp"
$portable = Join-Path $buildRoot 'dist\CodexTokenDesktop'
New-Item -ItemType Directory -Force -Path $buildRoot | Out-Null
Push-Location $PSScriptRoot
try {
    & $Python -m unittest discover -s tests
    if ($LASTEXITCODE -ne 0) { throw 'Tests failed; build stopped.' }
    & node --check web/app.js
    if ($LASTEXITCODE -ne 0) { throw 'JavaScript validation failed; build stopped.' }
    & $Python -m PyInstaller --noconfirm --workpath (Join-Path $buildRoot 'work') --distpath (Join-Path $buildRoot 'dist') CodexTokenDesktop.spec
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed.' }
    foreach ($name in @('LICENSE', 'THIRD_PARTY_NOTICES.md', 'providers.json.example', 'VERSION', '便携版使用说明.txt', '启动 Codex Token 看板.cmd')) {
        Copy-Item -LiteralPath (Join-Path $PSScriptRoot $name) -Destination $portable
    }
    $manifest = [ordered]@{version=$version; built_at=(Get-Date).ToUniversalTime().ToString('o'); files=@()}
    $manifest.files = @(Get-ChildItem -LiteralPath $portable -Recurse -File | ForEach-Object {
        [ordered]@{path=$_.FullName.Substring($portable.Length+1); sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash}
    })
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $portable 'build-manifest.json') -Encoding utf8
    $archive = Join-Path $destination "CodexTokenDashboard-Windows-Portable-$version-$stamp.zip"
    Compress-Archive -LiteralPath $portable -DestinationPath $archive
    Write-Output $archive
} finally {
    Pop-Location
}

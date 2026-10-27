$ErrorActionPreference = 'Stop'
$checkoutRoot = 'C:\Users\sandh\OneDrive\Projects\indus_valley_script'
$archiveRoot = 'D:\projects\indus_valley_script\data\raw\2026-10-24-q1032-town-axis-register\endpoint-source-records'
$records = @()
foreach ($version in @('v1','v2','v3','v4')) {
    $source = [IO.Path]::GetFullPath((Join-Path $checkoutRoot "experiments\2026-10-24-q1032-town-axis-register\run-$version\sources.jsonl"))
    $target = [IO.Path]::GetFullPath((Join-Path $archiveRoot "run-$version-sources.jsonl"))
    if (-not $source.StartsWith($checkoutRoot + '\') -or -not $target.StartsWith($archiveRoot + '\')) { throw 'Unexpected preservation path' }
    if ((Get-Item -LiteralPath $source).LinkType) { throw 'Source already linked' }
    if (Test-Path -LiteralPath $target) { throw 'Preserve earlier archive' }
    New-Item -ItemType Directory -Path $archiveRoot -Force | Out-Null
    $before = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
    Copy-Item -LiteralPath $source -Destination $target
    if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $before) { throw 'Archive hash mismatch' }
    Remove-Item -LiteralPath $source
    New-Item -ItemType SymbolicLink -Path $source -Target $target | Out-Null
    $records += [PSCustomObject]@{version=$version; original_path=$source; archive_path=$target; sha256=$before.ToLower(); handling='local-only, ignored; frozen bytes preserved'}
}
$records | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $checkoutRoot 'experiments\2026-10-24-q1032-town-axis-register\source-export-preservation.json') -Encoding utf8
Write-Output 'Four complete source-use exports preserved on D: with matching hashes and compatibility links.'

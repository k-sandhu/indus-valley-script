param([Parameter(Mandatory=$true)][string]$Manifest)
$ErrorActionPreference = 'Stop'
$migration = Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json
$sourceRoot = [IO.Path]::GetFullPath($migration.source_root).TrimEnd('\')
$targetRoot = [IO.Path]::GetFullPath($migration.destination_root).TrimEnd('\')
if ($sourceRoot -ne 'C:\Users\sandh\OneDrive\Projects\indus_valley_script' -or $targetRoot -ne 'D:\projects\indus_valley_script') { throw 'Unexpected migration roots' }
function Checked-Path([string]$Root, [string]$Relative) {
    $candidate = [IO.Path]::GetFullPath((Join-Path $Root $Relative))
    if (-not $candidate.StartsWith($Root + '\', [StringComparison]::OrdinalIgnoreCase)) { throw "Path outside approved root: $candidate" }
    return $candidate
}
foreach ($relative in $migration.directories) {
    $source = Checked-Path $sourceRoot $relative
    $target = Checked-Path $targetRoot $relative
    New-Item -ItemType Directory -Path $target -Force | Out-Null
    & robocopy $source $target /E /COPY:DAT /DCOPY:DAT /XJ /R:1 /W:1 /MT:16 /NFL /NDL /NJH /NJS /NP
    if ($LASTEXITCODE -ge 8) { Write-Output "Copy reported inaccessible paths: $relative (robocopy $LASTEXITCODE); full manifest verification must pass" }
    Write-Output "Copied $relative"
}
foreach ($relative in $migration.individual_files) {
    $source = Checked-Path $sourceRoot $relative
    $target = Checked-Path $targetRoot $relative
    New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
    Copy-Item -LiteralPath $source -Destination $target
}
& python (Join-Path $sourceRoot 'tools\migrate_local_storage.py') verify --manifest $Manifest
if ($LASTEXITCODE -ne 0) { throw 'Destination verification failed; C: copies preserved' }
foreach ($relative in $migration.preserve_trees) {
    $source = Checked-Path $sourceRoot $relative
    $remnant = Checked-Path $sourceRoot ('data/storage-remnants-2026-10-24/' + $relative)
    New-Item -ItemType Directory -Path (Split-Path -Parent $remnant) -Force | Out-Null
    Move-Item -LiteralPath $source -Destination $remnant
    Write-Output "Preserved unreadable source tree: $relative"
}
foreach ($relative in $migration.directories) {
    $source = Checked-Path $sourceRoot $relative
    $target = Checked-Path $targetRoot $relative
    # Paths are checked immediately before recursive removal. Every byte has
    # already been checked against the preserved destination manifest.
    if ((Get-Item -LiteralPath $source).LinkType) { throw "Unexpected link: $source" }
    Remove-Item -LiteralPath $source -Recurse -Force -ErrorAction SilentlyContinue
    if (Test-Path -LiteralPath $source) {
        $remnant = Checked-Path $sourceRoot ($relative + '.migration-remnant-2026-10-24')
        if (Test-Path -LiteralPath $remnant) { throw "Remnant path already exists: $remnant" }
        Move-Item -LiteralPath $source -Destination $remnant
        Write-Output "Preserved inaccessible remnant: $remnant"
    }
    New-Item -ItemType Junction -Path $source -Target $target | Out-Null
    Write-Output "Relocated $relative"
}
foreach ($relative in $migration.individual_files) {
    $source = Checked-Path $sourceRoot $relative
    $target = Checked-Path $targetRoot $relative
    Remove-Item -LiteralPath $source -Force
    New-Item -ItemType SymbolicLink -Path $source -Target $target | Out-Null
}
Write-Output 'Storage relocation complete. Directory junctions and file links retain historical paths.'

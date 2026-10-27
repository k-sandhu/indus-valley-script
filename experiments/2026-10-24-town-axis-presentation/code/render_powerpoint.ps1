param(
    [Parameter(Mandatory = $true)][string]$PresentationPath,
    [Parameter(Mandatory = $true)][string]$RenderDirectory
)
$ErrorActionPreference = 'Stop'
$resolvedDeck = (Resolve-Path -LiteralPath $PresentationPath).Path
$intendedRoot = 'D:\projects\indus_valley_script\data\raw\2026-10-24-town-axis-presentation\'
$resolvedOutput = [IO.Path]::GetFullPath($RenderDirectory)
if (-not $resolvedDeck.StartsWith($intendedRoot, [StringComparison]::OrdinalIgnoreCase) -or -not $resolvedOutput.StartsWith($intendedRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Presentation and renders must stay in the named D: package'
}
if (Test-Path -LiteralPath $resolvedOutput) { throw 'A render directory already exists' }
New-Item -ItemType Directory -Path $resolvedOutput | Out-Null
$powerpoint = $null
$deck = $null
try {
    $powerpoint = New-Object -ComObject PowerPoint.Application
    $deck = $powerpoint.Presentations.Open($resolvedDeck, -1, 0, 0)
    if ($deck.Slides.Count -ne 14) { throw 'Slide count differs from the authored deck' }
    $deck.Export($resolvedOutput, 'PNG', 1280, 720)
    Write-Output ('PowerPoint exported {0} slides to {1}' -f $deck.Slides.Count, $resolvedOutput)
    $applicationVersion = $powerpoint.Version
    $testCopy = Join-Path $resolvedOutput 'editable-test-copy.pptx'
    $deck.SaveCopyAs($testCopy, 24)
    $deck.Close()
    [Runtime.InteropServices.Marshal]::ReleaseComObject($deck) | Out-Null
    $deck = $powerpoint.Presentations.Open($testCopy, 0, 0, 0)
    $samples = @()
    foreach ($slideNumber in @(2, 6, 9)) {
        $nativeChart = $null
        foreach ($shape in $deck.Slides.Item($slideNumber).Shapes) {
            if ($shape.HasChart -eq -1) { $nativeChart = $shape; break }
        }
        if ($null -eq $nativeChart) { throw ('Native chart missing on slide {0}' -f $slideNumber) }
        $nativeChart.Width = $nativeChart.Width + 8
        $samples += [PSCustomObject]@{ slide = $slideNumber; shapeId = $nativeChart.Id; widthPoints = $nativeChart.Width; series = $nativeChart.Chart.SeriesCollection().Count }
    }
    $deck.Save()
    $deck.Close()
    [Runtime.InteropServices.Marshal]::ReleaseComObject($deck) | Out-Null
    $deck = $powerpoint.Presentations.Open($testCopy, -1, 0, 0)
    foreach ($sample in $samples) {
        $reopenedChart = $null
        foreach ($shape in $deck.Slides.Item($sample.slide).Shapes) {
            if ($shape.Id -eq $sample.shapeId) { $reopenedChart = $shape; break }
        }
        if ($null -eq $reopenedChart -or [Math]::Abs($reopenedChart.Width - $sample.widthPoints) -gt 0.01) { throw 'Resized chart did not survive save and reopen' }
    }
    [PSCustomObject]@{ application = 'Microsoft PowerPoint'; version = $applicationVersion; exportedSlides = 14; sampleChartsResizedSavedReopened = $samples; finalFileChanged = $false } |
        ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $resolvedOutput 'native-review.json') -Encoding utf8
}
finally {
    if ($null -ne $deck) {
        $deck.Close()
        [Runtime.InteropServices.Marshal]::ReleaseComObject($deck) | Out-Null
    }
    if ($null -ne $powerpoint) {
        if ($powerpoint.Presentations.Count -eq 0) { $powerpoint.Quit() }
        [Runtime.InteropServices.Marshal]::ReleaseComObject($powerpoint) | Out-Null
    }
}

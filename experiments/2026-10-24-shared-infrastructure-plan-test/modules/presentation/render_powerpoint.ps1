param(
 [Parameter(Mandatory=$true)][string]$PresentationPath,
 [Parameter(Mandatory=$true)][string]$RenderDirectory
)
$ErrorActionPreference='Stop'
$resolvedDeck=(Resolve-Path -LiteralPath $PresentationPath).Path
$resolvedOutput=[IO.Path]::GetFullPath($RenderDirectory)
$allowedRoot='D:\projects\indus_valley_script\data\raw\2026-10-24-shared-infrastructure-plan-test\presentation\'
if(-not $resolvedDeck.StartsWith($allowedRoot,[StringComparison]::OrdinalIgnoreCase) -or -not $resolvedOutput.StartsWith($allowedRoot,[StringComparison]::OrdinalIgnoreCase)){throw 'Deck and renders must remain in the named D: presentation directory'}
if(Test-Path -LiteralPath $resolvedOutput){throw 'Render directory already exists'}
New-Item -ItemType Directory -Path $resolvedOutput|Out-Null
$application=$null
$deck=$null
try{
 $application=New-Object -ComObject PowerPoint.Application
 $deck=$application.Presentations.Open($resolvedDeck,-1,0,0)
 if($deck.Slides.Count -ne 26){throw 'Unexpected slide count'}
 $deck.Export($resolvedOutput,'PNG',1600,900)
 $testCopy=Join-Path $resolvedOutput 'editable-test-copy.pptx'
 $deck.SaveCopyAs($testCopy,24)
 $deck.Close()
 [Runtime.InteropServices.Marshal]::ReleaseComObject($deck)|Out-Null
 $deck=$application.Presentations.Open($testCopy,0,0,0)
 $samples=@()
 foreach($slideNumber in @(18,19,22)){
  $nativeChart=$null
  foreach($shape in $deck.Slides.Item($slideNumber).Shapes){if($shape.HasChart -eq -1){$nativeChart=$shape;break}}
  if($null -eq $nativeChart){throw 'Native chart missing'}
  $nativeChart.Width+=6
  $series=$nativeChart.Chart.SeriesCollection(1)
  $newValues=switch($slideNumber){18{,@(36.0,18.0,11.0,10.0,19.0)}19{,@(224.0,223.0,211.0,201.0,204.0,162.0,3.0)}22{,@(4.1,4.1)}}
  $series.Values=$newValues
  $samples+=[PSCustomObject]@{slide=$slideNumber;shapeId=$nativeChart.Id;widthPoints=$nativeChart.Width;values=$newValues}
 }
 $deck.Save()
 $deck.Close()
 [Runtime.InteropServices.Marshal]::ReleaseComObject($deck)|Out-Null
 $deck=$application.Presentations.Open($testCopy,-1,0,0)
 foreach($sample in $samples){
  $chartShape=$null
  foreach($shape in $deck.Slides.Item($sample.slide).Shapes){if($shape.Id -eq $sample.shapeId){$chartShape=$shape;break}}
  if($null -eq $chartShape -or [Math]::Abs($chartShape.Width-$sample.widthPoints) -gt .01){throw 'Chart resize did not survive save and reopen'}
  $actual=@($chartShape.Chart.SeriesCollection(1).Values)
  if($actual.Count -ne $sample.values.Count){throw 'Chart value count differs'}
  for($i=0;$i -lt $actual.Count;$i++){if([Math]::Abs([double]$actual[$i]-[double]$sample.values[$i]) -gt .000001){throw 'Edited chart values did not survive reopen'}}
 }
 [PSCustomObject]@{application='Microsoft PowerPoint';version=$application.Version;exportedSlides=26;sampleChartsEditedResizedSavedReopened=$samples;finalFileChanged=$false}|
  ConvertTo-Json -Depth 8|Set-Content -LiteralPath (Join-Path $resolvedOutput 'native-review.json') -Encoding utf8
 Write-Output 'PowerPoint exported 26 slides and verified three editable chart copies'
}
finally{
 if($null -ne $deck){$deck.Close();[Runtime.InteropServices.Marshal]::ReleaseComObject($deck)|Out-Null}
 if($null -ne $application){if($application.Presentations.Count -eq 0){$application.Quit()};[Runtime.InteropServices.Marshal]::ReleaseComObject($application)|Out-Null}
}

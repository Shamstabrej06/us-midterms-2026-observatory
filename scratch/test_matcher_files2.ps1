$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$t = $asm.GetType("Microsoft.PowerBI.Packaging.Project.PBIProjectShredder")
$f = $t.GetField("EnhancedReportFormatMatcher", [System.Reflection.BindingFlags]"Public,NonPublic,Static")
$matcher = $f.GetValue($null)
Write-Host "Matcher is: $($matcher.GetType().FullName)"

$baseDir = "C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory.Report\definition"
$files = Get-ChildItem -Recurse -File $baseDir

$matched = 0
$unmatched = 0
foreach ($file in $files) {
    $rel = $file.FullName.Substring($baseDir.Length + 1)
    $isMatch = $matcher.IsMatch($rel)
    if ($isMatch) {
        $matched++
    } else {
        $unmatched++
        Write-Host "UNMATCHED: $rel"
    }
}
Write-Host "Matched: $matched, Unmatched: $unmatched"

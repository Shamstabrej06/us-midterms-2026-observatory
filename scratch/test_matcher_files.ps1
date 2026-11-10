$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$matcherType = $asm.GetType("Microsoft.PowerBI.Packaging.Project.EnhancedReportFormatMatcher")
$matcher = [Activator]::CreateInstance($matcherType)

$baseDir = "C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory.Report\definition"
$files = Get-ChildItem -Recurse -File $baseDir

foreach ($file in $files) {
    # Relative path from definition
    $rel = $file.FullName.Substring($baseDir.Length + 1)
    $isMatch = $matcher.IsMatch($rel)
    Write-Host "File: $rel -> IsMatch: $isMatch"
}

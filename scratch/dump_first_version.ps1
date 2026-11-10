$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$t = $asm.GetType("Microsoft.PowerBI.Packaging.Project.Artifacts.ReportDefinitionVersion")
$f = $t.GetField("FirstEnhancedReportVersion", [System.Reflection.BindingFlags]"Public,NonPublic,Static")
$val = $f.GetValue($null)
Write-Host "FirstEnhancedReportVersion = $val"

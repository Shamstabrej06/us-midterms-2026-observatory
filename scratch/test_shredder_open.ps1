$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$asmPkg = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Packaging.dll")
$asmClient = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Client.Windows.dll")

$shredder = $asmPkg.GetType("Microsoft.PowerBI.Packaging.Project.PBIProjectShredder")
$readerType = $asmPkg.GetType("Microsoft.PowerBI.Packaging.Project.DiskProjectFilesReader")
$reader = [Activator]::CreateInstance($readerType)

$pbipPath = "C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory.pbip"
$openMethod = $shredder.GetMethod("OpenProjectAsync", [System.Reflection.BindingFlags]"Public,Static", $null, @($readerType, [string], $asmPkg.GetType("Microsoft.PowerBI.Packaging.HostContext")), $null)

$task = $openMethod.Invoke($null, @($reader, $pbipPath, $null))
$proj = $task.GetAwaiter().GetResult()

Write-Host "Project loaded successfully!"
Write-Host "Report Path: $($proj.ReportPath)"
Write-Host "Report IsFileFormatV2: $($proj.Report.IsFileFormatV2)"
Write-Host "Report Exploration Count: $($proj.Report.Exploration.Count)"
foreach ($kv in $proj.Report.Exploration) {
    Write-Host "   Exploration Key: $($kv.Key)"
}

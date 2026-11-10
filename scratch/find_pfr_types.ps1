$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$asmPkg = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Packaging.dll")
$types = $asmPkg.GetTypes() | Where-Object { $_.GetInterface("IProjectFilesReader") -ne $null }
foreach ($t in $types) {
    Write-Host "Type: $($t.FullName)"
}

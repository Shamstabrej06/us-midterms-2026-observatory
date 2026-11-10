$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$types = $asm.GetTypes() | Where-Object { $_.Name -like "*Project*" -or $_.Name -like "*Pbip*" }
foreach ($t in $types) {
    Write-Host "Type: $($t.FullName)"
}

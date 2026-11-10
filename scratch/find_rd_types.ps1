$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$types = $asm.GetTypes()
foreach ($t in $types) {
    if ($t.Name -like "*ReportDefinition*") {
        Write-Host "Type: $($t.FullName)"
    }
}

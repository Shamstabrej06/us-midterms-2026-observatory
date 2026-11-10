$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$types = $asm.GetTypes() | Where-Object { $_.Name -like "*PBIR*" -or $_.Name -like "*Page*" -or $_.Name -like "*ReportDefinition*" }
foreach ($t in $types) {
    if ($t.FullName -like "*Pbir*" -or $t.FullName -like "*Packaging*") {
        Write-Host "Type: $($t.FullName)"
        $methods = $t.GetMethods([System.Reflection.BindingFlags]"Public,NonPublic,Static,Instance")
        foreach ($m in $methods | Select-Object -First 3) {
            Write-Host "   $($m.Name)"
        }
    }
}

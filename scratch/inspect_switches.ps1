$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$types = $asm.GetTypes() | Where-Object { $_.Name -like "*FeatureSwitch*" -or $_.Name -like "*Preview*" }
foreach ($t in $types) {
    Write-Host "Type: $($t.FullName)"
    $fields = $t.GetFields([System.Reflection.BindingFlags]"Public,NonPublic,Static")
    foreach ($f in $fields | Select-Object -First 10) {
        Write-Host "   $($f.Name) = $($f.GetValue($null))"
    }
}

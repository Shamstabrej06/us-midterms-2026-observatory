$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Client.Windows.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$t = $asm.GetType("Microsoft.PowerBI.Client.Windows.Services.PowerBIProjectPackagerFeatureSwitches")
Write-Host "Properties of $($t.FullName):"
foreach ($p in $t.GetProperties([System.Reflection.BindingFlags]"Public,NonPublic,Instance,Static")) {
    Write-Host "  Property: $($p.Name) ($($p.PropertyType.Name))"
}
Write-Host "Fields of $($t.FullName):"
foreach ($f in $t.GetFields([System.Reflection.BindingFlags]"Public,NonPublic,Instance,Static")) {
    Write-Host "  Field: $($f.Name) ($($f.FieldType.Name))"
}

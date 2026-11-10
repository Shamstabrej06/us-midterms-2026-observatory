$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$t = $asm.GetType("Microsoft.PowerBI.Packaging.Project.PBIProjectReport")
Write-Host "Properties of $($t.FullName):"
foreach ($p in $t.GetProperties([System.Reflection.BindingFlags]"Public,NonPublic,Instance,Static")) {
    Write-Host "  Property: $($p.Name) ($($p.PropertyType.Name))"
}

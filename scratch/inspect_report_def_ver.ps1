$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$t = $asm.GetType("Microsoft.PowerBI.Packaging.Project.Artifacts.ReportDefinitionVersion")
Write-Host "Type: $($t.FullName)"
$props = $t.GetProperties([System.Reflection.BindingFlags]"Public,NonPublic,Instance,Static")
foreach ($p in $props) {
    Write-Host "Property: $($p.Name) -> $($p.PropertyType)"
}
$methods = $t.GetMethods([System.Reflection.BindingFlags]"Public,NonPublic,Instance,Static")
foreach ($m in $methods) {
    Write-Host "Method: $($m.Name)"
}

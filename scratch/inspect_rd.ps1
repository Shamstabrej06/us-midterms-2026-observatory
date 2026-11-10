$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$t = $asm.GetType("Microsoft.PowerBI.Packaging.Project.Artifacts.ReportDefinition")
Write-Host "Base: $($t.BaseType.FullName)"
$props = $t.GetProperties([System.Reflection.BindingFlags]"Public,NonPublic,Instance,Static")
foreach ($p in $props) {
    Write-Host "Property: $($p.Name) -> $($p.PropertyType)"
}
$fields = $t.GetFields([System.Reflection.BindingFlags]"Public,NonPublic,Instance,Static")
foreach ($f in $fields) {
    Write-Host "Field: $($f.Name) = $($f.GetValue($null))"
}

$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
[System.Reflection.Assembly]::LoadFrom("$bin\Newtonsoft.Json.dll") | Out-Null
$asmPkg = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Packaging.dll")

$t = $asmPkg.GetType("Microsoft.PowerBI.Packaging.ExplorationContract")
Write-Host "Type: $($t.FullName)"
$props = $t.GetProperties([System.Reflection.BindingFlags]"Public,NonPublic,Instance")
foreach ($p in $props) {
    Write-Host "Property: $($p.Name) -> $($p.PropertyType)"
}

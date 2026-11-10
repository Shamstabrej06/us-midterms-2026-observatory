$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$t = $asm.GetType("Microsoft.PowerBI.Packaging.ExplorationDeserializationResult`1")
$props = $t.GetProperties([System.Reflection.BindingFlags]"Public,NonPublic,Instance")
foreach ($p in $props) {
    Write-Host "Property: $($p.Name) -> $($p.PropertyType)"
}

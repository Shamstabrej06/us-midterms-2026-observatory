$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$asm = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Packaging.dll")
$t = $asm.GetType("Microsoft.PowerBI.Packaging.Project.PbipContent")
Write-Host "Type: $($t.FullName)"
$ctors = $t.GetConstructors([System.Reflection.BindingFlags]"Public,NonPublic,Instance")
foreach ($c in $ctors) {
    $p = ($c.GetParameters() | ForEach-Object { "$($_.ParameterType.Name) $($_.Name)" }) -join ", "
    Write-Host "Ctor: ($p)"
}

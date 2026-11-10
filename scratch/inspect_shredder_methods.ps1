$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$asm = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Packaging.dll")
$t = $asm.GetType("Microsoft.PowerBI.Packaging.Project.PBIProjectShredder")
$methods = $t.GetMethods([System.Reflection.BindingFlags]"Public,NonPublic,Static,Instance") | Where-Object { $_.Name -like "*Open*" -or $_.Name -like "*Resolve*" }
foreach ($m in $methods) {
    $p = ($m.GetParameters() | ForEach-Object { "$($_.ParameterType.Name) $($_.Name)" }) -join ", "
    Write-Host "$($m.Name)($p)"
}

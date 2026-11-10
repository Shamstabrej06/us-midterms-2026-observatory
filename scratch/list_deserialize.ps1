$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$t = $asm.GetType("Microsoft.PowerBI.Packaging.ExplorationSerializer")

$methods = $t.GetMethods([System.Reflection.BindingFlags]"Public,NonPublic,Static,Instance") | Where-Object { $_.Name -like "*Deserialize*" }
foreach ($m in $methods) {
    $p = ($m.GetParameters() | ForEach-Object { "$($_.ParameterType.FullName) $($_.Name)" }) -join ", "
    $scope = if ($m.IsStatic) { "Static" } else { "Instance" }
    Write-Host "$scope $($m.Name)($p) -> $($m.ReturnType.FullName)"
}

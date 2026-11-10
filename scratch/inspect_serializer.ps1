$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$t = $asm.GetType("Microsoft.PowerBI.Packaging.ExplorationSerializer")
$methods = $t.GetMethods([System.Reflection.BindingFlags]"Public,NonPublic,Static,Instance")
foreach ($m in $methods) {
    if ($m.Name -like "*Page*" -or $m.Name -like "*Deserialize*") {
        $p = ($m.GetParameters() | ForEach-Object { "$($_.ParameterType.Name) $($_.Name)" }) -join ", "
        Write-Host "$($m.Name)($p)"
    }
}

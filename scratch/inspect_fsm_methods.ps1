$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Client.Windows.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$m = $asm.GetModules()[0]
$types = try { $m.GetTypes() } catch [System.Reflection.ReflectionTypeLoadException] { $_.Exception.Types | Where-Object { $_ -ne $null } }
$fsm = $types | Where-Object { $_.Name -eq "FeatureSwitchManager" }
foreach ($method in $fsm.GetMethods([System.Reflection.BindingFlags]"Public,NonPublic,Static,Instance")) {
    $p = ($method.GetParameters() | ForEach-Object { "$($_.ParameterType.Name) $($_.Name)" }) -join ", "
    Write-Host "$($method.Name)($p)"
}

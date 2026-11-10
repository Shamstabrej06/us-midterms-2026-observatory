$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Client.Windows.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$m = $asm.GetModules()[0]
$types = try { $m.GetTypes() } catch [System.Reflection.ReflectionTypeLoadException] { $_.Exception.Types | Where-Object { $_ -ne $null } }
$fsm = $types | Where-Object { $_.Name -eq "FeatureSwitchManager" }
$field = $fsm.GetField("EnhancedReportFormat", [System.Reflection.BindingFlags]"Public,NonPublic,Static")
$val = $field.GetValue($null)
Write-Host "Type of EnhancedReportFormat: $($val.GetType().FullName)"
foreach ($p in $val.GetType().GetProperties()) {
    Write-Host "  $($p.Name) = $($p.GetValue($val))"
}

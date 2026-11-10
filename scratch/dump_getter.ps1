$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Client.Windows.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$m = $asm.GetModules()[0]
$types = try { $m.GetTypes() } catch [System.Reflection.ReflectionTypeLoadException] { $_.Exception.Types | Where-Object { $_ -ne $null } }
$t = $types | Where-Object { $_.Name -eq "PowerBIProjectPackagerFeatureSwitches" }
foreach ($p in $t.GetProperties()) {
    $g = $p.GetGetMethod($true)
    $il = $g.GetMethodBody().GetILAsByteArray()
    $bytes = ($il | ForEach-Object { "0x{0:X2}" -f $_ }) -join " "
    Write-Host "$($p.Name) -> $bytes"
}

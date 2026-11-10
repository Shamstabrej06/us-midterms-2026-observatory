$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$asm = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Packaging.dll")
$t = $asm.GetType("Microsoft.PowerBI.Packaging.V2ExplorationUtils")
$f = $t.GetField("AllowedCharactersRegex", [System.Reflection.BindingFlags]"Public,NonPublic,Static")
Write-Host "AllowedCharactersRegex: $($f.GetValue($null))"

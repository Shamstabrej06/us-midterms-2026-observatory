$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$asm = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Packaging.dll")
$t = $asm.GetType("Microsoft.PowerBI.Packaging.Project.PBIProjectShredder")
$m = $t.GetMethod("AsStreamableContent", [System.Reflection.BindingFlags]"Public,NonPublic,Static")
$p = ($m.GetParameters() | ForEach-Object { "$($_.ParameterType.FullName) $($_.Name)" }) -join ", "
Write-Host "AsStreamableContent($p)"

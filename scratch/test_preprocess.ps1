$asm = [System.Reflection.Assembly]::LoadFrom("C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\PBIDesktop.exe")
$type = $asm.GetType("Microsoft.PowerBI.Client.CommandLine")
$preprocess = $type.GetMethod("PreProcess", [System.Reflection.BindingFlags]"NonPublic,Public,Static")

$argsArr = [string[]]@("C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory.pbip")
$params = [object[]]@($argsArr)
$preprocess.Invoke($null, $params)
Write-Host "PreProcessed args:" ($params[0] -join ", ")

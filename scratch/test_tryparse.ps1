$asm = [System.Reflection.Assembly]::LoadFrom("C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\PBIDesktop.exe")
$type = $asm.GetType("Microsoft.PowerBI.Client.CommandLine")
$method = $type.GetMethod("TryParse", [System.Reflection.BindingFlags]"Public,Static")

# Let's test calling TryParse with [ "C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory.pbip" ]
$argsArr = [string[]]@("C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory.pbip")
$parsedCmd = $null
$parameters = [object[]]@($null, $null, $argsArr, $true, $parsedCmd)
$res = $method.Invoke($null, $parameters)
Write-Host "TryParse returned: $res"
$parsed = $parameters[4]
if ($parsed) {
    Write-Host "FileName: $($parsed.FileName)"
    Write-Host "IsNewReport: $($parsed.IsNewReport())"
    Write-Host "FileType: $($parsed.GetFileType())"
}

$asm = [System.Reflection.Assembly]::LoadFrom("C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\PBIDesktop.exe")
$type = $asm.GetType("Microsoft.PowerBI.Client.CommandLine")
$method = $type.GetMethod("TryParse", [System.Reflection.BindingFlags]"Public,Static")
$body = $method.GetMethodBody()
$il = $body.GetILAsByteArray()
Write-Host "IL byte length: $($il.Length)"

# Let's inspect PreProcess and ProcessEnvSwitches
foreach ($m in @("PreProcess", "ProcessEnvSwitches", "ParseEncodedArgs")) {
    $minfo = $type.GetMethod($m, [System.Reflection.BindingFlags]"NonPublic,Public,Static")
    if ($minfo) {
        Write-Host "Found method $m"
    }
}

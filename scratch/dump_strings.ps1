$asm = [System.Reflection.Assembly]::LoadFrom("C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\PBIDesktop.exe")
$type = $asm.GetType("Microsoft.PowerBI.Client.CommandLine")
$method = $type.GetMethod("TryParse", [System.Reflection.BindingFlags]"Public,Static")
$body = $method.GetMethodBody()
$module = $method.Module

$il = $body.GetILAsByteArray()
for ($i = 0; $i -lt $il.Length; $i++) {
    $op = $il[$i]
    if ($op -eq 0x72) { # ldstr
        $token = [BitConverter]::ToInt32($il, $i + 1)
        try {
            $str = $module.ResolveString($token)
            Write-Host "ldstr: '$str'"
        } catch {}
    }
}

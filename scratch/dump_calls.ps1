$asm = [System.Reflection.Assembly]::LoadFrom("C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\PBIDesktop.exe")
$type = $asm.GetType("Microsoft.PowerBI.Client.CommandLine")
$method = $type.GetMethod("TryParse", [System.Reflection.BindingFlags]"Public,Static")
$body = $method.GetMethodBody()
$module = $method.Module

$il = $body.GetILAsByteArray()
for ($i = 0; $i -lt $il.Length; $i++) {
    $op = $il[$i]
    if ($op -eq 0x28 -or $op -eq 0x6F) { # call or callvirt
        $token = [BitConverter]::ToInt32($il, $i + 1)
        try {
            $m = $module.ResolveMethod($token)
            Write-Host "call: $($m.DeclaringType.Name)::$($m.Name)"
        } catch {}
    }
}

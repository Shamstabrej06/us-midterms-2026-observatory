$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$shredder = $asm.GetType("Microsoft.PowerBI.Packaging.Project.PBIProjectShredder")
$m = $shredder.GetMethod("ResolveReportExplorationAsync", [System.Reflection.BindingFlags]"NonPublic,Static")
$body = $m.GetMethodBody()
$module = $m.Module

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

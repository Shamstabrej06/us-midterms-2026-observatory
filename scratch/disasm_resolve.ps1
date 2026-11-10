$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$t = $asm.GetType("Microsoft.PowerBI.Packaging.Project.PBIProjectShredder+<ResolveReportExplorationAsync>d__6")
$m = $t.GetMethod("MoveNext", [System.Reflection.BindingFlags]"Public,NonPublic,Instance")
$body = $m.GetMethodBody()
$module = $m.Module
$il = $body.GetILAsByteArray()

for ($i = 0; $i -lt $il.Length; $i++) {
    $op = $il[$i]
    if ($op -eq 0x72) { # ldstr
        $token = [BitConverter]::ToInt32($il, $i + 1)
        try {
            $str = $module.ResolveString($token)
            Write-Host "[$i] ldstr: '$str'"
        } catch {}
    }
    if ($op -eq 0x28 -or $op -eq 0x6F) { # call/callvirt
        $token = [BitConverter]::ToInt32($il, $i + 1)
        try {
            $rm = $module.ResolveMethod($token)
            Write-Host "[$i] call: $($rm.DeclaringType.Name)::$($rm.Name)"
        } catch {}
    }
}

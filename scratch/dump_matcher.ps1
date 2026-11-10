$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$t = $asm.GetType("Microsoft.PowerBI.Packaging.Project.PBIProjectShredder+<ResolveReportExplorationAsync>d__6")
$m = $t.GetMethod("MoveNext", [System.Reflection.BindingFlags]"Public,NonPublic,Instance")
$module = $m.Module
$il = $m.GetMethodBody().GetILAsByteArray()

for ($i = 150; $i -lt 220; $i++) {
    if ($il[$i] -eq 0x28 -or $il[$i] -eq 0x6F -or $il[$i] -eq 0x73) { # call/callvirt/newobj
        $token = [BitConverter]::ToInt32($il, $i + 1)
        try {
            $rm = $module.ResolveMethod($token)
            Write-Host "[$i] new/call: $($rm.DeclaringType.Name)::$($rm.Name)"
        } catch {}
    }
}

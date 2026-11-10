$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$t = $asm.GetType("Microsoft.PowerBI.Packaging.Project.PBIProjectReport")
$m = $t.GetMethod("get_IsFileFormatV2", [System.Reflection.BindingFlags]"Public,NonPublic,Instance")
$module = $m.Module
$il = $m.GetMethodBody().GetILAsByteArray()

for ($i = 0; $i -lt $il.Length; $i++) {
    $op = $il[$i]
    if ($op -eq 0x72) {
        $tok = [BitConverter]::ToInt32($il, $i + 1)
        try { Write-Host "[$i] ldstr: '$($module.ResolveString($tok))'" } catch {}
    }
    if ($op -eq 0x28 -or $op -eq 0x6F -or $op -eq 0x73) {
        $tok = [BitConverter]::ToInt32($il, $i + 1)
        try { 
            $rm = $module.ResolveMethod($tok)
            Write-Host "[$i] call: $($rm.DeclaringType.Name)::$($rm.Name)" 
        } catch {}
    }
    if ($op -eq 0x7E -or $op -eq 0x7B) {
        $tok = [BitConverter]::ToInt32($il, $i + 1)
        try { 
            $rf = $module.ResolveField($tok)
            Write-Host "[$i] field: $($rf.DeclaringType.Name)::$($rf.Name)" 
        } catch {}
    }
}

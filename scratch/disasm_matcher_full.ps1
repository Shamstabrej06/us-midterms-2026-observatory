$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$t = $asm.GetType("Microsoft.PowerBI.Packaging.Project.EnhancedReportFormatMatcher")
$m = $t.GetMethod("IsMatch", [System.Reflection.BindingFlags]"Public,NonPublic,Instance")
$module = $m.Module
$il = $m.GetMethodBody().GetILAsByteArray()

for ($i = 0; $i -lt $il.Length; $i++) {
    $op = $il[$i]
    if ($op -eq 0x72) {
        $tok = [BitConverter]::ToInt32($il, $i + 1)
        try { Write-Host "[$i] ldstr: '$($module.ResolveString($tok))'" } catch {}
    }
    if ($op -eq 0x28 -or $op -eq 0x6F) {
        $tok = [BitConverter]::ToInt32($il, $i + 1)
        try { 
            $rm = $module.ResolveMethod($tok)
            Write-Host "[$i] call: $($rm.DeclaringType.Name)::$($rm.Name)" 
        } catch {}
    }
}

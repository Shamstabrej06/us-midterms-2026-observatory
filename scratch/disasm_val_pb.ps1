$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
[System.Reflection.Assembly]::LoadFrom("$bin\Newtonsoft.Json.dll") | Out-Null
$asmPkg = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Packaging.dll")
$t = $asmPkg.GetType("Microsoft.PowerBI.Packaging.V2ExplorationUtils")
$m = $t.GetMethod("ValidatePageBindings", [System.Reflection.BindingFlags]"Public,NonPublic,Static")
$module = $m.Module
$il = $m.GetMethodBody().GetILAsByteArray()

for ($i = 0; $i -lt $il.Length; $i++) {
    if ($il[$i] -eq 0x72) {
        $tok = [BitConverter]::ToInt32($il, $i + 1)
        try { Write-Host "[$i] ldstr: '$($module.ResolveString($tok))'" } catch {}
    }
    if ($il[$i] -eq 0x28 -or $il[$i] -eq 0x6F -or $il[$i] -eq 0x73) {
        $tok = [BitConverter]::ToInt32($il, $i + 1)
        try { 
            $rm = $module.ResolveMethod($tok)
            Write-Host "[$i] call: $($rm.DeclaringType.Name)::$($rm.Name)" 
        } catch {}
    }
    if ($il[$i] -eq 0x7E -or $il[$i] -eq 0x7B) {
        $tok = [BitConverter]::ToInt32($il, $i + 1)
        try { 
            $rf = $module.ResolveField($tok)
            Write-Host "[$i] field: $($rf.DeclaringType.Name)::$($rf.Name)" 
        } catch {}
    }
}

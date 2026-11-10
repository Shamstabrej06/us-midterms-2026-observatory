$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$t = $asm.GetType("Microsoft.PowerBI.Packaging.Project.PBIProjectReport")
$prop = $t.GetProperty("IsFileFormatV2")
$getter = $prop.GetGetMethod($true)
$body = $getter.GetMethodBody()
$m = $asm.GetModules()[0]
$il = $body.GetILAsByteArray()
for ($i = 0; $i -lt $il.Length; $i++) {
    if ($il[$i] -eq 0x72) {
        $tok = [BitConverter]::ToInt32($il, $i + 1)
        try { Write-Host "  ldstr:" $m.ResolveString($tok) } catch {}
    }
    if ($il[$i] -eq 0x28 -or $il[$i] -eq 0x6F) {
        $tok = [BitConverter]::ToInt32($il, $i + 1)
        try { 
            $rm = $m.ResolveMethod($tok)
            Write-Host "  call: $($rm.DeclaringType.Name)::$($rm.Name)" 
        } catch {}
    }
    if ($il[$i] -eq 0x7E -or $il[$i] -eq 0x7B) {
        $tok = [BitConverter]::ToInt32($il, $i + 1)
        try { 
            $rf = $m.ResolveField($tok)
            Write-Host "  ldfld: $($rf.DeclaringType.Name)::$($rf.Name)" 
        } catch {}
    }
}

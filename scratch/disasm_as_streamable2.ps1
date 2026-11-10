$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$asm = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Packaging.dll")
$t = $asm.GetType("Microsoft.PowerBI.Packaging.Project.PBIProjectShredder")
$m = $t.GetMethod("AsStreamableContent", [System.Reflection.BindingFlags]"Public,NonPublic,Static")
$module = $m.Module
$il = $m.GetMethodBody().GetILAsByteArray()

for ($i = 0; $i -lt $il.Length; $i++) {
    if ($il[$i] -eq 0x28 -or $il[$i] -eq 0x6F -or $il[$i] -eq 0x73) {
        $tok = [BitConverter]::ToInt32($il, $i + 1)
        try { 
            $rm = $module.ResolveMethod($tok)
            Write-Host "DeclaringType FullName: $($rm.DeclaringType.FullName) / $($rm.Name)" 
        } catch {}
    }
}

$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$t = $asm.GetType("Microsoft.PowerBI.Packaging.Project.EnhancedReportFormatMatcher")
foreach ($f in $t.GetFields([System.Reflection.BindingFlags]"Public,NonPublic,Static,Instance")) {
    $val = $f.GetValue($null)
    Write-Host "Field: $($f.Name) = $val"
}
$ctor = $t.GetConstructors([System.Reflection.BindingFlags]"Public,NonPublic,Static,Instance")[0]
$il = $ctor.GetMethodBody().GetILAsByteArray()
$m = $ctor.Module
for ($i = 0; $i -lt $il.Length; $i++) {
    if ($il[$i] -eq 0x72) {
        $tok = [BitConverter]::ToInt32($il, $i + 1)
        try { Write-Host "ctor ldstr: '$($m.ResolveString($tok))'" } catch {}
    }
}

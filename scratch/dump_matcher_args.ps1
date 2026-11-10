$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$t = $asm.GetType("Microsoft.PowerBI.Packaging.Project.PBIProjectShredder+<ResolveReportExplorationAsync>d__6")
$m = $t.GetMethod("MoveNext", [System.Reflection.BindingFlags]"Public,NonPublic,Instance")
$module = $m.Module
$il = $m.GetMethodBody().GetILAsByteArray()

for ($i = 175; $i -lt 210; $i++) {
    $op = $il[$i]
    if ($op -eq 0x73 -or $op -eq 0x28 -or $op -eq 0x6F) {
        $tok = [BitConverter]::ToInt32($il, $i + 1)
        try { Write-Host "[$i] call/new:" $module.ResolveMethod($tok).DeclaringType.Name "::" $module.ResolveMethod($tok).Name } catch {}
    }
    if ($op -eq 0x7E -or $op -eq 0x7B) {
        $tok = [BitConverter]::ToInt32($il, $i + 1)
        try { Write-Host "[$i] field:" $module.ResolveField($tok).Name } catch {}
    }
}

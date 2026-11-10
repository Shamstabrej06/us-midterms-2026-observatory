$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$asmClient = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Client.Windows.dll")
try { $allTypes = $asmClient.GetTypes() } catch [System.Reflection.ReflectionTypeLoadException] { $allTypes = $_.Exception.Types | Where-Object { $null -ne $_ } }
$t = $allTypes | Where-Object { $_.FullName -like "*GetEnhancedReportDocument*" }

$m = $t.GetMethod("MoveNext", [System.Reflection.BindingFlags]"Public,NonPublic,Instance")
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
}

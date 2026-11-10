$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$asm = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Client.Windows.dll")
try { $allTypes = $asm.GetTypes() } catch [System.Reflection.ReflectionTypeLoadException] { $allTypes = $_.Exception.Types | Where-Object { $null -ne $_ } }
$types = $allTypes | Where-Object { $_.FullName -like "*GetReportParts*b__*" }

foreach ($t in $types) {
    Write-Host "=== Type: $($t.FullName) ==="
    $m = $t.GetMethod("MoveNext", [System.Reflection.BindingFlags]"Public,NonPublic,Instance")
    if ($null -ne $m) {
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
        }
    }
}

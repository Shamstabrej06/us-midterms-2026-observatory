$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$asmClient = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Client.Windows.dll")
try { $types = $asmClient.GetTypes() } catch [System.Reflection.ReflectionTypeLoadException] { $types = $_.Exception.Types | Where-Object { $null -ne $_ } }

$t = $types | Where-Object { $_.Name -like "*EnhancedReportDocumentContent*" }
foreach ($x in $t) {
    Write-Host "Type: $($x.FullName)"
    $methods = $x.GetMethods([System.Reflection.BindingFlags]"Public,NonPublic,Instance,Static")
    foreach ($m in $methods) {
        Write-Host "   Method: $($m.Name)"
        $module = $m.Module
        $il = $m.GetMethodBody().GetILAsByteArray()
        for ($i = 0; $i -lt $il.Length; $i++) {
            if ($il[$i] -eq 0x72) {
                $tok = [BitConverter]::ToInt32($il, $i + 1)
                try { Write-Host "      [$i] ldstr: '$($module.ResolveString($tok))'" } catch {}
            }
            if ($il[$i] -eq 0x28 -or $il[$i] -eq 0x6F -or $il[$i] -eq 0x73) {
                $tok = [BitConverter]::ToInt32($il, $i + 1)
                try { 
                    $rm = $module.ResolveMethod($tok)
                    Write-Host "      [$i] call: $($rm.DeclaringType.Name)::$($rm.Name)" 
                } catch {}
            }
        }
    }
}

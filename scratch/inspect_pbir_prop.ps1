$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Client.Windows.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$m = $asm.GetModules()[0]
$types = try { $m.GetTypes() } catch [System.Reflection.ReflectionTypeLoadException] { $_.Exception.Types | Where-Object { $_ -ne $null } }

foreach ($t in $types) {
    $prop = $t.GetProperty("ReadEnhancedReportFormat", [System.Reflection.BindingFlags]"Public,NonPublic,Instance,Static")
    if ($prop) {
        Write-Host "Found in $($t.FullName)"
        $getter = $prop.GetGetMethod($true)
        $body = $getter.GetMethodBody()
        if ($body) {
            $il = $body.GetILAsByteArray()
            for ($i = 0; $i -lt $il.Length; $i++) {
                if ($il[$i] -eq 0x72) {
                    $tok = [BitConverter]::ToInt32($il, $i + 1)
                    try { Write-Host "  ldstr:" $m.ResolveString($tok) } catch {}
                }
                if ($il[$i] -eq 0x28 -or $il[$i] -eq 0x6F) {
                    $tok = [BitConverter]::ToInt32($il, $i + 1)
                    try { Write-Host "  call:" $m.ResolveMethod($tok).Name } catch {}
                }
                if ($il[$i] -eq 0x7E -or $il[$i] -eq 0x7B) { # ldfld / ldsfld
                    $tok = [BitConverter]::ToInt32($il, $i + 1)
                    try { Write-Host "  ldfld:" $m.ResolveField($tok).Name } catch {}
                }
            }
        }
    }
}

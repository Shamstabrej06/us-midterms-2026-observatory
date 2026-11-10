$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$asm = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Client.Windows.dll")
try { $types = $asm.GetTypes() } catch [System.Reflection.ReflectionTypeLoadException] { $types = $_.Exception.Types | Where-Object { $null -ne $_ } }

foreach ($t in $types) {
    foreach ($m in $t.GetMethods([System.Reflection.BindingFlags]"Public,NonPublic,Instance,Static")) {
        try {
            $il = $m.GetMethodBody().GetILAsByteArray()
            if ($null -ne $il) {
                for ($i = 0; $i -lt $il.Length; $i++) {
                    if ($il[$i] -eq 0x28 -or $il[$i] -eq 0x6F) {
                        $tok = [BitConverter]::ToInt32($il, $i + 1)
                        try {
                            $rm = $m.Module.ResolveMethod($tok)
                            if ($rm.Name -eq "PickupFromProject") {
                                Write-Host "$($t.FullName)::$($m.Name)"
                            }
                        } catch {}
                    }
                }
            }
        } catch {}
    }
}

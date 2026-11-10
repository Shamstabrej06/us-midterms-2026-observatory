$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$types = $asm.GetTypes()
foreach ($t in $types) {
    $methods = $t.GetMethods([System.Reflection.BindingFlags]"Public,NonPublic,Instance,Static")
    foreach ($m in $methods) {
        try {
            $il = $m.GetMethodBody().GetILAsByteArray()
            if ($null -ne $il) {
                for ($i = 0; $i -lt $il.Length; $i++) {
                    if ($il[$i] -eq 0x28 -or $il[$i] -eq 0x6F -or $il[$i] -eq 0x73) {
                        $tok = [BitConverter]::ToInt32($il, $i + 1)
                        try {
                            $rm = $m.Module.ResolveMethod($tok)
                            if ($rm.DeclaringType.Name -eq "ReportDefinitionVersion") {
                                Write-Host "$($t.FullName)::$($m.Name) calls $($rm.Name)"
                            }
                        } catch {}
                    }
                }
            }
        } catch {}
    }
}

$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$dlls = @("Microsoft.PowerBI.Packaging.dll", "Microsoft.PowerBI.Client.Windows.dll", "Microsoft.PowerBI.Client.Shared.dll")

foreach ($d in $dlls) {
    $asm = [System.Reflection.Assembly]::LoadFrom("$bin\$d")
    foreach ($t in $asm.GetTypes()) {
        foreach ($m in $t.GetMethods([System.Reflection.BindingFlags]"Public,NonPublic,Instance,Static")) {
            try {
                $il = $m.GetMethodBody().GetILAsByteArray()
                if ($null -ne $il) {
                    for ($i = 0; $i -lt $il.Length; $i++) {
                        if ($il[$i] -eq 0x28 -or $il[$i] -eq 0x6F) {
                            $tok = [BitConverter]::ToInt32($il, $i + 1)
                            try {
                                $rm = $m.Module.ResolveMethod($tok)
                                if ($rm.Name -eq "get_Exploration") {
                                    Write-Host "$d -> $($t.FullName)::$($m.Name)"
                                }
                            } catch {}
                        }
                    }
                }
            } catch {}
        }
    }
}

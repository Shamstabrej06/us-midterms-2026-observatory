$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$types = $asm.GetTypes() | Where-Object { $_.FullName -like "*ResolveReportExplorationAsync*" }
foreach ($t in $types) {
    Write-Host "Type: $($t.FullName)"
    $m = $t.GetMethod("MoveNext", [System.Reflection.BindingFlags]"Public,NonPublic,Instance")
    if ($m) {
        $body = $m.GetMethodBody()
        $module = $m.Module
        $il = $body.GetILAsByteArray()
        for ($i = 0; $i -lt $il.Length; $i++) {
            if ($il[$i] -eq 0x72) {
                $token = [BitConverter]::ToInt32($il, $i + 1)
                try {
                    $str = $module.ResolveString($token)
                    Write-Host "  ldstr: '$str'"
                } catch {}
            }
        }
    }
}

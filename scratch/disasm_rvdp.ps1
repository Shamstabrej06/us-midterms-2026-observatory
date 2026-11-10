$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$asmClient = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Client.Windows.dll")
$t = $asmClient.GetType("Microsoft.PowerBI.Client.Windows.ReportViewDocumentProvider")

$methods = $t.GetMethods([System.Reflection.BindingFlags]"Public,NonPublic,Instance,Static") | Where-Object { $_.Name -like "*GetReportDocument*" }
foreach ($m in $methods) {
    Write-Host "--- Method: $($m.Name) ---"
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

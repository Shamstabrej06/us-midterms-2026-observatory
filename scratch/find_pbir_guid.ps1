$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Client.Windows.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$m = $asm.GetModules()[0]
$types = try { $m.GetTypes() } catch [System.Reflection.ReflectionTypeLoadException] { $_.Exception.Types | Where-Object { $_ -ne $null } }
$fsType = $types | Where-Object { $_.Name -like "*FeatureSwitch*" -or $_.Name -like "*PreviewFeature*" }

foreach ($t in $fsType) {
    $fields = $t.GetFields([System.Reflection.BindingFlags]"Public,NonPublic,Static")
    foreach ($f in $fields) {
        $val = $f.GetValue($null)
        if ($val -is [Guid] -or $val -is [string]) {
            if ($f.Name -like "*Enhanced*" -or $f.Name -like "*Pbir*" -or $f.Name -like "*ReportFormat*") {
                Write-Host "$($t.Name).$($f.Name) = $val"
            }
        }
    }
}

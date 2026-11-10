$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Client.Windows.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$types = $asm.GetTypes()
foreach ($t in $types) {
    $fields = $t.GetFields([System.Reflection.BindingFlags]"Public,NonPublic,Static")
    foreach ($f in $fields) {
        $val = $f.GetValue($null)
        if ($val -is [Guid] -or $val -is [string]) {
            if ($val.ToString() -like "*22c217bb*") {
                Write-Host "Found in $($t.FullName).$($f.Name) = $val"
            }
        }
    }
}

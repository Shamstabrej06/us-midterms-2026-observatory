$asm = [System.Reflection.Assembly]::LoadFrom("C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\PBIDesktop.exe")
$types = $asm.GetTypes() | Where-Object { $_.Name -like "*CommandLine*" }
foreach ($t in $types) {
    Write-Host "Type: $($t.FullName)"
    $methods = $t.GetMethods([System.Reflection.BindingFlags]"Public,NonPublic,Static,Instance")
    foreach ($m in $methods) {
        $params = ($m.GetParameters() | ForEach-Object { "$($_.ParameterType.Name) $($_.Name)" }) -join ", "
        Write-Host "   $($m.Name)($params)"
    }
}

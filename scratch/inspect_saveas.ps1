$asm = [System.Reflection.Assembly]::LoadFrom('C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Client.Windows.dll')
$types = $asm.GetTypes() | Where-Object { $_.Name -like '*FileOperation*' }
foreach ($t in $types) {
    Write-Host "Type: $($t.FullName)"
    $t.GetMethods() | Where-Object { $_.Name -like '*SaveAs*' } | ForEach-Object {
        $params = ($_.GetParameters() | ForEach-Object { "$($_.ParameterType.Name) $($_.Name)" }) -join ", "
        Write-Host "   Method: $($_.Name)($params) -> $($_.ReturnType.Name)"
    }
}

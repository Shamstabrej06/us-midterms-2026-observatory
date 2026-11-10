$asm = [System.Reflection.Assembly]::LoadFrom('C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll')
$asm.GetTypes() | ForEach-Object {
    $t = $_
    $t.GetProperties() | Where-Object { $_.PropertyType.Name -like '*StaticResource*' } | ForEach-Object {
        "$($t.FullName).$($_.Name): $($_.PropertyType.FullName)"
    }
}

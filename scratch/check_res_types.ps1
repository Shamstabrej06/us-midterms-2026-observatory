Add-Type -Path 'C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll'
[AppDomain]::CurrentDomain.GetAssemblies() | Where-Object { $_.FullName -like '*Packaging*' } | ForEach-Object {
    $_.GetTypes() | Where-Object { $_.Name -like '*Resource*' -or $_.Name -like '*Static*' -or $_.Name -like '*Theme*' } | ForEach-Object {
        $_.FullName
    }
}

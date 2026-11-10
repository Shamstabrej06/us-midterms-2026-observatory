$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$asmClient = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Client.Windows.dll")
try { $types = $asmClient.GetTypes() } catch [System.Reflection.ReflectionTypeLoadException] { $types = $_.Exception.Types | Where-Object { $null -ne $_ } }

foreach ($t in $types) {
    if ($t.Name -like "*Exploration*" -or $t.Name -like "*ReportView*") {
        foreach ($m in $t.GetMethods([System.Reflection.BindingFlags]"Public,NonPublic,Instance,Static")) {
            if ($m.Name -like "*GetExploration*" -or $m.Name -like "*GetReport*") {
                Write-Host "$($t.FullName)::$($m.Name)"
            }
        }
    }
}

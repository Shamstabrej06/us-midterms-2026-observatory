$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$asm = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Client.Windows.dll")
try { $allTypes = $asm.GetTypes() } catch [System.Reflection.ReflectionTypeLoadException] { $allTypes = $_.Exception.Types | Where-Object { $null -ne $_ } }
$types = $allTypes | Where-Object { $_.FullName -like "*PowerBIReportPartReader*" }

foreach ($t in $types) {
    Write-Host "Type: $($t.FullName)"
    $methods = $t.GetMethods([System.Reflection.BindingFlags]"Public,NonPublic,Instance,Static")
    foreach ($m in $methods) {
        Write-Host "   Method: $($m.Name)"
    }
}

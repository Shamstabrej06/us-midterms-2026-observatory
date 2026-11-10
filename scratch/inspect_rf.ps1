$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$asm = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Client.Windows.dll")
try { $types = $asm.GetTypes() } catch [System.Reflection.ReflectionTypeLoadException] { $types = $_.Exception.Types | Where-Object { $null -ne $_ } }
$rf = $types | Where-Object { $_.Name -like "*ReportFactory*" }
foreach ($t in $rf) {
    Write-Host "Type: $($t.FullName)"
    $methods = $t.GetMethods([System.Reflection.BindingFlags]"Public,NonPublic,Static,Instance") | Where-Object { $_.Name -like "*Create*" }
    foreach ($m in $methods) {
        Write-Host "   Method: $($m.Name)"
    }
}

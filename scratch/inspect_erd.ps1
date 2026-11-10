$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$asmClient = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Client.Windows.dll")
try { $allTypes = $asmClient.GetTypes() } catch [System.Reflection.ReflectionTypeLoadException] { $allTypes = $_.Exception.Types | Where-Object { $null -ne $_ } }

$t = $allTypes | Where-Object { $_.Name -like "*EnhancedReportDocument*" }
foreach ($x in $t) {
    Write-Host "Type: $($x.FullName)"
    $props = $x.GetProperties([System.Reflection.BindingFlags]"Public,NonPublic,Instance")
    foreach ($p in $props) {
        Write-Host "   Property: $($p.Name) -> $($p.PropertyType)"
    }
}

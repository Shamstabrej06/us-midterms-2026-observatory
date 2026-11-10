$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$asmPkg = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Packaging.dll")
$asmClient = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Client.Windows.dll")
try { $types = $asmClient.GetTypes() } catch [System.Reflection.ReflectionTypeLoadException] { $types = $_.Exception.Types | Where-Object { $null -ne $_ } }

$t = $types | Where-Object { $_.Name -like "*PackagerHost*" }
foreach ($x in $t) {
    Write-Host "Type: $($x.FullName)"
    $f = $x.GetField("Context", [System.Reflection.BindingFlags]"Public,NonPublic,Static")
    if ($f) {
        Write-Host "Found Context static field on $($x.FullName)"
    }
}

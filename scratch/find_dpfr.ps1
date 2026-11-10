$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$asmClient = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Client.Windows.dll")
try { $types = $asmClient.GetTypes() } catch [System.Reflection.ReflectionTypeLoadException] { $types = $_.Exception.Types | Where-Object { $null -ne $_ } }
$t = $types | Where-Object { $_.Name -like "*ProjectFilesReader*" }
foreach ($x in $t) {
    Write-Host "Type: $($x.FullName)"
}

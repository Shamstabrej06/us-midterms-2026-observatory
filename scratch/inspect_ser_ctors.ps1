$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
[System.Reflection.Assembly]::LoadFrom("$bin\Newtonsoft.Json.dll") | Out-Null
$asmPkg = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Packaging.dll")
$serType = $asmPkg.GetType("Microsoft.PowerBI.Packaging.ExplorationSerializer")

foreach ($c in $serType.GetConstructors([System.Reflection.BindingFlags]"Public,NonPublic,Instance")) {
    $p = ($c.GetParameters() | ForEach-Object { "$($_.ParameterType.FullName) $($_.Name)" }) -join ", "
    Write-Host "Ctor: ($p)"
}

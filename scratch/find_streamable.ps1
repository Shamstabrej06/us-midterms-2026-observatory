$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$asmPkg = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Packaging.dll")

$types = $asmPkg.GetTypes() | Where-Object { $_.GetInterface("IStreamablePowerBIProjectPartContent") -ne $null }
foreach ($t in $types) {
    Write-Host "Streamable type: $($t.FullName)"
    $ctors = $t.GetConstructors([System.Reflection.BindingFlags]"Public,NonPublic,Instance")
    foreach ($c in $ctors) {
        $p = ($c.GetParameters() | ForEach-Object { "$($_.ParameterType.Name) $($_.Name)" }) -join ", "
        Write-Host "   Ctor: ($p)"
    }
}

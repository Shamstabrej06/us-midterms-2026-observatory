$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$asmPkg = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Packaging.dll")
$readerType = $asmPkg.GetType("Microsoft.PowerBI.Packaging.Project.DiskProjectFilesReader")
foreach ($c in $readerType.GetConstructors([System.Reflection.BindingFlags]"Public,NonPublic,Instance")) {
    $p = ($c.GetParameters() | ForEach-Object { "$($_.ParameterType.Name) $($_.Name)" }) -join ", "
    Write-Host "Ctor: ($p)"
}

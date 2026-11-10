$asm = [System.Reflection.Assembly]::LoadFrom('C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll')
$type = $asm.GetType('Microsoft.PowerBI.Packaging.Storage.StaticResourceCollection')
$type.GetMembers() | ForEach-Object {
    "$($_.MemberType): $($_.Name)"
}

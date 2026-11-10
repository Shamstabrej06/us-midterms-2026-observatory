$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$t = $asm.GetType("Microsoft.PowerBI.Packaging.ExplorationSerializer")

$baseDir = "C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory.Report\definition"
$files = Get-ChildItem -Recurse -File $baseDir

$fileDict = [System.Collections.Generic.Dictionary[string, byte[]]]::new()
foreach ($f in $files) {
    $rel = $f.FullName.Substring($baseDir.Length + 1).Replace("\", "/")
    $bytes = [System.IO.File]::ReadAllBytes($f.FullName)
    $fileDict.Add($rel, $bytes)
}

Write-Host "Dictionary populated with $($fileDict.Count) files."

# Let's inspect constructors of ExplorationSerializer
$ctors = $t.GetConstructors([System.Reflection.BindingFlags]"Public,NonPublic,Instance")
foreach ($c in $ctors) {
    $p = ($c.GetParameters() | ForEach-Object { "$($_.ParameterType.Name) $($_.Name)" }) -join ", "
    Write-Host "Ctor: ($p)"
}

# Or static methods
$staticMethods = $t.GetMethods([System.Reflection.BindingFlags]"Public,NonPublic,Static") | Where-Object { $_.Name -like "*Deserialize*" }
foreach ($sm in $staticMethods) {
    $p = ($sm.GetParameters() | ForEach-Object { "$($_.ParameterType.Name) $($_.Name)" }) -join ", "
    Write-Host "Static Method: $($sm.Name)($p)"
}

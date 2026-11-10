$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"

# Load Newtonsoft.Json first
[System.Reflection.Assembly]::LoadFrom("$bin\Newtonsoft.Json.dll") | Out-Null
$asmPkg = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Packaging.dll")

$baseDir = "C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory.Report\definition"
$files = Get-ChildItem -Recurse -File $baseDir

$fileDict = [System.Collections.Generic.Dictionary[Uri, Microsoft.PowerBI.Packaging.Project.IStreamablePowerBIProjectPartContent]]::new()
$streamableType = $asmPkg.GetType("Microsoft.PowerBI.Packaging.Project.StreamablePowerBIProjectPartContent")
$ctorBytes = $streamableType.GetConstructor(@([byte[]]))

foreach ($f in $files) {
    $rel = $f.FullName.Substring($baseDir.Length + 1).Replace("\", "/")
    if ($rel -eq "theme.json" -or $rel -like "StaticResources*") {
        continue
    }
    $bytes = [System.IO.File]::ReadAllBytes($f.FullName)
    $uri = [Uri]::new($rel, [UriKind]::Relative)
    $content = $ctorBytes.Invoke(@($bytes))
    $fileDict.Add($uri, $content)
}

Write-Host "Created fileDict with $($fileDict.Count) files."

# Create ExplorationSerializer
$serType = $asmPkg.GetType("Microsoft.PowerBI.Packaging.ExplorationSerializer")
$serCtor = $serType.GetConstructors([System.Reflection.BindingFlags]"Public,NonPublic,Instance")[0]

# Ctor params: (HostContext hostContext, ExplorationSerializerDeserializationParallelism deserializationParallelism, IV2ExplorationSchemas validationSchemas, ExplorationLimits explorationLimits)
$ser = $serCtor.Invoke(@($null, 0, $null, $null))

Write-Host "Calling DeserializeAsync..."
try {
    $task = $ser.DeserializeAsync($fileDict, [System.Threading.CancellationToken]::None, $false, 0)
    $res = $task.GetAwaiter().GetResult()
    Write-Host "Deserialization successful!"
    Write-Host "Value: $($res.Value)"
    if ($null -ne $res.SchemaValidationInfo) {
        Write-Host "SchemaValidationErrors: $($res.SchemaValidationInfo.SchemaValidationErrors.Count)"
        foreach ($err in $res.SchemaValidationInfo.SchemaValidationErrors) {
            Write-Host "   Schema Error: $err"
        }
    }
} catch {
    Write-Host "CAUGHT EXCEPTION:"
    Write-Host $_.Exception.ToString()
    if ($null -ne $_.Exception.InnerException) {
        Write-Host "INNER EXCEPTION:"
        Write-Host $_.Exception.InnerException.ToString()
        if ($null -ne $_.Exception.InnerException.InnerException) {
            Write-Host "INNER INNER EXCEPTION:"
            Write-Host $_.Exception.InnerException.InnerException.ToString()
        }
    }
}

$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$loadedJson = [System.Reflection.Assembly]::LoadFrom("$bin\Newtonsoft.Json.dll")

[System.AppDomain]::CurrentDomain.add_AssemblyResolve({
    param($sender, $args)
    if ($args.Name.StartsWith("Newtonsoft.Json")) {
        return $loadedJson
    }
    return $null
})

$asmPkg = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Packaging.dll")
$asmClient = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Client.Windows.dll")

$packagerHost = $asmClient.GetType("Microsoft.PowerBI.Client.Windows.Services.PackagerHost")
$contextField = $packagerHost.GetField("Context", [System.Reflection.BindingFlags]"Public,NonPublic,Static")
$context = $contextField.GetValue($null)

# Get ExplorationV2Schemas
$schemasType = $asmClient.GetType("Microsoft.PowerBI.Client.Windows.Services.ExplorationV2Schemas")
$schemas = $schemasType.GetMethod("Get", [System.Reflection.BindingFlags]"Public,NonPublic,Static").Invoke($null, @())
Write-Host "Got schemas: $($schemas.GetType().FullName)"

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
    $content = $ctorBytes.Invoke([object[]]@(,$bytes))
    $fileDict.Add($uri, $content)
}

$serType = $asmPkg.GetType("Microsoft.PowerBI.Packaging.ExplorationSerializer")
$serCtor = $serType.GetConstructors([System.Reflection.BindingFlags]"Public,NonPublic,Instance")[0]
$enumVal = [System.Enum]::ToObject($serCtor.GetParameters()[1].ParameterType, 0)
$ser = $serCtor.Invoke([object[]]@($context, $enumVal, $schemas, $null))

Write-Host "Calling DeserializeAsync WITH REAL schemas..."
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
    }
}

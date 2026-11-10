$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"
$packagingDll = "$bin\Microsoft.PowerBI.Packaging.dll"
$clientDll = "$bin\Microsoft.PowerBI.Client.Windows.dll"

[System.Reflection.Assembly]::LoadFrom($packagingDll) | Out-Null
[System.Reflection.Assembly]::LoadFrom($clientDll) | Out-Null

$baseDir = "C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory.Report\definition"
$files = Get-ChildItem -Recurse -File $baseDir

$fileDict = [System.Collections.Generic.Dictionary[Uri, Microsoft.PowerBI.Packaging.Project.IStreamablePowerBIProjectPartContent]]::new()
$streamableType = [System.Type]::GetType("Microsoft.PowerBI.Packaging.Project.StreamablePowerBIProjectPartMemoryContent, Microsoft.PowerBI.Packaging")

foreach ($f in $files) {
    $rel = $f.FullName.Substring($baseDir.Length + 1).Replace("\", "/")
    if ($rel -eq "theme.json" -or $rel -like "StaticResources*") {
        continue
    }
    $bytes = [System.IO.File]::ReadAllBytes($f.FullName)
    $uri = [Uri]::new($rel, [UriKind]::Relative)
    $content = [Activator]::CreateInstance($streamableType, @($bytes, [System.DateTime]::UtcNow))
    $fileDict.Add($uri, $content)
}

Write-Host "Created fileDict with $($fileDict.Count) files."

# Get ExplorationV2Schemas
$schemasType = [System.Type]::GetType("Microsoft.PowerBI.Client.Windows.ExplorationV2Schemas, Microsoft.PowerBI.Client.Windows")
$schemas = if ($null -ne $schemasType) {
    $schemasType.GetMethod("Get", [System.Reflection.BindingFlags]"Public,NonPublic,Static").Invoke($null, @())
} else {
    $null
}

# Create ExplorationSerializer
$serType = [System.Type]::GetType("Microsoft.PowerBI.Packaging.ExplorationSerializer, Microsoft.PowerBI.Packaging")
Write-Host "Serializer type found: $($serType.FullName)"

# Inspect constructors
$ctors = $serType.GetConstructors([System.Reflection.BindingFlags]"Public,NonPublic,Instance")
$ctor = $ctors[0]
$params = @($null, 0, $schemas, $null)
$ser = $ctor.Invoke($params)

Write-Host "Instantiated ExplorationSerializer. Calling DeserializeAsync..."
try {
    $task = $ser.DeserializeAsync($fileDict, [System.Threading.CancellationToken]::None, $false, 0)
    $res = $task.GetAwaiter().GetResult()
    Write-Host "Deserialization successful!"
    Write-Host "Value: $($res.Value)"
    if ($null -ne $res.SchemaValidationInfo) {
        Write-Host "Errors: $($res.SchemaValidationInfo.SchemaValidationErrors.Count)"
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

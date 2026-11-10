$bin = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin"

$resolving = $false
[System.AppDomain]::CurrentDomain.add_AssemblyResolve({
    param($sender, $args)
    if ($resolving) { return $null }
    $resolving = $true
    try {
        $assemblyName = ($args.Name -split ',')[0]
        $path = "$bin\$assemblyName.dll"
        if ([System.IO.File]::Exists($path)) {
            return [System.Reflection.Assembly]::LoadFrom($path)
        }
    } finally {
        $resolving = $false
    }
    return $null
})

$asmPkg = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Packaging.dll")
$asmClient = [System.Reflection.Assembly]::LoadFrom("$bin\Microsoft.PowerBI.Client.Windows.dll")

$shredder = $asmPkg.GetType("Microsoft.PowerBI.Packaging.Project.PBIProjectShredder")
$readerType = $asmClient.GetType("Microsoft.PowerBI.Client.Windows.Services.DiskProjectFilesReader")
$reader = [Activator]::CreateInstance($readerType)

$packagerHost = $asmClient.GetType("Microsoft.PowerBI.Client.Windows.Services.PackagerHost")
$contextField = $packagerHost.GetField("Context", [System.Reflection.BindingFlags]"Public,NonPublic,Static")
$context = $contextField.GetValue($null)

Write-Host "Context is: $($context.GetType().FullName)"

$pbipPath = "C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory.pbip"
$openMethod = $shredder.GetMethods([System.Reflection.BindingFlags]"Public,Static") | Where-Object { $_.Name -eq "OpenProjectAsync" -and $_.GetParameters().Count -eq 3 }

$task = $openMethod[0].Invoke($null, @($reader, $pbipPath, $context))
try {
    $proj = $task.GetAwaiter().GetResult()
    Write-Host "Project loaded successfully!"
    Write-Host "Report Path: $($proj.ReportPath)"
    Write-Host "Report IsFileFormatV2: $($proj.Report.IsFileFormatV2)"
    Write-Host "Report Exploration Count: $($proj.Report.Exploration.Count)"
} catch {
    Write-Host "EXCEPTION:"
    Write-Host $_.Exception.ToString()
    if ($_.Exception.InnerException) {
        Write-Host "INNER:"
        Write-Host $_.Exception.InnerException.ToString()
    }
}

$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$shredder = $asm.GetType("Microsoft.PowerBI.Packaging.Project.PBIProjectShredder")

# Find an implementation of IProjectFilesReader
$readerType = $asm.GetTypes() | Where-Object { [System.Reflection.CustomAttributeExtensions]::GetCustomAttributes($_) -ne $null } | Where-Object { $_.GetInterface("IProjectFilesReader") -ne $null }
Write-Host "Reader types: $($readerType.FullName -join ', ')"

if ($readerType) {
    $reader = [Activator]::CreateInstance($readerType[0])
    $pbipPath = "C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory.pbip"
    try {
        $task = $shredder.GetMethod("OpenProjectAsync", [System.Reflection.BindingFlags]"Public,Static", $null, @($readerType[0], [string], [type]::GetType("Microsoft.PowerBI.Packaging.HostContext, Microsoft.PowerBI.Packaging")), $null)
        if ($task) {
            Write-Host "Found OpenProjectAsync method"
        }
    } catch {
        Write-Host "Exception: $($_.Exception.ToString())"
    }
}

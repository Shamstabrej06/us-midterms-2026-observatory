$dll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Client.Windows.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$m = $asm.GetModules()[0]
$types = try { $m.GetTypes() } catch [System.Reflection.ReflectionTypeLoadException] { $_.Exception.Types | Where-Object { $_ -ne $null } }
$fsm = $types | Where-Object { $_.Name -eq "FeatureSwitchManager" }

$regMethod = $fsm.GetMethod("RegisterKnownSwitches", [System.Reflection.BindingFlags]"Public,NonPublic,Static")
if ($regMethod) { 
    $regMethod.Invoke($null, $null) 
    Write-Host "RegisterKnownSwitches succeeded!"
}

$names = $fsm.GetMethod("GetNames", [System.Reflection.BindingFlags]"Public,Static").Invoke($null, $null)
Write-Host "Total switches registered: $($names.Count)"
foreach ($n in $names) {
    if ($n -like "*Report*" -or $n -like "*Pbip*" -or $n -like "*Tmdl*" -or $n -like "*Project*" -or $n -like "*Enhanced*") {
        $sw = $fsm.GetMethod("GetFeatureSwitch", [System.Reflection.BindingFlags]"Public,Static").Invoke($null, @($n))
        $id = try { $sw.Id } catch { "no-id" }
        $title = try { $sw.Title } catch { "no-title" }
        Write-Host " - $n : ID=$id, Title=$title"
    }
}

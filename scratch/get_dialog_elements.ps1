Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$hwnd = [IntPtr]1048638
$el = [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)
if ($el) {
    Write-Host "Found element: $($el.Current.Name)"
    $all = $el.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    Write-Host "Total descendants: $($all.Count)"
    foreach ($item in $all) {
        $name = $item.Current.Name
        $ct = $item.Current.ControlType.ProgrammaticName
        $aid = $item.Current.AutomationId
        if ($name -or $aid) {
            Write-Host " - [$ct] ID='$aid' Name='$name'"
        }
    }
} else {
    Write-Host "Element not found"
}

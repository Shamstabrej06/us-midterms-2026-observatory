$sig = @'
[DllImport("user32.dll", SetLastError = true)]
public static extern IntPtr OpenDesktop(string lpszDesktop, uint dwFlags, bool fInherit, uint dwDesiredAccess);

[DllImport("user32.dll", SetLastError = true)]
public static extern bool SetThreadDesktop(IntPtr hDesktop);
'@
$win32 = Add-Type -MemberDefinition $sig -Name "Win32Desktop" -Namespace "Win32" -PassThru

$h = $win32::OpenDesktop("exebox-74RZTFYFMOWGO3HCYSNIF7SXYA", 0, $false, 0x01FF)
Write-Host "OpenDesktop handle: $h"
$res = $win32::SetThreadDesktop($h)
Write-Host "SetThreadDesktop result: $res"

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$root = [System.Windows.Automation.AutomationElement]::RootElement
$children = $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
Write-Host "Root children on desktop: $($children.Count)"
foreach ($c in $children) {
    Write-Host "Child: '$($c.Current.Name)' | Class: '$($c.Current.ClassName)'"
    if ($c.Current.Name -like "*Issue*" -or $c.Current.Name -like "*Power BI*") {
        $desc = $c.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
        foreach ($d in $desc) {
            if ($d.Current.Name) {
                Write-Host "   -> [$($d.Current.ControlType.ProgrammaticName)] $($d.Current.Name)"
            }
        }
    }
}

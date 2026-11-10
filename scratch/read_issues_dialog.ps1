$ts = [System.Threading.ThreadStart]{
    $sig = @'
    [DllImport("user32.dll", SetLastError = true)]
    public static extern IntPtr OpenDesktop(string lpszDesktop, uint dwFlags, bool fInherit, uint dwDesiredAccess);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SetThreadDesktop(IntPtr hDesktop);
'@
    $win32 = Add-Type -MemberDefinition $sig -Name "Win32ThreadDesktop2" -Namespace "Win32" -PassThru
    $h = $win32::OpenDesktop("exebox-74RZTFYFMOWGO3HCYSNIF7SXYA", 0, $false, 0x01FF)
    $res = $win32::SetThreadDesktop($h)
    Write-Host "Thread SetThreadDesktop: $res"
    
    Add-Type -AssemblyName UIAutomationClient
    Add-Type -AssemblyName UIAutomationTypes
    
    $root = [System.Windows.Automation.AutomationElement]::RootElement
    $dialog = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, "Issues were found")))
    if ($dialog) {
        Write-Host "Found dialog!"
        $desc = $dialog.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
        foreach ($d in $desc) {
            $n = $d.Current.Name
            $ct = $d.Current.ControlType.ProgrammaticName
            $aid = $d.Current.AutomationId
            $help = $d.Current.HelpText
            Write-Host "[$ct] Name='$n' ID='$aid' Help='$help'"
        }
    } else {
        Write-Host "Dialog not found"
    }
}

$t = [System.Threading.Thread]::new($ts)
$t.SetApartmentState([System.Threading.ApartmentState]::STA)
$t.Start()
$t.Join()

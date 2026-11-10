Add-Type -Path "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.AdomdClient.dll"
$port = 56045
$cat = "8457f476-7209-4c7c-88c4-180697ef1b01"
$connStr = "Data Source=localhost:$port;Initial Catalog=$cat;"
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection($connStr)
$conn.Open()

$kpis = @(
    "House Seats D 2026",
    "House Seats R 2026",
    "Senate Seats D 2026",
    "Senate Seats R 2026",
    "Senate Seats I 2026",
    "Gov Wins D 2026",
    "House Net Change D 2026",
    "House Popular Vote Margin 2026"
)

Write-Host "=== EVALUATING TARGET KPIS ==="
foreach ($k in $kpis) {
    try {
        $cmd = $conn.CreateCommand()
        $cmd.CommandText = "EVALUATE { [$k] }"
        $adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
        $dt = New-Object System.Data.DataTable
        $adapter.Fill($dt) | Out-Null
        $val = $dt.Rows[0][0]
        Write-Host "  [$k] = $val"
    } catch {
        Write-Host "  [$k] Error: $($_.Exception.Message)"
    }
}

$conn.Close()

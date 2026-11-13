Add-Type -Path "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.AdomdClient.dll"
$port = 50989
$cat = "6f5d90d2-415e-4d70-b935-907ab93cb970"
$connStr = "Data Source=localhost:$port;Initial Catalog=$cat;"
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection($connStr)
$conn.Open()

$kpis = @(
    "House Seats D 2026",
    "House Seats R 2026",
    "House Seats Uncalled 2026",
    "Senate Seats D 2026",
    "Senate Seats R 2026",
    "Senate Seats I 2026",
    "Gov Wins D 2026",
    "House Net Change D 2026",
    "House Popular Vote Margin 2026",
    "Total Midterm Spending 2026"
)

Write-Host "=== VERIFYING HEADLINE KPIS AGAINST REFRESHED MODEL ==="
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

Write-Host "`n=== TEXAS STATEWIDE 2026 RACES ==="
$txDax = @"
EVALUATE
FILTER(
    fact_texas_statewide,
    fact_texas_statewide[cycle] = 2026
)
"@
try {
    $cmd2 = $conn.CreateCommand()
    $cmd2.CommandText = $txDax
    $adapter2 = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd2)
    $dt2 = New-Object System.Data.DataTable
    $adapter2.Fill($dt2) | Out-Null
    foreach ($r in $dt2.Rows) {
        Write-Host "  Office: $($r['office']) | Dem: $($r['dem_candidate']) ($($r['dem_pct'])%) | Rep: $($r['rep_candidate']) ($($r['rep_pct'])%) | Margin: +$($r['margin_pts']) pts"
    }
} catch {
    Write-Host "Texas query error: $($_.Exception.Message)"
}

$conn.Close()

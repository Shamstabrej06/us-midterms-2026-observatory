Add-Type -Path "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.AdomdClient.dll"
$port = 50989
$connStr = "Data Source=localhost:$port;"
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection($connStr)
$conn.Open()
$cat = $conn.Databases[0].Name
$conn.ChangeDatabase($cat)

$kpis = @(
    "House Seats D 2026",
    "House Seats R 2026",
    "House Uncalled 2026",
    "Senate Seats D 2026",
    "Senate Seats R 2026",
    "Senate Seats I 2026",
    "Gov Wins D 2026",
    "House Net Change D 2026",
    "House Popular Vote Margin 2026"
)

Write-Host "Database: $cat"
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

# Also evaluate Texas Statewide results
Write-Host "`n=== TEXAS STATEWIDE RACES ==="
$txDax = @"
EVALUATE
SELECTCOLUMNS(
    fact_texas_statewide,
    "Office", fact_texas_statewide[office_name],
    "Democrat", fact_texas_statewide[dem_candidate],
    "Republican", fact_texas_statewide[rep_candidate],
    "Dem Margin", fact_texas_statewide[margin_pts]
)
"@
try {
    $cmd2 = $conn.CreateCommand()
    $cmd2.CommandText = $txDax
    $adapter2 = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd2)
    $dt2 = New-Object System.Data.DataTable
    $adapter2.Fill($dt2) | Out-Null
    foreach ($r in $dt2.Rows) {
        Write-Host "  $($r['Office']): $($r['Democrat']) vs $($r['Republican']) -> Dem Margin: +$($r['Dem Margin']) pts"
    }
} catch {
    Write-Host "Texas query error: $($_.Exception.Message)"
}

$conn.Close()

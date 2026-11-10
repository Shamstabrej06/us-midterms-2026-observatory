Add-Type -Path "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.AdomdClient.dll"
$port = 49907
$connStr = "Data Source=localhost:$port;"
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection($connStr)
$conn.Open()
$ds = $conn.GetSchemaDataSet("DBSCHEMA_CATALOGS", $null)
$cat = $ds.Tables[0].Rows[0]['CATALOG_NAME']
Write-Host "Catalog: $cat"
$conn.Close()

$connStr = "Data Source=localhost:$port;Initial Catalog=$cat;"
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection($connStr)
$conn.Open()
$ds = $conn.GetSchemaDataSet("DBSCHEMA_TABLES", $null)
Write-Host "`n--- Tables ---"
$tbls = 0
foreach ($row in $ds.Tables[0].Rows) {
    if ($row['TABLE_TYPE'] -eq 'TABLE') {
        Write-Host "Table: $($row['TABLE_NAME'])"
        $tbls++
    }
}
Write-Host "Total tables: $tbls"

Write-Host "`n--- Measures ---"
$cmd = $conn.CreateCommand()
$cmd.CommandText = "SELECT [MEASURE_NAME], [EXPRESSION] FROM `$SYSTEM.MDSCHEMA_MEASURES WHERE [MEASURE_NAME] <> '[RowsCount]'"
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null
Write-Host "Total measures in model: $($dt.Rows.Count)"
foreach ($r in $dt.Rows) {
    Write-Host " - $($r['MEASURE_NAME'])"
}

$conn.Close()

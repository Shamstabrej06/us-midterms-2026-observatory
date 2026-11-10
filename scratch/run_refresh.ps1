Add-Type -Path "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.AdomdClient.dll"
$port = 56045
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

$tmsl = @"
{
  "refresh": {
    "type": "full",
    "objects": [
      {
        "database": "$cat"
      }
    ]
  }
}
"@

Write-Host "Executing TMSL full refresh on database $cat..."
$cmd = $conn.CreateCommand()
$cmd.CommandText = $tmsl
try {
    $res = $cmd.ExecuteNonQuery()
    Write-Host "Refresh completed successfully! Result: $res"
} catch {
    Write-Host "Refresh Error: $($_.Exception.ToString())"
}

$conn.Close()

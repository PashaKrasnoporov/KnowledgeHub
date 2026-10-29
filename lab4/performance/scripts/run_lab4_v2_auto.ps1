param(
    [string]$Project = "D:\Studies\2026-2027_(1_magistr)\1_semester\Inform_merezhi_Rozrobka ta vykorystannia informatsiinykh merezh\KnowledgeHub",
    [string]$Duration = "15s",
    [string]$SearchQuery = "performance",
    [int]$SearchLimit = 10
)

$ErrorActionPreference = "Stop"

$ScriptDir = Join-Path $Project "lab4\performance\scripts"
$K6Script = Join-Path $ScriptDir "lab4_performance_v2.js"
$ResultsRoot = Join-Path $Project "lab4\performance\results"

if (-not (Test-Path $K6Script)) {
    throw "k6 script not found: $K6Script"
}

& k6 version | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "k6 is not available in PATH."
}

Write-Host ""
Write-Host "KnowledgeHub LR4 V2 automated performance experiment"
Write-Host "===================================================="
Write-Host "Local collection ID : 5"
Write-Host "Railway collection ID: 3"
Write-Host "Scenarios            : health, collections, documents, search"
Write-Host "VU levels            : 1, 10, 25"
Write-Host "Repeats              : 3"
Write-Host "Total runs           : 72"
Write-Host ""

$SecurePassword = Read-Host "Enter the performance-user password" -AsSecureString
$Password = [System.Net.NetworkCredential]::new("", $SecurePassword).Password

if ([string]::IsNullOrWhiteSpace($Password)) {
    throw "Password cannot be empty."
}

$Environments = @(
    [PSCustomObject]@{
        Name = "localhost"
        BaseUrl = "http://127.0.0.1:8000"
        Email = "performance.local.v2@example.com"
        CollectionId = "5"
    },
    [PSCustomObject]@{
        Name = "railway"
        BaseUrl = "https://knowledgehub-production-6644.up.railway.app"
        Email = "performance.railway.v2@example.com"
        CollectionId = "3"
    }
)

$Scenarios = @(
    [PSCustomObject]@{
        Name = "health"
        Endpoint = "GET /api/v1/health"
    },
    [PSCustomObject]@{
        Name = "collections"
        Endpoint = "GET /api/v1/collections"
    },
    [PSCustomObject]@{
        Name = "documents"
        Endpoint = "GET /api/v1/collections/{id}/documents"
    },
    [PSCustomObject]@{
        Name = "search"
        Endpoint = "GET /api/v1/collections/{id}/search?mode=lexical"
    }
)

$VuLevels = @(1, 10, 25)
$Runs = @(1, 2, 3)

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$RunDir = Join-Path $ResultsRoot ($Timestamp + "_v2")
$RawDir = Join-Path $RunDir "raw"

New-Item -ItemType Directory -Force $RawDir | Out-Null

$Rows = New-Object System.Collections.Generic.List[object]

$TotalRuns = 72
$CurrentRun = 0

function Get-MetricValue {
    param(
        $Metric,
        [string]$Name
    )

    if ($null -eq $Metric) {
        return $null
    }

    if ($null -eq $Metric.values) {
        return $null
    }

    $Property = $Metric.values.PSObject.Properties[$Name]

    if ($null -eq $Property) {
        return $null
    }

    return [double]$Property.Value
}

foreach ($Environment in $Environments) {
    foreach ($Scenario in $Scenarios) {
        foreach ($Vus in $VuLevels) {
            foreach ($Run in $Runs) {
                $CurrentRun = $CurrentRun + 1

                $Stem = "{0}_{1}_vus{2}_run{3}" -f `
                    $Environment.Name, `
                    $Scenario.Name, `
                    $Vus, `
                    $Run

                $JsonPath = Join-Path $RawDir ($Stem + ".json")

                Write-Host ""
                Write-Host ("[{0}/{1}] {2} | {3} | VU={4} | run={5}" -f `
                    $CurrentRun, `
                    $TotalRuns, `
                    $Environment.Name, `
                    $Scenario.Name, `
                    $Vus, `
                    $Run)

                $env:BASE_URL = $Environment.BaseUrl
                $env:SCENARIO = $Scenario.Name
                $env:TEST_EMAIL = $Environment.Email
                $env:TEST_PASSWORD = $Password
                $env:COLLECTION_ID = $Environment.CollectionId
                $env:SEARCH_QUERY = $SearchQuery
                $env:SEARCH_LIMIT = [string]$SearchLimit
                $env:VUS = [string]$Vus
                $env:DURATION = $Duration
                $env:SLEEP_SECONDS = "1"

                & k6 run `
                    --quiet `
                    --summary-export $JsonPath `
                    $K6Script

                if ($LASTEXITCODE -ne 0) {
                    throw ("k6 failed: {0}" -f $Stem)
                }

                if (-not (Test-Path $JsonPath)) {
                    throw ("Summary JSON was not created: {0}" -f $JsonPath)
                }

                $Summary = Get-Content $JsonPath -Raw | ConvertFrom-Json

                $DurationMetric = $Summary.metrics.target_req_duration
                $ReqMetric = $Summary.metrics.target_reqs
                $FailedMetric = $Summary.metrics.target_req_failed
                $ChecksMetric = $Summary.metrics.target_checks_success

                $ErrorRate = Get-MetricValue $FailedMetric "rate"
                $ChecksRate = Get-MetricValue $ChecksMetric "rate"

                if ($null -eq $ErrorRate) {
                    $ErrorRate = 1.0
                }

                if ($null -eq $ChecksRate) {
                    $ChecksRate = 0.0
                }

                if ($ErrorRate -gt 0.0) {
                    throw ("Measured request failed in {0}. error_rate={1}" -f $Stem, $ErrorRate)
                }

                if ($ChecksRate -lt 1.0) {
                    throw ("Checks failed in {0}. checks_rate={1}" -f $Stem, $ChecksRate)
                }

                $Row = [PSCustomObject]@{
                    environment = $Environment.Name
                    scenario = $Scenario.Name
                    endpoint = $Scenario.Endpoint
                    vus = $Vus
                    run = $Run
                    duration = $Duration
                    sleep_seconds = 1
                    avg_ms = Get-MetricValue $DurationMetric "avg"
                    median_ms = Get-MetricValue $DurationMetric "med"
                    p90_ms = Get-MetricValue $DurationMetric "p(90)"
                    p95_ms = Get-MetricValue $DurationMetric "p(95)"
                    p99_ms = Get-MetricValue $DurationMetric "p(99)"
                    req_per_s = Get-MetricValue $ReqMetric "rate"
                    error_rate_pct = 100.0 * $ErrorRate
                    checks_success_pct = 100.0 * $ChecksRate
                }

                $Rows.Add($Row)
            }
        }
    }
}

$ResultsCsv = Join-Path $RunDir "lab4_v2_results.csv"

$Rows |
    Export-Csv `
        -Path $ResultsCsv `
        -NoTypeInformation `
        -Encoding UTF8

$SummaryRows = New-Object System.Collections.Generic.List[object]

$Groups = $Rows | Group-Object {
    "{0}|{1}|{2}" -f $_.environment, $_.scenario, $_.vus
}

foreach ($Group in $Groups) {
    $Items = @($Group.Group)
    $First = $Items[0]

    $AvgValue = ($Items | Measure-Object -Property avg_ms -Average).Average
    $MedValue = ($Items | Measure-Object -Property median_ms -Average).Average
    $P90Value = ($Items | Measure-Object -Property p90_ms -Average).Average
    $P95Value = ($Items | Measure-Object -Property p95_ms -Average).Average
    $P99Value = ($Items | Measure-Object -Property p99_ms -Average).Average
    $ReqValue = ($Items | Measure-Object -Property req_per_s -Average).Average
    $ErrValue = ($Items | Measure-Object -Property error_rate_pct -Average).Average
    $ChkValue = ($Items | Measure-Object -Property checks_success_pct -Average).Average

    $SummaryRow = [PSCustomObject]@{
        environment = $First.environment
        scenario = $First.scenario
        endpoint = $First.endpoint
        vus = $First.vus
        repeats = $Items.Count
        avg_ms = [math]::Round([double]$AvgValue, 3)
        median_ms = [math]::Round([double]$MedValue, 3)
        p90_ms = [math]::Round([double]$P90Value, 3)
        p95_ms = [math]::Round([double]$P95Value, 3)
        p99_ms = [math]::Round([double]$P99Value, 3)
        req_per_s = [math]::Round([double]$ReqValue, 3)
        error_rate_pct = [math]::Round([double]$ErrValue, 3)
        checks_success_pct = [math]::Round([double]$ChkValue, 3)
    }

    $SummaryRows.Add($SummaryRow)
}

$SummaryCsv = Join-Path $RunDir "lab4_v2_summary.csv"

$SummaryRows |
    Sort-Object environment, scenario, vus |
    Export-Csv `
        -Path $SummaryCsv `
        -NoTypeInformation `
        -Encoding UTF8

$InfoFile = Join-Path $RunDir "experiment_info.txt"

$InfoLines = @(
    "KnowledgeHub LR4 V2 Performance Experiment",
    ("Generated: " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss")),
    "Branch: testova-gilka-1",
    "Localhost collection ID: 5",
    "Railway collection ID: 3",
    "Documents per collection: 5",
    "Scenarios: health, collections, documents, lexical search",
    "VU levels: 1, 10, 25",
    ("Duration per run: " + $Duration),
    "Repeats: 3",
    ("Total runs: " + $TotalRuns),
    "sleep_seconds: 1",
    ("Search query: " + $SearchQuery),
    ("Search limit: " + $SearchLimit)
)

$InfoLines | Set-Content -Path $InfoFile -Encoding ASCII

$RawCount = (Get-ChildItem $RawDir -Filter "*.json").Count

if ($RawCount -ne $TotalRuns) {
    throw ("Expected {0} raw JSON files, found {1}." -f $TotalRuns, $RawCount)
}

$ZipPath = Join-Path $ResultsRoot ($Timestamp + "_v2_results.zip")

if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
}

Compress-Archive `
    -Path (Join-Path $RunDir "*") `
    -DestinationPath $ZipPath `
    -Force

Remove-Item Env:TEST_PASSWORD -ErrorAction SilentlyContinue
$Password = $null
$SecurePassword = $null

Write-Host ""
Write-Host "===================================================="
Write-Host "EXPERIMENT COMPLETED SUCCESSFULLY"
Write-Host "===================================================="
Write-Host ("Runs                : {0}/{1}" -f $TotalRuns, $TotalRuns)
Write-Host ("Raw JSON count      : {0}" -f $RawCount)
Write-Host ("All runs CSV        : {0}" -f $ResultsCsv)
Write-Host ("Summary CSV         : {0}" -f $SummaryCsv)
Write-Host ("Experiment info     : {0}" -f $InfoFile)
Write-Host ("Results ZIP         : {0}" -f $ZipPath)
Write-Host ""
Write-Host "SUMMARY"

$SummaryRows |
    Sort-Object environment, scenario, vus |
    Format-Table `
        environment, `
        scenario, `
        vus, `
        avg_ms, `
        p95_ms, `
        p99_ms, `
        req_per_s, `
        error_rate_pct, `
        checks_success_pct `
        -AutoSize

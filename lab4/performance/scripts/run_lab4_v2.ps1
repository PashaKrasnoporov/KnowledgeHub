param(
    [string]$LocalBaseUrl = "http://127.0.0.1:8000",
    [string]$RailwayBaseUrl = "https://knowledgehub-production-6644.up.railway.app",
    [string]$Duration = "15s",
    [string]$SearchQuery = "performance",
    [int]$SearchLimit = 10
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$K6Script = Join-Path $ScriptDir "lab4_performance_v2.js"

if (-not (Test-Path $K6Script)) {
    throw "Cannot find k6 script: $K6Script"
}

try {
    k6 version | Out-Null
}
catch {
    throw "k6 is not available in PATH."
}

function Read-PlainPassword {
    param(
        [string]$Prompt
    )

    $secure = Read-Host $Prompt -AsSecureString

    return (
        [System.Net.NetworkCredential]::new(
            "",
            $secure
        ).Password
    )
}

Write-Host ""
Write-Host "KnowledgeHub LR4 Performance Experiment V2"
Write-Host "=========================================="
Write-Host ""
Write-Host "Use dedicated test users and the same test dataset"
Write-Host "in Localhost and Railway."
Write-Host ""

$LocalEmail = Read-Host "Localhost test user email"
$LocalPassword = Read-PlainPassword "Localhost test user password"
$LocalCollectionId = Read-Host "Localhost Performance Test collection ID"

Write-Host ""

$RailwayEmail = Read-Host "Railway test user email"
$RailwayPassword = Read-PlainPassword "Railway test user password"
$RailwayCollectionId = Read-Host "Railway Performance Test collection ID"

$VuLevels = @(1, 10, 25)
$Runs = @(1, 2, 3)
$Scenarios = @(
    "health",
    "collections",
    "documents",
    "search"
)

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$ResultsRoot = Join-Path (
    Split-Path $ScriptDir -Parent
) "results"
$RunDir = Join-Path $ResultsRoot "${Timestamp}_v2"
$RawDir = Join-Path $RunDir "raw"

New-Item -ItemType Directory -Force $RawDir |
    Out-Null

$Rows = @()

$Environments = @(
    @{
        Name = "localhost"
        BaseUrl = $LocalBaseUrl
        Email = $LocalEmail
        Password = $LocalPassword
        CollectionId = $LocalCollectionId
    },
    @{
        Name = "railway"
        BaseUrl = $RailwayBaseUrl
        Email = $RailwayEmail
        Password = $RailwayPassword
        CollectionId = $RailwayCollectionId
    }
)

function Get-MetricValue {
    param(
        $Metric,
        [string]$Name
    )

    if (
        $null -eq $Metric -or
        $null -eq $Metric.values
    ) {
        return $null
    }

    $property = $Metric.values.PSObject.Properties[
        $Name
    ]

    if ($null -eq $property) {
        return $null
    }

    return [double]$property.Value
}

foreach ($Environment in $Environments) {
    foreach ($Scenario in $Scenarios) {
        foreach ($Vus in $VuLevels) {
            foreach ($Run in $Runs) {

                $Stem = (
                    "{0}_{1}_vus{2}_run{3}" -f
                    $Environment.Name,
                    $Scenario,
                    $Vus,
                    $Run
                )

                $JsonPath = Join-Path (
                    $RawDir
                ) "${Stem}.json"

                Write-Host ""
                Write-Host (
                    "Running: {0} | {1} | VU={2} | run={3}" -f
                    $Environment.Name,
                    $Scenario,
                    $Vus,
                    $Run
                )

                $env:BASE_URL = $Environment.BaseUrl
                $env:SCENARIO = $Scenario
                $env:TEST_EMAIL = $Environment.Email
                $env:TEST_PASSWORD = $Environment.Password
                $env:COLLECTION_ID = $Environment.CollectionId
                $env:SEARCH_QUERY = $SearchQuery
                $env:SEARCH_LIMIT = "$SearchLimit"
                $env:VUS = "$Vus"
                $env:DURATION = $Duration
                $env:SLEEP_SECONDS = "1"

                & k6 run `
                    --summary-export $JsonPath `
                    $K6Script

                if ($LASTEXITCODE -ne 0) {
                    throw (
                        "k6 failed for $Stem " +
                        "with exit code $LASTEXITCODE"
                    )
                }

                $Summary = Get-Content (
                    $JsonPath
                ) -Raw | ConvertFrom-Json

                $DurationMetric =
                    $Summary.metrics.target_req_duration
                $ReqMetric =
                    $Summary.metrics.target_reqs
                $FailedMetric =
                    $Summary.metrics.target_req_failed
                $ChecksMetric =
                    $Summary.metrics.target_checks_success

                $Endpoint = switch ($Scenario) {
                    "health" {
                        "GET /api/v1/health"
                    }
                    "collections" {
                        "GET /api/v1/collections"
                    }
                    "documents" {
                        "GET /api/v1/collections/{id}/documents"
                    }
                    "search" {
                        "GET /api/v1/collections/{id}/search?mode=lexical"
                    }
                }

                $Rows += [PSCustomObject]@{
                    environment = $Environment.Name
                    scenario = $Scenario
                    endpoint = $Endpoint
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
                    error_rate_pct = (
                        100 *
                        (Get-MetricValue $FailedMetric "rate")
                    )
                    checks_success_pct = (
                        100 *
                        (Get-MetricValue $ChecksMetric "rate")
                    )
                }
            }
        }
    }
}

$ResultsCsv = Join-Path (
    $RunDir
) "lab4_v2_results.csv"

$Rows |
    Export-Csv `
        -Path $ResultsCsv `
        -NoTypeInformation `
        -Encoding UTF8

$SummaryRows = @()

$Groups = $Rows | Group-Object {
    "$($_.environment)|$($_.scenario)|$($_.vus)"
}

foreach ($Group in $Groups) {
    $Items = $Group.Group
    $First = $Items[0]

    $SummaryRows += [PSCustomObject]@{
        environment = $First.environment
        scenario = $First.scenario
        endpoint = $First.endpoint
        vus = $First.vus
        repeats = $Items.Count
        avg_ms = [math]::Round(
            ($Items |
                Measure-Object avg_ms -Average
            ).Average,
            3
        )
        median_ms = [math]::Round(
            ($Items |
                Measure-Object median_ms -Average
            ).Average,
            3
        )
        p90_ms = [math]::Round(
            ($Items |
                Measure-Object p90_ms -Average
            ).Average,
            3
        )
        p95_ms = [math]::Round(
            ($Items |
                Measure-Object p95_ms -Average
            ).Average,
            3
        )
        p99_ms = [math]::Round(
            ($Items |
                Measure-Object p99_ms -Average
            ).Average,
            3
        )
        req_per_s = [math]::Round(
            ($Items |
                Measure-Object req_per_s -Average
            ).Average,
            3
        )
        error_rate_pct = [math]::Round(
            ($Items |
                Measure-Object error_rate_pct -Average
            ).Average,
            3
        )
        checks_success_pct = [math]::Round(
            ($Items |
                Measure-Object checks_success_pct -Average
            ).Average,
            3
        )
    }
}

$SummaryCsv = Join-Path (
    $RunDir
) "lab4_v2_summary.csv"

$SummaryRows |
    Sort-Object environment, scenario, vus |
    Export-Csv `
        -Path $SummaryCsv `
        -NoTypeInformation `
        -Encoding UTF8

Remove-Item Env:TEST_PASSWORD -ErrorAction SilentlyContinue
Remove-Item Env:TEST_EMAIL -ErrorAction SilentlyContinue
Remove-Item Env:COLLECTION_ID -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Experiment completed."
Write-Host "Raw JSON:"
Write-Host "  $RawDir"
Write-Host "All runs CSV:"
Write-Host "  $ResultsCsv"
Write-Host "Averaged summary CSV:"
Write-Host "  $SummaryCsv"

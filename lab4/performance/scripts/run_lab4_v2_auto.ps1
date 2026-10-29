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

function Convert-DurationToSeconds {
    param([string]$Value)

    if ($Value -match '^([0-9]+(?:\.[0-9]+)?)s$') {
        return [double]$Matches[1]
    }

    if ($Value -match '^([0-9]+(?:\.[0-9]+)?)m$') {
        return ([double]$Matches[1] * 60.0)
    }

    throw "Unsupported duration format: $Value"
}

function Get-Percentile {
    param(
        [double[]]$Values,
        [double]$Percentile
    )

    if ($null -eq $Values -or $Values.Count -eq 0) {
        return $null
    }

    $Sorted = @($Values | Sort-Object)

    if ($Sorted.Count -eq 1) {
        return [double]$Sorted[0]
    }

    $Index = ($Percentile / 100.0) * ($Sorted.Count - 1)

    $Lower = [math]::Floor($Index)
    $Upper = [math]::Ceiling($Index)

    if ($Lower -eq $Upper) {
        return [double]$Sorted[$Lower]
    }

    $Weight = $Index - $Lower

    return (
        [double]$Sorted[$Lower] +
        (
            ([double]$Sorted[$Upper] - [double]$Sorted[$Lower]) *
            $Weight
        )
    )
}

function Get-PointValues {
    param(
        [string]$Path,
        [string]$MetricName
    )

    $Values = @()

    foreach ($Line in Get-Content -LiteralPath $Path) {

        if ([string]::IsNullOrWhiteSpace($Line)) {
            continue
        }

        try {
            $Object = $Line | ConvertFrom-Json
        }
        catch {
            continue
        }

        if (
            $Object.type -eq "Point" -and
            $Object.metric -eq $MetricName
        ) {
            $Values += [double]$Object.data.value
        }
    }

    return @($Values)
}

Write-Host ""
Write-Host "KnowledgeHub LR4 V2"
Write-Host "Automated performance experiment"
Write-Host "================================"
Write-Host "Environments : localhost, Railway"
Write-Host "Scenarios    : health, collections, documents, search"
Write-Host "VU levels    : 1, 10, 25"
Write-Host "Repeats      : 3"
Write-Host "Total runs   : 72"
Write-Host ""

$SecurePassword = Read-Host "Enter the performance-user password" -AsSecureString

$Password = [System.Net.NetworkCredential]::new(
    "",
    $SecurePassword
).Password

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
$Repeats = @(1, 2, 3)

$DurationSeconds = Convert-DurationToSeconds $Duration

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

$RunDir = Join-Path $ResultsRoot ($Timestamp + "_v2")
$RawDir = Join-Path $RunDir "raw"

New-Item -ItemType Directory -Force $RawDir | Out-Null

$Rows = @()

$TotalRuns = 72
$CurrentRun = 0

foreach ($Environment in $Environments) {

    foreach ($Scenario in $Scenarios) {

        foreach ($Vus in $VuLevels) {

            foreach ($Run in $Repeats) {

                $CurrentRun++

                $Stem = "{0}_{1}_vus{2}_run{3}" -f `
                    $Environment.Name,
                    $Scenario.Name,
                    $Vus,
                    $Run

                $JsonPath = Join-Path $RawDir ($Stem + ".json")

                Write-Host ""
                Write-Host (
                    "[{0}/{1}] {2} | {3} | VU={4} | run={5}" -f `
                    $CurrentRun,
                    $TotalRuns,
                    $Environment.Name,
                    $Scenario.Name,
                    $Vus,
                    $Run
                )

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
                    --summary-mode=disabled `
                    --out ("json=" + $JsonPath) `
                    $K6Script

                if ($LASTEXITCODE -ne 0) {
                    throw "k6 failed: $Stem"
                }

                if (-not (Test-Path $JsonPath)) {
                    throw "Raw JSON was not created: $JsonPath"
                }

                $Durations = @(
                    Get-PointValues `
                        -Path $JsonPath `
                        -MetricName "target_req_duration"
                )

                $Failures = @(
                    Get-PointValues `
                        -Path $JsonPath `
                        -MetricName "target_req_failed"
                )

                $Checks = @(
                    Get-PointValues `
                        -Path $JsonPath `
                        -MetricName "target_checks_success"
                )

                $RequestCounter = @(
                    Get-PointValues `
                        -Path $JsonPath `
                        -MetricName "target_reqs"
                )

                if ($Durations.Count -eq 0) {
                    throw "No target_req_duration samples: $Stem"
                }

                if ($Failures.Count -eq 0) {
                    throw "No target_req_failed samples: $Stem"
                }

                if ($Checks.Count -eq 0) {
                    throw "No target_checks_success samples: $Stem"
                }

                if ($RequestCounter.Count -eq 0) {
                    throw "No target_reqs samples: $Stem"
                }

                $Average = (
                    $Durations |
                    Measure-Object -Average
                ).Average

                $Median = Get-Percentile `
                    -Values $Durations `
                    -Percentile 50

                $P90 = Get-Percentile `
                    -Values $Durations `
                    -Percentile 90

                $P95 = Get-Percentile `
                    -Values $Durations `
                    -Percentile 95

                $P99 = Get-Percentile `
                    -Values $Durations `
                    -Percentile 99

                $FailureAverage = (
                    $Failures |
                    Measure-Object -Average
                ).Average

                $CheckAverage = (
                    $Checks |
                    Measure-Object -Average
                ).Average

                $RequestCount = (
                    $RequestCounter |
                    Measure-Object -Sum
                ).Sum

                $ErrorPercent = 100.0 * [double]$FailureAverage
                $ChecksPercent = 100.0 * [double]$CheckAverage
                $RequestsPerSecond = [double]$RequestCount / $DurationSeconds

                if ($ErrorPercent -gt 0.000001) {
                    throw (
                        "Measured request failure: {0}. Error={1}%" -f `
                        $Stem,
                        $ErrorPercent
                    )
                }

                if ($ChecksPercent -lt 99.999) {
                    throw (
                        "Check failure: {0}. Checks={1}%" -f `
                        $Stem,
                        $ChecksPercent
                    )
                }

                $Rows += [PSCustomObject]@{
                    environment = $Environment.Name
                    scenario = $Scenario.Name
                    endpoint = $Scenario.Endpoint
                    vus = $Vus
                    run = $Run
                    duration_seconds = $DurationSeconds
                    sleep_seconds = 1
                    request_count = [int]$RequestCount
                    avg_ms = [math]::Round([double]$Average, 3)
                    median_ms = [math]::Round([double]$Median, 3)
                    p90_ms = [math]::Round([double]$P90, 3)
                    p95_ms = [math]::Round([double]$P95, 3)
                    p99_ms = [math]::Round([double]$P99, 3)
                    req_per_s = [math]::Round(
                        [double]$RequestsPerSecond,
                        3
                    )
                    error_rate_pct = [math]::Round(
                        [double]$ErrorPercent,
                        3
                    )
                    checks_success_pct = [math]::Round(
                        [double]$ChecksPercent,
                        3
                    )
                }
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

$SummaryRows = @()

$Groups = $Rows | Group-Object {
    "{0}|{1}|{2}" -f `
        $_.environment,
        $_.scenario,
        $_.vus
}

foreach ($Group in $Groups) {

    $Items = @($Group.Group)
    $First = $Items[0]

    $SummaryRows += [PSCustomObject]@{
        environment = $First.environment
        scenario = $First.scenario
        endpoint = $First.endpoint
        vus = $First.vus
        repeats = $Items.Count

        avg_ms = [math]::Round(
            [double](
                $Items |
                Measure-Object avg_ms -Average
            ).Average,
            3
        )

        median_ms = [math]::Round(
            [double](
                $Items |
                Measure-Object median_ms -Average
            ).Average,
            3
        )

        p90_ms = [math]::Round(
            [double](
                $Items |
                Measure-Object p90_ms -Average
            ).Average,
            3
        )

        p95_ms = [math]::Round(
            [double](
                $Items |
                Measure-Object p95_ms -Average
            ).Average,
            3
        )

        p99_ms = [math]::Round(
            [double](
                $Items |
                Measure-Object p99_ms -Average
            ).Average,
            3
        )

        req_per_s = [math]::Round(
            [double](
                $Items |
                Measure-Object req_per_s -Average
            ).Average,
            3
        )

        error_rate_pct = [math]::Round(
            [double](
                $Items |
                Measure-Object error_rate_pct -Average
            ).Average,
            3
        )

        checks_success_pct = [math]::Round(
            [double](
                $Items |
                Measure-Object checks_success_pct -Average
            ).Average,
            3
        )
    }
}

$SummaryCsv = Join-Path $RunDir "lab4_v2_summary.csv"

$SummaryRows |
    Sort-Object environment, scenario, vus |
    Export-Csv `
        -Path $SummaryCsv `
        -NoTypeInformation `
        -Encoding UTF8

$InfoFile = Join-Path $RunDir "experiment_info.txt"

@(
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
    "Total runs: 72",
    "sleep_seconds: 1",
    ("Search query: " + $SearchQuery),
    ("Search limit: " + $SearchLimit),
    "Metrics source: k6 raw JSON Point records"
) |
    Set-Content `
        -Path $InfoFile `
        -Encoding ASCII

$RawCount = (
    Get-ChildItem $RawDir -Filter "*.json" -File
).Count

if ($RawCount -ne 72) {
    throw "Expected 72 JSON files, found $RawCount."
}

$ZipPath = Join-Path `
    $ResultsRoot `
    ($Timestamp + "_v2_results.zip")

Compress-Archive `
    -Path (Join-Path $RunDir "*") `
    -DestinationPath $ZipPath `
    -Force

Remove-Item Env:TEST_PASSWORD -ErrorAction SilentlyContinue

$Password = $null
$SecurePassword = $null

Write-Host ""
Write-Host "=========================================="
Write-Host "EXPERIMENT COMPLETED SUCCESSFULLY"
Write-Host "=========================================="
Write-Host "Runs           : 72/72"
Write-Host "Raw JSON count : $RawCount"
Write-Host "Results CSV    : $ResultsCsv"
Write-Host "Summary CSV    : $SummaryCsv"
Write-Host "ZIP            : $ZipPath"
Write-Host ""

$SummaryRows |
    Sort-Object environment, scenario, vus |
    Format-Table `
        environment,
        scenario,
        vus,
        avg_ms,
        p95_ms,
        p99_ms,
        req_per_s,
        error_rate_pct,
        checks_success_pct `
        -AutoSize
<#
.SYNOPSIS
    Runs the Playwright async test suite and opens the Allure HTML report.

.DESCRIPTION
    Builds a pytest command from the supplied parameters, executes it, then
    generates the Allure HTML report from the collected results and opens it
    in the default browser.

    API-only runs (Marker = 'api' or TestPath under tests/api) are always
    executed headless and never open a headed browser window.

.PARAMETER Browser
    Browser engine(s): chromium, firefox or webkit. Repeatable to run across multiple
    browsers, e.g. -Browser chromium -Browser firefox -Browser webkit.
    Defaults to the BROWSER env var.

.PARAMETER Device
    Device emulation (repeatable): a Playwright device name (e.g. 'iPhone 12',
    'Pixel 5') or a preset: desktop / tablet / mobile. Repeat to run across
    multiple devices, e.g. -Device "Pixel 5" -Device "iPhone 7".

.PARAMETER Viewport
    Custom viewport size as WxH, e.g. '1024x768'. Ignored when Device is set.

.PARAMETER Headed
    Run in headed (visible) mode. UI tests default to headless.

.PARAMETER Workers
    Number of parallel workers passed to pytest -n. Use 0 to disable
    parallelism. Default keeps pytest.ini (-n auto).

.PARAMETER TestPath
    Test target: a directory, file or node id. Defaults to 'tests'.

.PARAMETER Marker
    Pytest marker to select tests, e.g. ui, api, smoke, regression.

.PARAMETER Reruns
    Number of reruns for failed tests (default from pytest.ini).

.PARAMETER RerunsDelay
    Delay in seconds between reruns (default from pytest.ini).

.PARAMETER MaxFail
    Stop after N failures (default from pytest.ini).

.PARAMETER NoMaximize
    Do not maximize the window; use the default 1280x720 viewport.

.PARAMETER Trace
    Record a Playwright trace for each test (sets RECORD_TRACE=1).

.PARAMETER Video
    Record a video for each test (sets RECORD_VIDEO=1).

.PARAMETER TraceMode
    When to record/keep a Playwright trace: on, off, only-on-failure,
    on-first-retry, on-all-retries or on-success. Passed as --trace-mode.

.PARAMETER VideoMode
    When to record/keep a video: on, off, only-on-failure, on-first-retry,
    on-all-retries or on-success. Passed as --video.

.PARAMETER ScreenshotMode
    When to take a screenshot: on, off, only-on-failure, on-first-retry,
    on-all-retries or on-success. Passed as --screenshot.

.PARAMETER SkipAllure
    Skip Allure report generation and auto-open.

.PARAMETER NoOpen
    Generate the Allure report but do not open it in the browser.

.PARAMETER HtmlReport
    Path of the pytest HTML report (default reports/report.html).

.PARAMETER ExtraArgs
    Additional arguments passed straight through to pytest, e.g. -ExtraArgs "--tb=long","-v".

.EXAMPLE
    .\run_tests.ps1
    Run the full suite with default settings; open the Allure report afterwards.

.EXAMPLE
    .\run_tests.ps1 -Browser firefox -Headed
    Run all tests headed on Firefox.

.EXAMPLE
    .\run_tests.ps1 -Browser webkit -Device "iPhone 12"
    Run all tests on an emulated iPhone 12 (webkit).

.EXAMPLE
    .\run_tests.ps1 -TestPath tests/UI -Workers 2 -Video
    Run only the UI suite with 2 workers and video recording.

.EXAMPLE
    .\run_tests.ps1 -Marker api
    Run only API tests; forced headless automatically.

.EXAMPLE
    .\run_tests.ps1 -TestPath tests/UI -NoOpen -SkipAllure
    Run UI tests without generating or opening any report.
#>
[CmdletBinding()]
param(
    [string]$Viewport,

    [switch]$Headed,

    [int]$Workers = -1,

    [string]$TestPath = "tests",

    [string]$Marker,

    [int]$Reruns = -1,

    [int]$RerunsDelay = -1,

    [int]$MaxFail = -1,

    [switch]$NoMaximize,

    [switch]$Trace,

    [switch]$Video,

    [string]$TraceMode,

    [string]$VideoMode,

    [string]$ScreenshotMode,

    [switch]$DisableAdBlock,

    [switch]$SkipAllure,

    [switch]$NoOpen,

    [string]$HtmlReport = "reports/report.html",

    [string[]]$ExtraArgs,

    # -Browser and -Device are intentionally NOT declared here so they can be
    # repeated (-Browser chromium -Browser firefox); the raw tokens are captured
    # by $Remaining and parsed below.
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Remaining
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = $ScriptDir
$Python = Join-Path $RootDir "venv\Scripts\python.exe"
$AllureCmd = "allure"

# ------------------------------------------------------------------------- #
# Sanity checks
# ------------------------------------------------------------------------- #
if (-not (Test-Path -LiteralPath $Python)) {
    throw "Virtual environment not found: $Python. Run 'python -m venv venv' and 'venv\Scripts\pip install -r requirements.txt' first."
}

$AllureExe = Get-Command $AllureCmd -ErrorAction SilentlyContinue
if (-not $SkipAllure -and -not $AllureExe) {
    throw "Allure CLI not found on PATH. Install it (e.g. scoop install allure) or use -SkipAllure."
}

# ------------------------------------------------------------------------- #
# Normalize repeatable Browser/Device values (support comma-separated too)
# ------------------------------------------------------------------------- #
function Expand-ListParam {
    param([string[]]$Values)
    $result = @()
    foreach ($v in $Values) {
        foreach ($part in ($v -split ',')) {
            $trimmed = $part.Trim()
            if ($trimmed) { $result += $trimmed }
        }
    }
    return $result
}

# Parse repeated -Browser / -Device flags from the raw argument list.
$Browser = @()
$Device = @()
$i = 0
while ($i -lt $Remaining.Count) {
    $tok = $Remaining[$i]
    if ($tok -eq "-Browser" -or $tok -eq "--browser") {
        if ($i + 1 -ge $Remaining.Count) { throw "-Browser requires a value." }
        $Browser += $Remaining[$i + 1]
        $i += 2
    } elseif ($tok -eq "-Device" -or $tok -eq "--device") {
        if ($i + 1 -ge $Remaining.Count) { throw "-Device requires a value." }
        $Device += $Remaining[$i + 1]
        $i += 2
    } else {
        throw "Unknown argument '$tok'. Use -Browser/-Device (repeatable), or -ExtraArgs for pytest flags."
    }
}

$Browser = @(Expand-ListParam -Values $Browser)
$Device = @(Expand-ListParam -Values $Device)

$ValidBrowsers = @("chromium", "chrome", "firefox", "webkit")
foreach ($b in $Browser) {
    if ($ValidBrowsers -notcontains $b) {
        throw "Unknown browser '$b'. Valid: $($ValidBrowsers -join ', ')."
    }
}

$ValidModes = @("only-on-failure", "on", "off", "on-first-retry", "on-all-retries", "on-success")
foreach ($m in @($TraceMode, $VideoMode, $ScreenshotMode)) {
    if ($m -and $ValidModes -notcontains $m) {
        throw "Invalid mode '$m'. Valid: $($ValidModes -join ', ')."
    }
}

# ------------------------------------------------------------------------- #
# Concurrency: scale workers down for multi-scenario runs so the live site
# (automationexercise.com) isn't hit by too many concurrent browser instances
# at once (Cloudflare rate-limits under heavy concurrency).
# ------------------------------------------------------------------------- #
if ($Workers -lt 0) {
    $ScenarioCount = [Math]::Max(1, $Browser.Count) * [Math]::Max(1, $Device.Count)
    if ($ScenarioCount -gt 1) {
        $Procs = [int][Math]::Max(2, [int]$env:NUMBER_OF_PROCESSORS)
        $Workers = [Math]::Max(2, [Math]::Floor($Procs / $ScenarioCount))
        Write-Host "Multiple scenarios ($ScenarioCount): capping parallelism to $Workers workers." -ForegroundColor Yellow
    }
}

# ------------------------------------------------------------------------- #
# Environment overrides
# ------------------------------------------------------------------------- #
$env:BASE_URL = if ($env:BASE_URL) { $env:BASE_URL } else { "https://automationexercise.com" }
$env:API_BASE_URL = if ($env:API_BASE_URL) { $env:API_BASE_URL } else { "https://automationexercise.com" }
if ($Trace) { $env:RECORD_TRACE = "true" }
if ($Video) { $env:RECORD_VIDEO = "true" }
if ($DisableAdBlock) { $env:BLOCK_ADS = "false" }

# ------------------------------------------------------------------------- #
# API runs never open a headed browser
# ------------------------------------------------------------------------- #
$IsApiOnly = $false
if ($Marker -and $Marker -eq "api") {
    $IsApiOnly = $true
}
if ($TestPath -and $TestPath -match "^tests[/\\]api") {
    $IsApiOnly = $true
}

# ------------------------------------------------------------------------- #
# Build the pytest argument list
# ------------------------------------------------------------------------- #
$Args = [System.Collections.Generic.List[string]]::new()

if ($Browser) { foreach ($b in $Browser) { $Args.Add("--browser"); $Args.Add($b) } }
if ($Device) { foreach ($d in $Device) { $Args.Add("--device"); $Args.Add($d) } }
if ($Viewport) { $Args.Add("--viewport"); $Args.Add($Viewport) }

if ($IsApiOnly) {
    $Args.Add("--headless")
} elseif ($Headed) {
    $Args.Add("--headed")
} else {
    $Args.Add("--headless")
}

if ($Workers -ge 0) { $Args.Add("-n"); $Args.Add("$Workers") }
if ($Marker) { $Args.Add("-m"); $Args.Add($Marker) }
if ($Reruns -ge 0) { $Args.Add("--reruns"); $Args.Add("$Reruns") }
if ($RerunsDelay -ge 0) { $Args.Add("--reruns-delay"); $Args.Add("$RerunsDelay") }
if ($MaxFail -ge 0) { $Args.Add("--maxfail"); $Args.Add("$MaxFail") }
if ($NoMaximize) { $Args.Add("--no-maximized") }

if ($TraceMode) { $Args.Add("--trace-mode"); $Args.Add($TraceMode) }
if ($VideoMode) { $Args.Add("--video"); $Args.Add($VideoMode) }
if ($ScreenshotMode) { $Args.Add("--screenshot"); $Args.Add($ScreenshotMode) }

$Args.Add("--html=$HtmlReport")
$Args.Add("--alluredir=allure_reports/results")
$Args.Add($TestPath)

if ($ExtraArgs) {
    foreach ($extra in $ExtraArgs) {
        $Args.Add($extra)
    }
}

# ------------------------------------------------------------------------- #
# Run pytest
# ------------------------------------------------------------------------- #
Write-Host ""
Write-Host "=== Playwright Async Test Runner ===" -ForegroundColor Cyan
Write-Host "Python   : $Python"
Write-Host "Target   : $TestPath" $(if ($Marker) { " (marker: $Marker)" } else { "" })
Write-Host "Browser  : $(if ($Browser) { $Browser -join ', ' } else { 'default (env)' })"
Write-Host "Device   : $(if ($Device) { $Device -join ', ' } else { 'default' })"
Write-Host "Trace    : $(if ($TraceMode) { $TraceMode } elseif ($Trace) { 'on' } else { 'off' })"
Write-Host "Video    : $(if ($VideoMode) { $VideoMode } elseif ($Video) { 'on' } else { 'off' })"
Write-Host "Screenshot: $(if ($ScreenshotMode) { $ScreenshotMode } else { 'only-on-failure' })"
Write-Host "Mode     : $(if ($IsApiOnly) { 'headless (API forced)' } elseif ($Headed) { 'headed' } else { 'headless' })"
if ($Workers -ge 0) { Write-Host "Workers  : $Workers" }
Write-Host ""
Write-Host "pytest $($Args -join ' ')" -ForegroundColor DarkGray
Write-Host ""

& $Python -m pytest @Args
$ExitCode = $LASTEXITCODE
if ($null -eq $ExitCode) { $ExitCode = 1 }

Write-Host ""
Write-Host "pytest finished with exit code $ExitCode" -ForegroundColor Yellow

# ------------------------------------------------------------------------- #
# Allure report generation + auto-open
# ------------------------------------------------------------------------- #
if (-not $SkipAllure) {
    $ResultsDir = Join-Path $RootDir "allure_reports\results"
    $ReportDir = Join-Path $RootDir "allure_reports\html"
    $IndexHtml = Join-Path $ReportDir "index.html"

    if (-not (Test-Path -LiteralPath $ResultsDir)) {
        Write-Host "No Allure results found at $ResultsDir - skipping report generation." -ForegroundColor Red
    } else {
        Write-Host "Generating Allure report..." -ForegroundColor Cyan
        # Run through cmd.exe so the .cmd shim propagates the real exit code and
        # its stderr (e.g. 'Picked up JAVA_TOOL_OPTIONS: ...') never becomes a
        # terminating NativeCommandError under $ErrorActionPreference='Stop',
        # which would otherwise abort the script before the report is opened.
        $AllureOutput = & cmd.exe /d /c "call $AllureCmd generate `"$ResultsDir`" -o `"$ReportDir`" --clean --single-file 2>&1"
        $AllureExitCode = $LASTEXITCODE
        if ($AllureOutput) { $AllureOutput | ForEach-Object { Write-Host $_ } }

        if ($AllureExitCode -eq 0 -and (Test-Path -LiteralPath $IndexHtml) -and -not $NoOpen) {
            Write-Host "Opening Allure report in default browser..." -ForegroundColor Cyan
            try {
                Start-Process -FilePath $IndexHtml -ErrorAction Stop
            } catch {
                Write-Host "Could not auto-open the report: $($_.Exception.Message)" -ForegroundColor Yellow
                Write-Host "Open it manually: $IndexHtml" -ForegroundColor Yellow
            }
        } elseif (-not $NoOpen) {
            Write-Host "Allure report generated at $IndexHtml" -ForegroundColor Green
        }
    }
}

exit $ExitCode

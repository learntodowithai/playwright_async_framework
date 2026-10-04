# Test Runner — `run_tests.bat` / `run_tests.ps1`

A thin wrapper around `pytest` that runs the Playwright async test suite, then
generates the **Allure HTML report** and opens it in your default browser.

## Prerequisites

- Python 3.10+ virtual environment at `venv\`
- Dependencies installed: `venv\Scripts\pip install -r requirements.txt`
- Playwright browsers installed: `venv\Scripts\playwright install`
- **Allure CLI** on PATH (optional, only needed for report generation).
  Install via Scoop: `scoop install allure`, or add `-SkipAllure`.

## Usage

```bat
run_tests.bat [parameters]
```

Both `run_tests.bat` (batch) and `run_tests.ps1` (PowerShell) accept the same
parameters. From PowerShell you can also get inline help:

```powershell
Get-Help .\run_tests.ps1 -Full
```

## Parameters

| Parameter | Values / Example | Description |
|---|---|---|
| `-Browser` | `chromium`, `firefox`, `webkit` | Browser engine(s). Repeat the flag to run across multiple browsers: `-Browser chromium -Browser firefox -Browser webkit` (comma-separated also works: `-Browser "chromium,webkit"`). Defaults to `BROWSER` env var. |
| `-Device` | `"iPhone 12"`, `"Pixel 5"`, `desktop`, `tablet`, `mobile` | Device emulation (Playwright device name or preset). Repeat the flag to run across multiple devices: `-Device "Pixel 5" -Device "iPhone 7"` (comma-separated also works). |
| `-Viewport` | `1024x768` | Custom viewport size. Ignored when `-Device` is set. |
| `-Headed` | switch | Run UI tests with a visible browser window. Default is headless. |
| `-Workers` | `2`, `8`, `0` | Parallel workers for `-n`. `0` disables parallelism. Default keeps pytest.ini (`-n auto`), unless the run spans multiple browsers/devices — see below. |
| `-TestPath` | `tests`, `tests/UI`, `tests/api/test_login_api.py::TestLoginAPI` | Test target. Defaults to `tests`. |
| `-Marker` | `ui`, `api`, `smoke`, `regression` | Run tests matching the marker. |
| `-Reruns` | `2` | Rerun failed tests N times. |
| `-RerunsDelay` | `2` | Seconds between reruns. |
| `-MaxFail` | `5` | Stop after N failures. |
| `-NoMaximize` | switch | Use 1280x720 viewport instead of maximizing the window. |
| `-Trace` | switch | Record a Playwright trace per test (equivalent to `-TraceMode on`). |
| `-Video` | switch | Record a video per test (equivalent to `-VideoMode on`). |
| `-TraceMode` | `on`, `off`, `only-on-failure`, `on-first-retry`, `on-all-retries`, `on-success` | When to record/keep a Playwright trace. Overrides `RECORD_TRACE` env. |
| `-VideoMode` | `on`, `off`, `only-on-failure`, `on-first-retry`, `on-all-retries`, `on-success` | When to record/keep a video. Overrides `RECORD_VIDEO` env. |
| `-ScreenshotMode` | `on`, `off`, `only-on-failure`, `on-first-retry`, `on-all-retries`, `on-success` | When to take a screenshot. Default `only-on-failure`. |
| `-DisableAdBlock` | switch | Do not block ad/tracker requests (ads are blocked by default). |
| `-SkipAllure` | switch | Do not generate or open the Allure report. |
| `-NoOpen` | switch | Generate the report but do not open it. |
| `-HtmlReport` | `reports/report.html` | Path of the pytest HTML report. |
| `-ExtraArgs` | `"--tb=long","-v"` | Extra arguments passed straight to pytest. |

## Examples

```bat
:: Full suite, default settings, auto-open Allure report
run_tests.bat

:: UI tests on Firefox, headed
run_tests.bat -Browser firefox -Headed

:: Mobile emulation on webkit
run_tests.bat -Browser webkit -Device "iPhone 12"

:: Run every test in all three engines (repeat the -Browser flag)
run_tests.bat -Browser chromium -Browser firefox -Browser webkit

:: Cross-product: 2 browsers x 2 devices (repeat the flags)
run_tests.bat -Browser chromium -Browser webkit -Device "Pixel 5" -Device "iPhone 7"

:: UI suite only, 2 workers, with video
run_tests.bat -TestPath tests/UI -Workers 2 -Video

:: API tests only (always headless)
run_tests.bat -Marker api

:: API directory, no parallelism, no report
run_tests.bat -TestPath tests/api -Workers 0 -SkipAllure

:: Headed run without auto-opening the report
run_tests.bat -Headed -NoOpen
```

## Multi-browser / multi-device concurrency

When the run spans multiple browsers **or** devices (e.g. `-Browser chromium -Browser firefox`
or `-Device "Pixel 5" -Device "iPhone 7"`), the runner automatically scales the default
parallelism down to `logical CPUs ÷ scenario count` (min 2 workers). This keeps the number of
concurrent browser instances against the live site low enough to avoid Cloudflare rate-limiting
under full `-n auto` concurrency. An explicit `-Workers N` always overrides this.

## API tests and headed mode

API runs **never open a browser window**. If the run targets only API tests
(`-Marker api` or `-TestPath tests\api...`), the runner automatically forces
`--headless` and ignores `-Headed`. API tests only exercise the REST endpoints
via Playwright's request context, so no browser UI is needed.

## Artifacts / Reports

Ad requests to known ad/tracker hosts (`googlesyndication.com`, `doubleclick.net`, etc.) are
aborted automatically so overlay ad iframes cannot intercept clicks; disable with
`-DisableAdBlock` (or `BLOCK_ADS=false`).

Trace / video / screenshot capture is controlled per artifact with a **mode**:

| Mode | Behavior |
|---|---|
| `on` | Always capture and keep the artifact. |
| `off` | Never capture it. |
| `only-on-failure` | Keep only when the test failed (default for screenshots). |
| `on-success` | Keep only when the test passed. |
| `on-first-retry` | Keep only on the first retry run of the test. |
| `on-all-retries` | Keep on any retry run, drop on the first run. |

```bat
:: Trace only when a test fails
run_tests.bat -TraceMode only-on-failure

:: Video always, screenshot only on retries, no traces
run_tests.bat -VideoMode on -ScreenshotMode on-all-retries
```

| Output | Location |
|---|---|
| Allure results | `allure_reports/results/` |
| Allure HTML report | `allure_reports/html/index.html` (single-file, self-contained, opens directly in a browser) |
| pytest HTML report | `reports/report.html` |
| Screenshots (per `-ScreenshotMode`) | `reports/screenshots/` (also attached to the Allure/pytest report) |
| Traces (per `-TraceMode`) | `reports/traces/` |
| Videos (per `-VideoMode`) | `reports/videos/` |

## Exit codes

The runner exits with pytest's exit code, so it can be used in CI:

| Code | Meaning |
|---|---|
| 0 | All tests passed |
| 1 | Tests failed |
| 2 | Interrupted by the user |
| 3 | Internal error |
| 4 | Usage error |
| 5 | No tests collected |

"""
Enterprise test configuration.

Provides:
  - Session/function scoped async browser fixtures (Playwright + pytest-asyncio)
  - Per-test video recording, tracing and failure screenshots
  - Automatic attachment of artifacts to the pytest-html report and Allure
  - Automatic generation of the Allure HTML report after the run
"""
import os
import shutil
import subprocess
import threading
import uuid
from datetime import datetime
from pathlib import Path

import allure
import pytest

from config.settings import settings

ROOT_DIR = Path(__file__).resolve().parent

#: Plugins whose fixtures (auth sessions, page/API object collections, user
#: factory) should be shared by every test suite without per-suite duplication.
pytest_plugins = ("auth.fixtures",)

REPORTS_DIR = ROOT_DIR / settings.REPORTS_DIR
SCREENSHOT_DIR = ROOT_DIR / settings.SCREENSHOT_DIR
TRACE_DIR = ROOT_DIR / settings.TRACE_DIR
VIDEO_DIR = ROOT_DIR / settings.VIDEO_DIR
ALLURE_RESULTS_DIR = ROOT_DIR / settings.ALLURE_RESULTS_DIR
ALLURE_REPORT_DIR = ROOT_DIR / settings.ALLURE_REPORT_DIR
HTML_REPORT_FILE = REPORTS_DIR / settings.HTML_REPORT_FILE

#: Valid values for --trace / --video / --screenshot artifact modes.
_ARTIFACT_MODES = ("only-on-failure", "on", "off", "on-first-retry", "on-all-retries", "on-success")


# --------------------------------------------------------------------------- #
# Directory helpers
# --------------------------------------------------------------------------- #
def _ensure_dirs() -> None:
    for directory in (REPORTS_DIR, SCREENSHOT_DIR, TRACE_DIR, VIDEO_DIR, ALLURE_RESULTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def _cleanup_dirs() -> None:
    for directory in (SCREENSHOT_DIR, TRACE_DIR, VIDEO_DIR):
        shutil.rmtree(directory, ignore_errors=True)
    shutil.rmtree(ALLURE_RESULTS_DIR, ignore_errors=True)
    shutil.rmtree(ALLURE_REPORT_DIR, ignore_errors=True)
    if HTML_REPORT_FILE.exists():
        HTML_REPORT_FILE.unlink()


def _unique_name(prefix: str) -> str:
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"


def _rel_to_reports(path: str) -> str:
    return os.path.relpath(path, start=REPORTS_DIR)


# --------------------------------------------------------------------------- #
# Excel results reporting (testcaseName / testCaseStatus)
# --------------------------------------------------------------------------- #
_EXCEL_RESULTS: dict[str, dict[str, str]] = {}
_EXCEL_LOCK = threading.Lock()
_PYTEST_CONFIG = None

#: Phase outcomes that mean the test did not pass.
_FAILED_OUTCOMES = ("failed", "error")


def _excel_status(outcome: str) -> str:
    return {
        "passed": "PASS",
        "failed": "FAIL",
        "error": "FAIL",
        "skipped": "SKIP",
    }.get(outcome, outcome.upper())


def _final_outcome(phases: dict[str, str]) -> str:
    """Derive the test's final outcome from its setup/call/teardown phases.

    The last report received per phase is the final attempt (intermediate
    rerun attempts are reported with outcome ``rerun`` and are overwritten).
    A failure/error in any phase fails the test.
    """
    for phase in ("setup", "call", "teardown"):
        if phases.get(phase) in _FAILED_OUTCOMES:
            return "failed"
    if "skipped" in phases.values():
        return "skipped"
    return "passed"


def _record_excel_result(nodeid: str, phase: str, outcome: str) -> None:
    """Collect a finished test case on the controller process only.

    With pytest-xdist the worker processes run the tests; their reports are
    forwarded to and collected by the controller (which has no ``workerinput``).
    A single-process run has no ``workerinput`` either, so it records locally.

    Reports arrive per phase (setup / call / teardown) and per attempt; only
    the last outcome per phase is kept so reruns resolve to the final result.
    """
    if _PYTEST_CONFIG is not None and hasattr(_PYTEST_CONFIG, "workerinput"):
        return
    if outcome == "rerun":
        return
    with _EXCEL_LOCK:
        phases = _EXCEL_RESULTS.setdefault(nodeid, {})
        phases[phase] = outcome


def _write_excel_report() -> None:
    """Write all recorded test results to an Excel workbook (sheet 'Report')."""
    from openpyxl import Workbook

    path = ROOT_DIR / settings.EXCEL_REPORT_FILE
    path.parent.mkdir(parents=True, exist_ok=True)

    with _EXCEL_LOCK:
        results = [
            (nodeid, _final_outcome(phases))
            for nodeid, phases in _EXCEL_RESULTS.items()
        ]
    results.sort(key=lambda item: item[0])

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Report"
    worksheet.append(["testcaseName", "testCaseStatus"])
    for nodeid, outcome in results:
        worksheet.append([nodeid, _excel_status(outcome)])

    workbook.save(str(path))
    passed = sum(1 for _, o in results if o == "passed")
    failed = sum(1 for _, o in results if o == "failed")
    skipped = sum(1 for _, o in results if o == "skipped")
    print(f"[excel] {len(results)} test cases written to {path} "
          f"(PASS={passed}, FAIL={failed}, SKIP={skipped})")


# --------------------------------------------------------------------------- #
# Ad blocking
# --------------------------------------------------------------------------- #
AD_BLOCK_HOSTS = (
    "doubleclick.net",
    "googlesyndication.com",
    "googleadservices.com",
    "adservice.google.com",
    "amazon-adsystem.com",
    "adnxs.com",
    "adsystem.com",
    "criteo.com",
    "taboola.com",
    "outbrain.com",
    "moatads.com",
    "scorecardresearch.com",
    "pubmatic.com",
    "openx.net",
    "rubiconproject.com",
)


async def _block_ad_requests(route) -> None:
    """Abort requests to known ad/tracker hosts so overlay iframes never load."""
    if any(host in route.request.url for host in AD_BLOCK_HOSTS):
        await route.abort()
    else:
        await route.continue_()


async def _install_ad_blocker(context) -> None:
    await context.route("**/*", _block_ad_requests)


# --------------------------------------------------------------------------- #
# Command-line options
# --------------------------------------------------------------------------- #
def pytest_addoption(parser):
    existing = set()
    for group in [parser._anonymous] + list(getattr(parser, "_groups", []) or []):
        for action in group.options:
            existing.update(action.names())

    def addoption(name, **kwargs):
        if name not in existing:
            parser.addoption(name, **kwargs)

    addoption(
        "--browser",
        action="append",
        choices=["chromium", "chrome", "firefox", "webkit"],
        default=None,
        metavar="BROWSER",
        help="Browser(s) to run tests on (repeatable: --browser chromium "
             "--browser firefox). Overrides BROWSER env var.",
    )
    addoption(
        "--device",
        action="append",
        default=None,
        metavar="DEVICE",
        help="Device emulation (repeatable): a Playwright device name (e.g. "
             "'iPhone 12', 'Pixel 5') or a preset: desktop / tablet / mobile.",
    )
    addoption(
        "--viewport",
        default=None,
        help="Custom viewport size as WxH, e.g. '1024x768'. Ignored when --device is set.",
    )
    addoption(
        "--headed",
        action="store_true",
        default=None,
        help="Run in headed mode (overrides HEADLESS env var).",
    )
    addoption(
        "--headless",
        action="store_true",
        default=None,
        help="Run in headless mode (overrides HEADLESS env var).",
    )
    addoption(
        "--no-maximized",
        action="store_true",
        default=None,
        help="Do not maximize the window; use the default 1280x720 viewport.",
    )

    addoption(
        "--trace-mode",
        choices=_ARTIFACT_MODES,
        default=None,
        help="When to record a Playwright trace: on / off / only-on-failure / "
             "on-first-retry / on-all-retries / on-success. "
             "Default: RECORD_TRACE env (on/off).",
    )
    addoption(
        "--video",
        choices=_ARTIFACT_MODES,
        default=None,
        help="When to record a video: on / off / only-on-failure / "
             "on-first-retry / on-all-retries / on-success. "
             "Default: RECORD_VIDEO env (on/off).",
    )
    addoption(
        "--screenshot",
        choices=_ARTIFACT_MODES,
        default=None,
        help="When to take a failure/result screenshot: on / off / only-on-failure / "
             "on-first-retry / on-all-retries / on-success. Default: only-on-failure.",
    )


def _screen_size() -> tuple[int, int]:
    """Primary screen resolution; used for maximized viewport on non-Chromium."""
    try:
        import ctypes
        user32 = ctypes.windll.user32
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    except Exception:
        return 1280, 720


def _should_maximize(request) -> bool:
    """True when the window should be maximized (default), unless a custom
    device / viewport is requested or --no-maximized is passed."""
    if request.config.getoption("--device") or request.config.getoption("--viewport"):
        return False
    return not request.config.getoption("--no-maximized")


def _requested_browsers(config) -> list[str]:
    """All browser engines requested on the CLI (--browser is repeatable)."""
    names = config.getoption("--browser") or [settings.BROWSER]
    if isinstance(names, str):
        names = [names]
    return ["chromium" if n.lower() == "chrome" else n.lower() for n in names]


def _requested_devices(config) -> list[str | None]:
    """All devices requested on the CLI (--device is repeatable), or [None]."""
    devices = config.getoption("--device")
    if not devices:
        return [None]
    if isinstance(devices, str):
        devices = [devices]
    return list(devices)


# --------------------------------------------------------------------------- #
# Artifact modes (--trace / --video / --screenshot)
# --------------------------------------------------------------------------- #
def _artifact_mode(config, option: str, env_var: str, default: str) -> str:
    """Resolve the effective artifact mode: CLI option > env var > default.

    Env vars historically hold a boolean (RECORD_TRACE=true/false); those map
    to on/off. Any valid mode string is passed through unchanged.
    """
    from_config = config.getoption(f"--{option}")
    if from_config is not None:
        return from_config
    env = os.getenv(env_var)
    if env:
        e = env.strip().lower()
        if e in ("1", "true", "yes", "y"):
            return "on"
        if e in ("0", "false", "no"):
            return "off"
        if e in _ARTIFACT_MODES:
            return e
    return default


def _call_failed(item) -> bool:
    """True when the test's call phase failed (ignores teardown-phase outcome)."""
    call_report = getattr(item, "_rep_call", None)
    return bool(call_report and call_report.failed)


def _attempt_number(item) -> int:
    """Which run of the test this is: 1 = first, 2 = first retry, etc.
    Provided by pytest-rerunfailures via item.execution_count."""
    return int(getattr(item, "execution_count", 1))


def _keep_artifact(mode: str, item) -> bool:
    """Decide whether an artifact captured during this attempt should be kept.

    Retry-aware modes use item.execution_count (first attempt == 1).
    """
    if mode == "on":
        return True
    if mode == "off":
        return False
    if mode == "only-on-failure":
        return _call_failed(item)
    if mode == "on-success":
        return not _call_failed(item)
    if mode == "on-first-retry":
        return _attempt_number(item) == 2
    if mode == "on-all-retries":
        return _attempt_number(item) > 1
    return True


def pytest_generate_tests(metafunc) -> None:
    """Parametrize UI tests over every requested browser and device
    (--browser a --browser b --device x --device y => cross product)."""
    if "browser_name" in metafunc.fixturenames:
        browsers = _requested_browsers(metafunc.config)
        metafunc.parametrize("browser_name", browsers, ids=browsers, scope="session")
    if "device_name" in metafunc.fixturenames:
        devices = _requested_devices(metafunc.config)
        metafunc.parametrize(
            "device_name", devices,
            ids=[d or "default" for d in devices], scope="session",
        )


# --------------------------------------------------------------------------- #
# Session hooks
# --------------------------------------------------------------------------- #
def pytest_configure(config):
    # BasePage.goto() reads BASE_URL from the environment; expose settings to it.
    global _PYTEST_CONFIG
    _PYTEST_CONFIG = config
    os.environ.setdefault("BASE_URL", settings.BASE_URL)
    os.environ.setdefault("API_BASE_URL", settings.API_BASE_URL)
    _ensure_dirs()


def _is_xdist_worker(config) -> bool:
    """True when running under pytest-xdist as a worker (not the controller)."""
    return hasattr(config, "workerinput")


def pytest_sessionstart(session):
    """Start every run from a clean slate to avoid stale artifacts."""
    if _is_xdist_worker(session.config):
        return
    _cleanup_dirs()
    _ensure_dirs()


def pytest_sessionfinish(session, exitstatus):
    """Generate the Allure HTML report from the collected results."""
    if _is_xdist_worker(session.config):
        return
    _write_excel_report()
    if settings.GENERATE_ALLURE_REPORT and ALLURE_RESULTS_DIR.exists():
        try:
            import shutil
            allure_cmd = shutil.which("allure") or shutil.which("allure.cmd") or "allure"
            subprocess.run(
                [allure_cmd, "generate", str(ALLURE_RESULTS_DIR),
                 "-o", str(ALLURE_REPORT_DIR), "--clean", "--single-file"],
                check=False,
                capture_output=True,
                text=True,
            )
        except Exception as exc:  # pragma: no cover
            print(f"[allure] Could not generate report: {exc}")


# --------------------------------------------------------------------------- #
# Browser fixtures (async)
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="session")
async def playwright():
    """Async Playwright driver, shared for the whole session."""
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        yield p


@pytest.fixture(scope="session")
async def browser(browser_name, playwright, request):
    """Session-scoped async browser instance (one per requested engine)."""
    browser_type = getattr(playwright, browser_name)

    headless = settings.HEADLESS
    if request.config.getoption("--headed"):
        headless = False
    if request.config.getoption("--headless"):
        headless = True

    launch_kwargs = {"headless": headless}
    if browser_name == "chromium" and _should_maximize(request):
        launch_kwargs["args"] = ["--start-maximized"]

    browser = await browser_type.launch(**launch_kwargs)
    yield browser
    await browser.close()


@pytest.fixture
async def context(browser, browser_name, device_name, playwright, request):
    """Function-scoped browser context; trace/video capture is mode-controlled.

    Modes (--trace / --video): on, off, only-on-failure, on-first-retry,
    on-all-retries, on-success. Recording starts whenever the mode is not
    'off'; whether the artifact is kept is decided at teardown.

    Sizing is resolved as:
      --device <preset|device name>  >  --viewport WxH  >  maximized (default)  >  1280x720.
    """
    trace_mode = _artifact_mode(request.config, "trace-mode", "RECORD_TRACE", "off")
    video_mode = _artifact_mode(request.config, "video", "RECORD_VIDEO", "off")

    context_kwargs = {"accept_downloads": True}

    device = device_name
    viewport_arg = request.config.getoption("--viewport")

    if device:
        presets = {
            "desktop": {"width": 1280, "height": 720},
            "tablet": {"width": 768, "height": 1024},
            "mobile": {"width": 390, "height": 844},
        }
        preset = presets.get(device.lower())
        if preset:
            context_kwargs["viewport"] = preset
        else:
            descriptor = playwright.devices.get(device)
            if not descriptor:
                raise ValueError(
                    f"Unknown device '{device}'. Use a preset (desktop/tablet/mobile) "
                    f"or a Playwright device name e.g. {', '.join(list(playwright.devices)[:5])}...'"
                )
            context_kwargs.update(descriptor)
    elif viewport_arg:
        width, height = viewport_arg.lower().split("x")
        context_kwargs["viewport"] = {"width": int(width), "height": int(height)}
    elif _should_maximize(request) and browser_name == "chromium":
        context_kwargs["no_viewport"] = True
    elif _should_maximize(request):
        width, height = _screen_size()
        context_kwargs["viewport"] = {"width": width, "height": height}
    else:
        context_kwargs["viewport"] = {"width": 1280, "height": 720}

    if video_mode != "off":
        context_kwargs["record_video_dir"] = str(VIDEO_DIR)
        context_kwargs["record_video_size"] = {"width": 1280, "height": 720}

    context = await browser.new_context(**context_kwargs)
    if settings.BLOCK_ADS:
        await _install_ad_blocker(context)
    if trace_mode != "off":
        await context.tracing.start(screenshots=True, snapshots=True, sources=True)
    request.node._artifacts = {}
    request.node._video_path = None
    yield context

    if trace_mode != "off":
        try:
            if _keep_artifact(trace_mode, request.node):
                trace_path = TRACE_DIR / f"{_unique_name(request.node.name)}.zip"
                await context.tracing.stop(path=str(trace_path))
                request.node._artifacts["trace"] = str(trace_path)
            else:
                await context.tracing.stop()
        except Exception:
            pass

    try:
        await context.close()
    except Exception:
        pass

    if video_mode != "off" and request.node._video_path:
        if _keep_artifact(video_mode, request.node):
            request.node._artifacts["video"] = request.node._video_path
        else:
            try:
                Path(request.node._video_path).unlink(missing_ok=True)
            except Exception:
                pass


@pytest.fixture
async def page(context, request):
    """Function-scoped page; captures screenshots per --screenshot mode."""
    page = await context.new_page()
    page.set_default_timeout(settings.TIMEOUT)
    page.set_default_navigation_timeout(settings.PAGE_LOAD_TIMEOUT)
    yield page

    screenshot_mode = _artifact_mode(request.config, "screenshot", "SCREENSHOT_MODE", "only-on-failure")
    if screenshot_mode != "off" and _keep_artifact(screenshot_mode, request.node):
        screenshot_path = SCREENSHOT_DIR / f"{_unique_name(request.node.name)}.png"
        try:
            await page.screenshot(path=str(screenshot_path), full_page=True)
            request.node._artifacts["screenshot"] = str(screenshot_path)
        except Exception:
            pass

    if page.video is not None:
        try:
            request.node._video_path = await page.video.path()
        except Exception:
            pass

    try:
        await page.close()
    except Exception:
        pass


@pytest.fixture(scope="session")
async def api_request_context(playwright):
    """Session-scoped API request context for the automationexercise.com REST API."""
    request_ctx = await playwright.request.new_context(
        base_url=settings.API_BASE_URL,
        extra_http_headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    yield request_ctx
    await request_ctx.dispose()


# --------------------------------------------------------------------------- #
# Reporting hooks: attach artifacts to HTML report and Allure
# --------------------------------------------------------------------------- #
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"_rep_{report.when}", report)
    if report.when == "teardown":
        artifacts = getattr(item, "_artifacts", {})
        if artifacts:
            _attach_artifacts(item, report, artifacts)


@pytest.hookimpl(trylast=True)
def pytest_runtest_logreport(report) -> None:
    """Record each finished test case for the Excel report.

    Works under pytest-xdist too: worker results are forwarded to the
    controller, which aggregates them before ``pytest_sessionfinish``.
    """
    if _PYTEST_CONFIG is not None and hasattr(_PYTEST_CONFIG, "workerinput"):
        return
    _record_excel_result(report.nodeid, report.when, report.outcome)


def _attach_artifacts(item, report, artifacts: dict) -> None:
    try:
        import pytest_html
        from pytest_html import extras
        html_available = True
    except Exception:
        html_available = False

    # Artifacts were already filtered by their capture mode (e.g. only
    # on-failure screenshots are produced), so everything present is attached.
    for kind, path in artifacts.items():
        if not path or not Path(path).exists():
            continue

        if html_available and getattr(report, "extra", None) is None:
            report.extra = []

        if kind == "screenshot":
            if html_available:
                report.extra.append(extras.image(path, "Failure screenshot"))
            allure.attach.file(
                path, name="Failure screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
        elif kind == "trace":
            if html_available:
                report.extra.append(extras.html(
                    f'<a href="{_rel_to_reports(path)}">Download Playwright trace</a>'))
            allure.attach.file(
                path, name="Playwright trace",
                attachment_type=allure.attachment_type.ZIP,
            )
        elif kind == "video":
            if html_available:
                report.extra.append(extras.html(
                    f'<a href="{_rel_to_reports(path)}">Download test video</a>'))
            allure.attach.file(
                path, name="Test video",
                attachment_type=allure.attachment_type.WEBM,
            )

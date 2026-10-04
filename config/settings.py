import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


class Settings:
    """Application settings loaded from environment variables."""

    # Timeouts
    TIMEOUT = int(os.getenv("TIMEOUT", 30000))
    PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", 60000))
    SHORT_TIMEOUT = int(os.getenv("SHORT_TIMEOUT", 5000))

    # Application URLs
    BASE_URL = os.getenv("BASE_URL", "https://automationexercise.com")
    API_BASE_URL = os.getenv("API_BASE_URL", "https://automationexercise.com")

    # Browser settings
    HEADLESS = os.getenv("HEADLESS", "true").lower() == "false"
    BROWSER = os.getenv("BROWSER", "webkit").lower()
    PAGE_WAIT_UNTIL = os.getenv("PAGE_WAIT_UNTIL", "domcontentloaded")
    RECORD_TRACE = os.getenv("RECORD_TRACE", "false").lower() == "true"
    RECORD_VIDEO = os.getenv("RECORD_VIDEO", "false").lower() == "true"
    BLOCK_ADS = os.getenv("BLOCK_ADS", "true").lower() == "true"

    # Parallel settings
    WORKERS = int(os.getenv("WORKERS", 4))

    # Reporting: HTML report
    REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")
    HTML_REPORT_DIR = os.getenv("HTML_REPORT_DIR", "reports")
    HTML_REPORT_FILE = os.getenv("HTML_REPORT_FILE", "report.html")

    # Reporting: Artifacts (traces / screenshots / videos)
    SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "reports/screenshots")
    TRACE_DIR = os.getenv("TRACE_DIR", "reports/traces")
    VIDEO_DIR = os.getenv("VIDEO_DIR", "reports/videos")

    # Reporting: Excel results (testcaseName / testCaseStatus)
    EXCEL_REPORT_FILE = os.getenv("EXCEL_REPORT_FILE", "reports/test_results.xlsx")

    # Reporting: Allure
    ALLURE_RESULTS_DIR = os.getenv("ALLURE_RESULTS_DIR", "allure_reports/results")
    ALLURE_REPORT_DIR = os.getenv("ALLURE_REPORT_DIR", "allure_reports/html")

    # Artifact behaviour
    ATTACH_ALL_ARTIFACTS = os.getenv("ATTACH_ALL_ARTIFACTS", "true").lower() == "true"
    GENERATE_ALLURE_REPORT = os.getenv("GENERATE_ALLURE_REPORT", "true").lower() == "true"

    # Test data
    CONTACT_FILE = os.getenv("CONTACT_FILE", "test_data/upload.txt")


settings = Settings()

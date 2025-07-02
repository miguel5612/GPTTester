from playwright.sync_api import sync_playwright


def test_chrome_navigates_example():
    """Simple Playwright example using Chromium headless browser."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://example.com", wait_until="networkidle")
        assert "Example Domain" in page.title()
        browser.close()

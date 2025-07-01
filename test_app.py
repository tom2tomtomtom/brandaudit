import re
from playwright.sync_api import Page, expect

def test_homepage_loads(page: Page):
    page.goto("file:///Users/thomasdowuona-hyde/brand-audit-app/frontend/dist/index.html")
    expect(page).to_have_title(re.compile("AI Brand Audit Tool"))

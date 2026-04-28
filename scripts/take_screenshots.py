import asyncio
from playwright.async_api import async_playwright

BASE = "http://127.0.0.1:8765"
OUT = "docs/screenshots"
TABS = [
    ("home", "01_dashboard.png"),
    ("upload", "02_upload.png"),
    ("query", "03_query.png"),
    ("documents", "04_knowledge_base.png"),
    ("overview", "05_overview.png"),
    ("architecture", "06_architecture.png"),
    ("settings", "07_settings.png"),
]


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        await page.goto(BASE, wait_until="networkidle")
        await page.wait_for_timeout(2000)

        for tab_id, filename in TABS:
            await page.evaluate(f"showTab('{tab_id}')")
            await page.wait_for_timeout(800)
            await page.screenshot(path=f"{OUT}/{filename}", full_page=False)
            print(f"  Captured {filename}")

        await browser.close()
    print(f"\nAll {len(TABS)} screenshots saved to {OUT}/")


asyncio.run(main())

import asyncio
from playwright.async_api import async_playwright


async def _search(query: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.google.com")
        await page.fill("textarea[name=q]", query)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(2000)
        titles = await page.eval_on_selector_all("h3", "els => els.slice(0,3).map(e=>e.textContent)")
        await browser.close()
        return " | ".join(titles) if titles else "No results."


def handle_web(prompt: str) -> str:
    lower = prompt.lower()
    if "search" in lower or "google" in lower:
        q = lower.replace("search", "").replace("google", "").strip() or "news"
        try:
            return asyncio.run(_search(q))
        except Exception as exc:
            return f"Web automation failed: {exc}"
    return ""

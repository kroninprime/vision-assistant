import asyncio
from playwright.async_api import async_playwright
from app.main import assistant


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


def web_skill(prompt: str) -> str:
    q = prompt.lower().replace("search", "").replace("google", "").strip()
    try:
        result = asyncio.run(_search(q or "news"))
        return f"Top results: {result}"
    except Exception as exc:
        return f"Web automation failed: {exc}"


assistant.register("web", ["search", "google", "book", "ticket"], web_skill)

import asyncio
from playwright.async_api import async_playwright
import json

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        print("Navigating to Amul...")
        await page.goto('https://shop.amul.com/en/product/amul-high-protein-plain-lassi-200-ml-or-pack-of-30', wait_until="networkidle")
        
        # force click pincode_wrap
        await page.locator(".pincode_wrap").first.click()
        await page.wait_for_timeout(2000)
        
        await page.fill('#search', '486001')
        item = page.locator('p:has-text("486001")').first
        await item.wait_for(timeout=5000)
        await item.click()
        await page.wait_for_timeout(3000)
        
        cookies = await page.context.cookies()
        print("Cookies after setting pincode:")
        for c in cookies:
            print(f"{c['name']}: {c['value']}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())

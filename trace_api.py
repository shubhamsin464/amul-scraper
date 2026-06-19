import asyncio
from playwright.async_api import async_playwright
import urllib.parse

async def main():
    url = "https://shop.amul.com/en/product/amul-high-protein-plain-lassi-200-ml-or-pack-of-30"
    pincode = "486001"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Intercept and log requests
        page.on("request", lambda request: print(f"> {request.method} {request.url}") if "api" in request.url or "graphql" in request.url or "storehippo" in request.url or "availability" in request.url or "pincode" in request.url else None)
        
        print(f"Navigating to {url}")
        await page.goto(url, wait_until="networkidle")
        
        print("Filling pincode")
        await page.fill("#search", pincode)
        dropdown_item = page.locator(f"p:has-text('{pincode}')").first
        await dropdown_item.wait_for(state="visible", timeout=5000)
        await dropdown_item.click()
        
        await page.wait_for_timeout(3000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

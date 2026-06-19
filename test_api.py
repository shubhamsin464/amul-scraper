import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    url = "https://shop.amul.com/en/product/amul-high-protein-plain-lassi-200-ml-or-pack-of-30"
    api_url = 'https://shop.amul.com/api/1/entity/ms.products?q={"alias":"amul-high-protein-plain-lassi-200-ml-or-pack-of-30"}&limit=1'
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("Navigating to Amul to get cookies/tokens...")
        await page.goto(url, wait_until="domcontentloaded")
        
        print("Fetching API directly...")
        response = await context.request.get(api_url)
        data = await response.json()
        print("API Response:")
        print(json.dumps(data, indent=2)[:500])
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

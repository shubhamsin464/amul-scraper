import asyncio
from playwright.async_api import async_playwright

async def main():
    url = "https://shop.amul.com/en/product/amul-high-protein-rose-lassi-200-ml-or-pack-of-30"
    pincode = "486001"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print(f"Navigating to {url}")
        await page.goto(url, wait_until="networkidle")
        
        print("Filling pincode")
        await page.fill("#search", pincode)
        dropdown_item = page.locator(f"p:has-text('{pincode}')").first
        await dropdown_item.wait_for(state="visible", timeout=5000)
        await dropdown_item.click()
        
        await page.wait_for_timeout(5000)
        
        html = await page.content()
        with open("debug_html.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

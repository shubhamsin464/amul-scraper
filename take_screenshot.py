import asyncio
from playwright.async_api import async_playwright

async def main():
    url = "https://shop.amul.com/en/product/amul-kool-protein-milkshake-or-chocolate-180-ml-or-pack-of-8"
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
        
        await page.wait_for_timeout(3000)
        
        add_btn = page.locator(".add-to-cart").first
        html = await add_btn.evaluate("el => el.outerHTML")
        print("OUTER HTML IS:")
        print(html)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

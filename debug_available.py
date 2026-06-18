import asyncio
from playwright.async_api import async_playwright

async def main():
    urls = [
        "https://shop.amul.com/en/product/amul-high-protein-plain-lassi-200-ml-or-pack-of-30",
        "https://shop.amul.com/en/product/amul-high-protein-rose-lassi-200-ml-or-pack-of-30",
        "https://shop.amul.com/en/product/amul-kool-protein-milkshake-or-chocolate-180-ml-or-pack-of-8"
    ]
    pincode = "486001"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        for url in urls:
            print(f"\nChecking: {url}")
            await page.goto(url, wait_until="networkidle")
            
            await page.fill("#search", pincode)
            try:
                dropdown_item = page.locator(f"p:has-text('{pincode}')").first
                await dropdown_item.wait_for(state="visible", timeout=5000)
                await dropdown_item.click()
            except:
                print("Could not select pincode")
                continue
            
            await page.wait_for_timeout(3000)
            
            try:
                add_btn = page.locator(".add-to-cart").first
                is_disabled = await add_btn.evaluate("el => el.hasAttribute('disabled') || el.classList.contains('disabled')")
                text = await add_btn.inner_text()
                print(f"Is disabled? {is_disabled}")
            except Exception as e:
                print(f"Error checking button: {e}")
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

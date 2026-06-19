import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        url = 'https://shop.amul.com/en/product/amul-kool-protein-milkshake-or-chocolate-180-ml-or-pack-of-8'
        print(f"Navigating to {url}")
        await page.goto(url, wait_until="networkidle")
        
        # open location modal
        await page.locator(".pincode_wrap").first.click()
        await page.wait_for_timeout(2000)
        
        await page.fill('#search', '486001')
        item = page.locator('p:has-text("486001")').first
        await item.wait_for(timeout=5000)
        await item.click()
        await page.wait_for_timeout(3000)
        
        await page.screenshot(path="milkshake_486001.png")
        print("Screenshot saved to milkshake_486001.png")
        
        add_btn = page.locator(".add-to-cart").first
        if await add_btn.is_visible():
            html = await add_btn.evaluate("el => el.outerHTML")
            print("Button HTML:")
            print(html)
        else:
            print("Add to cart button not visible.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())

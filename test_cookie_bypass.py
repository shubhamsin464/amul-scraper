import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 1920x1080 viewport
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        
        # Pre-set the substore cookie for 486001
        await context.add_cookies([{
            'name': 'ms.substore',
            'value': 'madhya-pradesh',
            'domain': 'shop.amul.com',
            'path': '/'
        }])
        
        page = await context.new_page()
        
        url = 'https://shop.amul.com/en/product/amul-high-protein-plain-lassi-200-ml-or-pack-of-30'
        print(f"Navigating to {url}")
        await page.goto(url, wait_until="networkidle")
        
        # Check if the modal still pops up, or if we can see the stock directly!
        await page.wait_for_timeout(3000)
        add_btn = page.locator(".add-to-cart").first
        
        html = await add_btn.evaluate("el => el.outerHTML")
        print("Button HTML:")
        print(html)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())

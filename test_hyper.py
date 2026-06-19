import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Block images and CSS
        context = await browser.new_context()
        
        # Inject the substore cookie for Madhya Pradesh (486001)
        await context.add_cookies([{
            'name': 'ms.substore',
            'value': 'madhya-pradesh',
            'domain': 'shop.amul.com',
            'path': '/'
        }])
        
        page = await context.new_page()
        
        # Intercept and block unnecessary resources to save RAM
        async def route_intercept(route):
            if route.request.resource_type in ["image", "stylesheet", "font", "media"]:
                await route.abort()
            else:
                await route.continue_()
                
        await page.route("**/*", route_intercept)
        
        url = 'https://shop.amul.com/en/product/amul-kool-protein-milkshake-or-chocolate-180-ml-or-pack-of-8'
        print(f"Navigating to {url}")
        
        # Since we injected the cookie, we don't need to click anything! Just wait for the button.
        await page.goto(url, wait_until="domcontentloaded")
        
        try:
            add_btn = page.locator(".add-to-cart").first
            await add_btn.wait_for(state="attached", timeout=15000)
            
            html = await add_btn.evaluate("el => el.outerHTML")
            print("Button HTML found:")
            print(html)
            
            is_disabled = await add_btn.evaluate("el => el.classList.contains('disabled')")
            print(f"Is Disabled: {is_disabled}")
            
        except Exception as e:
            print("Failed to find button:", e)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())

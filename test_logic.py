import asyncio
from playwright.async_api import async_playwright

async def test_url(url, pincode):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print(f"\n--- Checking: {url} ---")
        
        await page.goto(url, wait_until="networkidle")
        
        print("Filling pincode")
        await page.fill("#search", pincode)
        dropdown_item = page.locator(f"p:has-text('{pincode}')").first
        await dropdown_item.wait_for(state="visible", timeout=5000)
        await dropdown_item.click()
        
        await page.wait_for_timeout(2000)
        add_btn = page.locator(".add-to-cart").first
        await add_btn.wait_for(state="visible", timeout=10000)
        
        is_disabled = await add_btn.evaluate("el => el.getAttribute('disabled') === 'true' || el.classList.contains('disabled')")
        html = await add_btn.evaluate("el => el.outerHTML")
        print(f"Is disabled logic returned: {is_disabled}")
        print(f"Outer HTML: {html}")
        
        await browser.close()

async def main():
    urls = [
        "https://shop.amul.com/en/product/amul-high-protein-plain-lassi-200-ml-or-pack-of-30",
        "https://shop.amul.com/en/product/amul-high-protein-rose-lassi-200-ml-or-pack-of-30",
        "https://shop.amul.com/en/product/amul-kool-protein-milkshake-or-chocolate-180-ml-or-pack-of-8"
    ]
    pincode = "486001"
    
    for url in urls:
        await test_url(url, pincode)

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from playwright.async_api import async_playwright

async def main():
    url = "https://shop.amul.com/en/product/amul-high-protein-plain-lassi-200-ml-or-pack-of-30"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto(url, wait_until="networkidle")
        
        # Find all elements that trigger the location modal
        trigger_html = await page.evaluate('''() => {
            const el = document.querySelector('[data-bs-target="#locationWidgetModal"]');
            return el ? el.outerHTML : "Not found";
        }''')
        
        print("Trigger HTML:")
        print(trigger_html)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

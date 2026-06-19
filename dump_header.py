import asyncio
from playwright.async_api import async_playwright

async def main():
    url = "https://shop.amul.com/en/product/amul-high-protein-plain-lassi-200-ml-or-pack-of-30"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto(url, wait_until="networkidle")
        
        header_html = await page.evaluate('''() => {
            const header = document.querySelector('header');
            return header ? header.outerHTML : "No header";
        }''')
        
        with open("header_dump.html", "w", encoding="utf-8") as f:
            f.write(header_html)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from playwright.async_api import async_playwright

async def main():
    url = "https://shop.amul.com/en/product/amul-high-protein-plain-lassi-200-ml-or-pack-of-30"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        def handle_request(request):
            if "api/1/entity/ms.products" in request.url:
                print(f"URL: {request.url}")
                print("HEADERS:")
                for k, v in request.headers.items():
                    print(f"  {k}: {v}")
                    
        page.on("request", handle_request)
        
        print(f"Navigating to {url}")
        await page.goto(url, wait_until="networkidle")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

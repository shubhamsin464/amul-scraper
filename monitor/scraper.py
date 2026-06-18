import asyncio
import logging
from playwright.async_api import async_playwright
from core.config import settings

logger = logging.getLogger(__name__)

async def check_availability(url: str, pincode: str) -> bool:
    """
    Navigates to the product URL, enters the pincode in the #search box, 
    selects it from the autocomplete dropdown, and checks the page text.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            logger.info(f"Navigating to {url}")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Handle the Autocomplete Pincode logic
            if pincode.lower() not in ["global", "any"]:
                try:
                    logger.info(f"Typing pincode {pincode} into #search")
                    await page.fill("#search", pincode, timeout=5000)
                    
                    # Wait for the specific autocomplete <p> tag to appear and click it
                    dropdown_item = page.locator(f"p:has-text('{pincode}')").first
                    await dropdown_item.wait_for(state="visible", timeout=5000)
                    await dropdown_item.click()
                    logger.info(f"Clicked autocomplete dropdown for {pincode}")
                except Exception as e:
                    logger.warning(f"Could not complete pincode entry for {pincode}. Error: {e}")
            
            # Wait briefly to ensure the page refreshes after selecting the pincode
            await page.wait_for_timeout(5000)
            
            # Read all visible text on the page
            page_text = await page.locator("body").inner_text()
            page_text_lower = page_text.lower()
            
            # Common out-of-stock phrases
            out_of_stock_phrases = ["out of stock", "sold out", "currently unavailable", "not available"]
            
            is_available = True
            for phrase in out_of_stock_phrases:
                if phrase in page_text_lower:
                    is_available = False
                    logger.info(f"Found negative phrase '{phrase}'. Product is UNAVAILABLE.")
                    break
            
            if is_available:
                logger.info("No negative phrases found. Product is assumed AVAILABLE.")
                
            return is_available

        except Exception as e:
            logger.error(f"Error checking availability for {url}: {e}")
            return False
        finally:
            await browser.close()

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
            
            # Instead of searching the whole page (which triggers false positives on 'Related Products'),
            # we directly check the main 'Add to Cart' button.
            try:
                # Wait briefly to ensure button state is updated
                await page.wait_for_timeout(2000)
                add_btn = page.locator(".add-to-cart").first
                await add_btn.wait_for(state="visible", timeout=10000)
                
                is_disabled = await add_btn.evaluate("el => el.hasAttribute('disabled') || el.classList.contains('disabled')")
                if is_disabled:
                    logger.info("Add to Cart button is disabled. Product is UNAVAILABLE.")
                    is_available = False
                else:
                    logger.info("Add to Cart button is active! Product is AVAILABLE.")
                    is_available = True
            except Exception as e:
                logger.warning(f"Could not find or check the Add to Cart button. Assuming UNAVAILABLE. Error: {e}")
                is_available = False

        except Exception as e:
            logger.error(f"Error checking availability for {url}: {e}")
            return False
        finally:
            await browser.close()

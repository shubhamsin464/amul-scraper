import asyncio
import logging
from playwright.async_api import async_playwright
from core.config import settings

logger = logging.getLogger(__name__)

async def route_intercept(route):
    if route.request.resource_type in ["image", "stylesheet", "font", "media"]:
        await route.abort()
    else:
        await route.continue_()

async def check_availability(url: str, pincode: str) -> bool:
    """
    Checks if an Amul product is available for a given pincode.
    Returns True if available, False otherwise.
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-dev-shm-usage", "--no-sandbox"] # Critical for low-RAM environments like Render
            )
            
            # Force desktop viewport to prevent elements hiding in mobile menus
            context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = await context.new_page()
            
            # Intercept and block heavy resources to save RAM
            await page.route("**/*", route_intercept)
            
            logger.info(f"Navigating to {url}")
            await page.goto(url, wait_until="domcontentloaded")
            
            try:
                logger.info("Opening location modal via JS injection")
                # Force click via JS to bypass Playwright visibility checks
                await page.evaluate('document.querySelector(".pincode_wrap").click()')
                await page.wait_for_timeout(1500)
                
                logger.info(f"Filling pincode: {pincode}")
                await page.fill('#search', pincode)
                
                logger.info("Waiting for pincode dropdown suggestion")
                await page.wait_for_selector(f'p:has-text("{pincode}")', timeout=15000)
                
                logger.info("Clicking pincode suggestion via JS injection")
                await page.evaluate(f'''
                    const el = Array.from(document.querySelectorAll("p")).find(e => e.textContent.includes("{pincode}"));
                    if (el) el.click();
                ''')
                
                # Wait for the page to refresh/update stock status
                await page.wait_for_timeout(4000)
                
            except Exception as e:
                logger.error(f"UI interaction failed (modal might be blocked or changed): {e}")
                # We do not return False immediately, we try to read the button anyway.
                
            # Check availability button
            try:
                add_btn = page.locator(".add-to-cart").first
                await add_btn.wait_for(timeout=15000)
                
                # Extremely resilient check: looking explicitly for "disabled" class or true disabled attribute
                is_disabled = await add_btn.evaluate("el => el.classList.contains('disabled') || el.getAttribute('disabled') === 'true'")
                
                if is_disabled:
                    logger.info(f"Product is UNAVAILABLE (button is disabled).")
                    return False
                else:
                    logger.info(f"Product is AVAILABLE (button is active).")
                    return True
                    
            except Exception as e:
                logger.warning(f"Add to Cart button not found, assuming unavailable. Error: {e}")
                return False
                
            finally:
                await browser.close()
                
    except Exception as e:
        logger.error(f"Fatal error checking availability: {e}")
        return False

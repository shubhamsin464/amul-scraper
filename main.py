import asyncio
import logging
import uvicorn
from datetime import datetime

from core import database
from core.config import settings
from core.notifier import send_whatsapp_alert, send_discord_alert
from web.main import app as fastapi_app
from monitor.scraper import check_availability

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_scraper_cycle():
    logger.info("Starting scraper cycle...")
    products = await database.get_products()
    pincodes = await database.get_pincodes()
    
    if not products or not pincodes:
        logger.info("No products or pincodes to check.")
        return

    # Check all product/pincode combinations sequentially to prevent OOM
    for product in products:
        for pincode in pincodes:
            await process_availability(product, pincode)
            # Wait a few seconds between checks to reduce CPU spikes and be polite
            await asyncio.sleep(2)
    logger.info("Scraper cycle complete.")

async def process_availability(product, pincode):
    try:
        is_available = await check_availability(product['url'], pincode['pincode'])
        
        # Update database state and check if it transitioned to Available
        became_available = await database.update_state(
            product_id=product['id'],
            pincode_id=pincode['id'],
            is_available=is_available
        )
        
        if became_available:
            logger.info(f"ALERT! {product['name']} is available at {pincode['pincode']}")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if settings.discord_webhook_url:
                await send_discord_alert(
                    product_name=product['name'],
                    product_url=product['url'],
                    pincode=pincode['pincode'],
                    timestamp=timestamp
                )
            elif settings.whatsapp_phone_number:
                await send_whatsapp_alert(
                    product_name=product['name'],
                    product_url=product['url'],
                    pincode=pincode['pincode'],
                    timestamp=timestamp
                )
    except Exception as e:
        logger.error(f"Error processing {product['name']} for {pincode['pincode']}: {e}")

async def scraper_loop():
    """Background task to run the scraper periodically."""
    while True:
        await run_scraper_cycle()
        await asyncio.sleep(settings.poll_interval_seconds)

async def start_web_server():
    """Run the FastAPI web server using Uvicorn programmatically."""
    config = uvicorn.Config(
        app=fastapi_app, 
        host="0.0.0.0", 
        port=settings.dashboard_port, 
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    logger.info("Initializing database...")
    await database.init_db()

    logger.info("Starting services...")
    
    # Run Scraper and Web Server concurrently
    await asyncio.gather(
        scraper_loop(),
        start_web_server()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped manually.")

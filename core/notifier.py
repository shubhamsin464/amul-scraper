import logging
import aiohttp
from core.config import settings

logger = logging.getLogger(__name__)

async def send_whatsapp_alert(product_name: str, product_url: str, pincode: str, timestamp: str):
    """
    Send an alert to the user's WhatsApp using the CallMeBot API.
    """
    phone = settings.whatsapp_phone_number
    apikey = settings.whatsapp_apikey

    if not phone or not apikey:
        logger.warning("WhatsApp Phone Number or API Key is missing. Cannot send alert.")
        return

    message = (
        f"🚨 *Product Available*\n"
        f"*Product:* {product_name}\n"
        f"*Pincode:* {pincode}\n"
        f"*Time:* {timestamp}\n"
        f"*Link:* {product_url}"
    )

    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={message}&apikey={apikey}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    logger.info("Successfully sent WhatsApp alert.")
                else:
                    logger.error(f"Failed to send WhatsApp alert. Status: {response.status}")
    except Exception as e:
        logger.error(f"Error while sending WhatsApp alert: {e}")

async def send_discord_alert(product_name: str, product_url: str, pincode: str, timestamp: str):
    """
    Send an alert to a Discord Webhook.
    """
    webhook_url = settings.discord_webhook_url
    if not webhook_url:
        logger.warning("Discord Webhook URL is missing. Cannot send alert.")
        return

    message = (
        f"🚨 **Product Available**\\n"
        f"**Product:** {product_name}\\n"
        f"**Pincode:** {pincode}\\n"
        f"**Time:** {timestamp}\\n"
        f"**Link:** {product_url}"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json={"content": message}) as response:
                if response.status in (200, 204):
                    logger.info("Successfully sent Discord alert.")
                else:
                    logger.error(f"Failed to send Discord alert. Status: {response.status}")
    except Exception as e:
        logger.error(f"Error while sending Discord alert: {e}")

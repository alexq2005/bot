import requests
import logging
from .config import settings

logger = logging.getLogger(__name__)

class TelegramService:
    """
    Sends real-time alerts to a Telegram User/Channel.
    """

    def __init__(self):
        self.token = settings.TELEGRAM_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.enabled = bool(self.token and self.chat_id)

        if self.enabled:
            logger.info("📱 Telegram Notifications: ENABLED")
        else:
            logger.info("🔕 Telegram Notifications: DISABLED (Missing Token/ChatID)")

    def send_alert(self, message: str):
        """Sends a message to the configured chat."""
        if not self.enabled:
            return

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(url, json=payload, timeout=5)
            response.raise_for_status()
            logger.debug("Telegram message sent successfully.")
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")

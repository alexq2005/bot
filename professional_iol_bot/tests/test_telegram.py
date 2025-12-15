import pytest
from unittest.mock import MagicMock, patch
from src.telegram_service import TelegramService

def test_telegram_disabled_by_default():
    with patch('src.telegram_service.settings') as mock_settings:
        mock_settings.TELEGRAM_TOKEN = None
        service = TelegramService()
        assert not service.enabled

def test_telegram_enabled_with_creds():
    with patch('src.telegram_service.settings') as mock_settings:
        mock_settings.TELEGRAM_TOKEN = "123:abc"
        mock_settings.TELEGRAM_CHAT_ID = "999"
        service = TelegramService()
        assert service.enabled

def test_send_alert_calls_api():
    with patch('src.telegram_service.settings') as mock_settings:
        mock_settings.TELEGRAM_TOKEN = "123:abc"
        mock_settings.TELEGRAM_CHAT_ID = "999"

        with patch('src.telegram_service.requests.post') as mock_post:
            service = TelegramService()
            service.send_alert("Test Message")

            mock_post.assert_called_once()
            assert mock_post.call_args[1]['json']['text'] == "Test Message"

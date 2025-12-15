import time
import logging
import sys
from datetime import datetime
from typing import Optional

from .config import settings
from .iol_client import IOLClient
from .strategy import TechnicalStrategy
from .database import init_db, get_db, Trade, LogEntry

# Configure Logging
logger = logging.getLogger("IOLBot")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class TradingBot:
    def __init__(self):
        logger.info("🤖 Initializing IOL Professional Bot")

        self.client = IOLClient()
        self.strategy = TechnicalStrategy()

        # Initialize Database
        init_db()

        self.running = False

    def run(self):
        """Main Bot Loop"""
        logger.info("🚀 Starting Bot Loop")
        self.running = True

        # Authentication
        if not self.client.authenticate():
            logger.critical("❌ Authentication Failed. Exiting.")
            return

        while self.running:
            try:
                self.process_cycle()

                # Sleep interval
                logger.info("💤 Sleeping for next cycle...")
                time.sleep(5) # Short sleep for demo purposes (real would be longer)

            except KeyboardInterrupt:
                logger.info("🛑 Bot stopped by user.")
                self.running = False
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                time.sleep(5) # Prevent rapid error loops

    def process_cycle(self):
        """Single execution cycle"""
        symbol = settings.TRADING_SYMBOL
        logger.info(f"🔍 Analyzing {symbol}...")

        # 1. Get Data
        history = self.client.get_historical_data(symbol)

        # 2. Analyze
        analysis = self.strategy.analyze(symbol, history)
        signal = analysis.get("signal")
        price = analysis.get("price")

        # 3. Execute
        if "BUY" in signal:
            self.execute_trade(symbol, "BUY", 10, price, signal)
        elif "SELL" in signal:
            self.execute_trade(symbol, "SELL", 10, price, signal)
        else:
            logger.info(f"⏸️ No Action: {signal}")

    def execute_trade(self, symbol: str, side: str, quantity: int, price: float, signal: str):
        """Executes and logs a trade"""
        logger.info(f"⚡ Executing {side} Order for {symbol}")

        success = self.client.place_order(symbol, side, quantity, price)

        if success:
            self.save_trade(symbol, side, quantity, price, signal)
            logger.info(f"✅ Trade Successful: {side} {quantity} {symbol}")

    def save_trade(self, symbol, side, quantity, price, signal):
        """Persists trade to DB"""
        try:
            with get_db() as db:
                trade = Trade(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    price=price,
                    strategy_signal=signal,
                    timestamp=datetime.utcnow()
                )
                db.add(trade)
                db.commit()
        except Exception as e:
            logger.error(f"Failed to save trade to DB: {e}")

if __name__ == "__main__":
    bot = TradingBot()
    bot.run()

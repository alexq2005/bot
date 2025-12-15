import time
import logging
import sys
from datetime import datetime
from typing import Optional

from .config import settings
from .iol_client import IOLClient
from .strategy import EvolutionaryStrategy
from .news_service import NewsService
from .ai_engine import AIEngine
from .ml_engine import MLEngine
from .risk_manager import RiskManager
from .reasoning_engine import ReasoningEngine
from .database import init_db, get_db, Trade, LogEntry, SentimentLog

# Configure Logging
logger = logging.getLogger("IOLBot")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class TradingBot:
    def __init__(self):
        logger.info("🤖 Initializing IOL Evolutionary Bot (SOTA v2.0)")

        self.client = IOLClient()
        self.news_service = NewsService()
        self.ai = AIEngine()

        # Advanced Modules
        self.ml_brain = MLEngine()
        self.risk_manager = RiskManager()
        self.reasoning = ReasoningEngine()
        self.strategy = EvolutionaryStrategy(self.ml_brain)

        # Initialize Database
        init_db()

        self.running = False

    def run(self):
        """Main Bot Loop"""
        logger.info("🚀 Starting Evolutionary Bot Loop")
        self.running = True

        # Initial Evolution (Retrain on startup)
        try:
            self.ml_brain.train_model()
        except Exception as e:
            logger.warning(f"Initial training skipped: {e}")

        # Authentication
        if not self.client.authenticate():
            logger.critical("❌ Authentication Failed. Exiting.")
            return

        while self.running:
            try:
                self.process_cycle()

                # Sleep interval
                logger.info("💤 Sleeping for next cycle...")
                time.sleep(60)

            except KeyboardInterrupt:
                logger.info("🛑 Bot stopped by user.")
                self.running = False
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                time.sleep(5) # Prevent rapid error loops

    def process_cycle(self):
        """Single execution cycle"""
        symbols = settings.TRADING_SYMBOLS
        logger.info(f"🔄 Starting Portfolio Cycle for {len(symbols)} assets: {symbols}")

        for symbol in symbols:
            try:
                self._process_symbol(symbol)
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")

    def _process_symbol(self, symbol: str):
        logger.info(f"🔍 Analyzing {symbol}...")

        # 1. Get Market Data (Technical)
        history = self.client.get_historical_data(symbol)

        # 2. Get AI Sentiment (Fundamental)
        logger.info(f"📰 Gathering Intelligence for {symbol}...")
        # Search for symbol + "Argentina Economy" to get broader context
        # Optimized query to reduce API spam if necessary
        news = self.news_service.get_news(query=f"{symbol} Argentina Economy")
        sentiment_score = self.ai.analyze_sentiment(news)

        # Log sentiment for future learning
        self._log_sentiment(symbol, news, sentiment_score)

        # 3. Calculate Volatility (Risk)
        atr = self.risk_manager.calculate_atr(history)

        # 4. Execute with Institutional Risk Management
        current_position = self.get_current_position(symbol)

        # 5. Evolutionary Analysis (Tech + AI + ML)
        # We pass current position to the RL Brain so it knows context (Hold vs Buy vs Sell)
        analysis = self.strategy.analyze(symbol, history, sentiment_score, atr, current_position)
        signal = analysis.get("signal")
        price = analysis.get("price")

        # 6. Reasoning Output
        self.reasoning.explain_decision(
            symbol,
            analysis['indicators']['rsi'],
            sentiment_score,
            analysis['indicators'].get('rl_action', 0),
            signal,
            atr,
            signal
        )

        if "BUY" in signal:
            if current_position == 0:
                # Dynamic Position Sizing
                quantity = self.risk_manager.calculate_position_size(symbol, price, atr)
                self.execute_trade(symbol, "BUY", quantity, price, signal)
            else:
                logger.info(f"⚠️ Signal BUY ignored: Already holding {symbol}")

        elif "SELL" in signal:
            if current_position > 0:
                # Sell all for simplicity in this version, or manage scaling out
                self.execute_trade(symbol, "SELL", current_position, price, signal)
            else:
                logger.info(f"⚠️ Signal SELL ignored: No position in {symbol}")

        else:
            logger.info(f"⏸️ No Action: {signal}")

    def get_current_position(self, symbol: str) -> int:
        """Calculates current position from DB history"""
        try:
            with get_db() as db:
                trades = db.query(Trade).filter(Trade.symbol == symbol).all()
                position = 0
                for t in trades:
                    if t.side == "BUY":
                        position += t.quantity
                    elif t.side == "SELL":
                        position -= t.quantity
                return position
        except Exception as e:
            logger.error(f"Failed to calculate position: {e}")
            return 0

    def _log_sentiment(self, symbol, news_items, score):
        """Logs sentiment data to DB for training"""
        import hashlib
        try:
            with get_db() as db:
                for item in news_items:
                    # Stable hash to avoid duplicates across restarts
                    title_hash = hashlib.sha256(item['title'].encode('utf-8')).hexdigest()
                    exists = db.query(SentimentLog).filter(SentimentLog.title_hash == title_hash).first()

                    if not exists:
                        log = SentimentLog(
                            symbol=symbol,
                            news_source=item['source'],
                            title_hash=title_hash,
                            sentiment_score=score # We attribute the daily score to each article for simplicity now
                        )
                        db.add(log)
                db.commit()
        except Exception as e:
            logger.error(f"Failed to log sentiment: {e}")

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

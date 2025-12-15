import logging
import joblib
import pandas as pd
import numpy as np
import os
from stable_baselines3 import PPO
from typing import Dict, List
from .database import get_db, Trade, SentimentLog
from .rl_agent import TradingEnv

logger = logging.getLogger(__name__)

class MLEngine:
    """
    Next-Gen AI Brain using Deep Reinforcement Learning (PPO).
    The agent learns optimal policies by simulating market interactions.
    """

    MODEL_PATH = "drl_agent.zip"

    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.MODEL_PATH):
            try:
                self.model = PPO.load(self.MODEL_PATH)
                logger.info("🧠 Loaded Deep RL Agent")
            except:
                logger.warning("Could not load RL Agent, starting fresh")
        else:
            logger.info("🆕 No RL Agent found. Waiting for training.")

    def predict_action(self, rsi: float, macd: float, sentiment: float, position_status: int) -> int:
        """
        Asks the RL Agent for the best action.
        Returns: 0 (Hold), 1 (Buy), 2 (Sell)
        """
        if not self.model:
            return 0 # Hold

        # Observation must match environment space: [Price(ignored here), RSI, MACD, Sentiment, PosStatus]
        # Note: Price is less relevant for the policy if we use normalized indicators,
        # but the env expects 5 values. We pass 0 for price as placeholder if we only care about relative indicators.
        obs = np.array([0.0, rsi, macd, sentiment, position_status], dtype=np.float32)

        try:
            action, _states = self.model.predict(obs, deterministic=True)
            logger.info(f"🤖 RL Agent chose action: {action}")
            return int(action)
        except Exception as e:
            logger.error(f"RL Prediction failed: {e}")
            return 0

    def train_model(self):
        """
        Evolutionary Step: Retrains the RL Agent using simulated environment.
        Uses deterministic patterns (Sine Wave) so the agent can actually learn logic.
        """
        logger.info("🎓 Starting Deep RL Training (Simulated Pattern)...")

        # 1. Create Deterministic Simulation Data (Sine Wave + Trend)
        # This allows the agent to learn "Buy Low, Sell High" logic reliably
        length = 1000
        x = np.linspace(0, 50, length)

        # Price = Upward Trend + Sine Wave + Noise
        price = 100 + x + 10 * np.sin(x) + np.random.normal(0, 2, length)

        # Generate Indicators based on this price (Semi-Realistic)
        rsi = 50 + 40 * np.sin(x) # RSI follows price cycles
        macd = np.gradient(price) # Momentum proxy

        data = {
            'close': price,
            'RSI_14': rsi,
            'MACD_12_26_9': macd,
            'sentiment': np.sin(x/2) # Sentiment cycles slower
        }
        df = pd.DataFrame(data)

        # 2. Initialize Environment
        env = TradingEnv(df)

        # 3. Train Agent (PPO)
        try:
            model = PPO("MlpPolicy", env, verbose=0)
            model.learn(total_timesteps=10000)

            self.model = model
            model.save(self.MODEL_PATH)
            logger.info("✅ Deep RL Agent Evolved & Saved.")
        except Exception as e:
            logger.error(f"Training failed: {e}")

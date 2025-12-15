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
        """
        logger.info("🎓 Starting Deep RL Training...")

        # 1. Create Simulation Data
        # In a real scenario, this comes from DB history or fetched historical data
        dates = pd.date_range(start='2023-01-01', periods=200)
        data = {
            'close': np.random.uniform(100, 200, 200),
            'RSI_14': np.random.uniform(20, 80, 200),
            'MACD_12_26_9': np.random.uniform(-5, 5, 200),
            'sentiment': np.random.uniform(-1, 1, 200)
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

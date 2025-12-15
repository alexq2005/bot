import logging
import joblib
import pandas as pd
import numpy as np
import os
from sb3_contrib import RecurrentPPO
from typing import Dict, List
from .database import get_db, Trade, SentimentLog
from .rl_agent import TradingEnv

logger = logging.getLogger(__name__)

class MLEngine:
    """
    Next-Gen AI Brain using Recurrent Deep Reinforcement Learning (LSTM-PPO).
    The agent has MEMORY of past sequences, enabling trend and pattern recognition.
    """

    MODEL_PATH = "drl_lstm_agent.zip"

    def __init__(self):
        self.model = None
        self._load_model()
        self.lstm_states = None # To store hidden states between steps if needed

    def _load_model(self):
        if os.path.exists(self.MODEL_PATH):
            try:
                self.model = RecurrentPPO.load(self.MODEL_PATH)
                logger.info("🧠 Loaded Deep Recurrent RL Agent (LSTM)")
            except:
                logger.warning("Could not load RL Agent, starting fresh")
        else:
            logger.info("🆕 No RL Agent found. Waiting for training.")

    def predict_action(self, rsi: float, macd: float, sentiment: float, position_status: int, atr: float, vol_change: float = 0.0) -> int:
        """
        Asks the RL Agent for the best action.
        Returns: 0 (Hold), 1 (Buy), 2 (Sell)
        """
        if not self.model:
            return 0 # Hold

        # Observation: [Price(0), RSI, MACD, Sentiment, PosStatus, ATR, VolChange]
        # Matches the expanded observation space
        obs = np.array([0.0, rsi, macd, sentiment, position_status, atr, vol_change], dtype=np.float32)

        try:
            # RecurrentPPO predict returns action and next_lstm_states
            # We must maintain state continuity ideally, but for single-step prediction in this architecture,
            # we rely on the model inferring from the current input or we reset state if gap is large.
            # Here we pass None to reset state, assuming decision is made on snapshot (suboptimal but robust for bot loop)
            # Improvement: Store self.lstm_states and pass it here.

            action, self.lstm_states = self.model.predict(
                obs,
                state=self.lstm_states,
                episode_start=np.array([False]), # Assume continuing episode
                deterministic=True
            )
            logger.info(f"🤖 LSTM Agent chose action: {action}")
            return int(action)
        except Exception as e:
            logger.error(f"RL Prediction failed: {e}")
            return 0

    def train_model(self):
        """
        Evolutionary Step: Retrains the Recurrent RL Agent using simulated environment.
        """
        logger.info("🎓 Starting Deep Recurrent RL Training (LSTM)...")

        # 1. Create Deterministic Simulation Data (Sine Wave + Trend)
        length = 2000 # Longer for LSTM to learn patterns
        x = np.linspace(0, 100, length)
        price = 100 + x + 10 * np.sin(x) + np.random.normal(0, 2, length)
        rsi = 50 + 40 * np.sin(x)
        macd = np.gradient(price)

        data = {
            'close': price,
            'RSI_14': rsi,
            'MACD_12_26_9': macd,
            'sentiment': np.sin(x/2),
            'ATR_14': np.random.uniform(0.5, 3.0, length),
            'volume': np.random.uniform(1000, 50000, length)
        }
        df = pd.DataFrame(data)

        # 2. Initialize Environment
        env = TradingEnv(df)

        # 3. Train Agent (RecurrentPPO)
        try:
            # MlpLstmPolicy is default for RecurrentPPO
            model = RecurrentPPO("MlpLstmPolicy", env, verbose=0)
            model.learn(total_timesteps=20000)

            self.model = model
            model.save(self.MODEL_PATH)
            logger.info("✅ Deep Recurrent RL Agent Evolved & Saved.")
        except Exception as e:
            logger.error(f"Training failed: {e}")

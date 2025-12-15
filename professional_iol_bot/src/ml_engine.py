import logging
import joblib
import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from typing import Dict, List
from .database import get_db, Trade, SentimentLog

logger = logging.getLogger(__name__)

class MLEngine:
    """
    Self-Improving Machine Learning Brain.
    Predicts: Will this trade be profitable?
    Algorithm: Random Forest
    """

    MODEL_PATH = "ml_brain.joblib"

    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.MODEL_PATH):
            try:
                self.model = joblib.load(self.MODEL_PATH)
                logger.info("🧠 Loaded existing ML Brain")
            except:
                logger.warning("Could not load ML Brain, starting fresh")
        else:
            logger.info("🆕 No ML Brain found. Waiting for training data.")

    def predict_profitability(self, rsi: float, macd: float, sentiment: float, atr: float) -> float:
        """
        Returns probability of profit (0.0 to 1.0).
        If model is not trained yet, returns 0.5 (Neutral).
        """
        if not self.model:
            return 0.5

        # Features must match training data
        features = np.array([[rsi, macd, sentiment, atr]])
        try:
            # Predict probability of class 1 (Win)
            prob = self.model.predict_proba(features)[0][1]
            logger.info(f"🔮 ML Prediction: Win Probability = {prob:.2%}")
            return prob
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return 0.5

    def train_model(self):
        """
        Evolutionary Step: Retrains the model using DB history.
        Should be called periodically (e.g., daily).
        """
        logger.info("🎓 Starting Evolutionary Training...")

        # 1. Fetch Data from DB
        # Ideally, we need to join Trades with Market Conditions at that time.
        # For this prototype, we'll simulate a dataset generation or assume we logged features.
        # TODO: In production, we must log 'features_at_entry' in the Trade table.

        # Simulating data for structure (RSI, MACD, Sentiment, ATR, RESULT)
        # Result: 1 if Trade was Profitable, 0 otherwise

        # Real implementation would query DB here
        # df = pd.read_sql(...)

        # Check if we have enough data (e.g. > 50 trades)
        # if len(df) < 50: return

        # Placeholder training logic for demo
        X_train = np.random.rand(100, 4) # Fake features
        y_train = np.random.randint(0, 2, 100) # Fake targets

        clf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        clf.fit(X_train, y_train)

        self.model = clf
        joblib.dump(self.model, self.MODEL_PATH)
        logger.info("✅ ML Brain Evolved & Saved.")

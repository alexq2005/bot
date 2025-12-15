import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
from typing import List, Dict

class TradingEnv(gym.Env):
    """
    Custom Environment that follows gym interface.
    The agent learns to trade by interacting with this environment.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, df: pd.DataFrame, initial_balance=10000):
        super(TradingEnv, self).__init__()

        self.df = df
        self.initial_balance = initial_balance
        self.current_step = 0

        # Action Space: 0=Hold, 1=Buy, 2=Sell
        self.action_space = spaces.Discrete(3)

        # Observation Space: [Price, RSI, MACD, Sentiment, Position_Status]
        # Position_Status: 0=No Position, 1=Long
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(5,), dtype=np.float32
        )

        self.reset()

    def reset(self, seed=None):
        self.current_step = 0
        self.balance = self.initial_balance
        self.position = 0 # 0 or shares held
        self.entry_price = 0
        self.net_worth = self.initial_balance

        observation = self._next_observation()
        return observation, {}

    def _next_observation(self):
        # Get data for current step
        frame = self.df.iloc[self.current_step]

        obs = np.array([
            frame['close'],
            frame.get('RSI_14', 50), # Default to neutral if missing
            frame.get('MACD_12_26_9', 0),
            frame.get('sentiment', 0), # Added sentiment feature
            1 if self.position > 0 else 0
        ], dtype=np.float32)

        return obs

    def step(self, action):
        current_price = self.df.iloc[self.current_step]['close']
        reward = 0
        terminated = False
        truncated = False

        # Actions
        if action == 1: # Buy
            if self.position == 0:
                # Buy as much as possible
                self.position = self.balance / current_price
                self.balance = 0
                self.entry_price = current_price

        elif action == 2: # Sell
            if self.position > 0:
                # Sell everything
                self.balance = self.position * current_price
                self.position = 0

                # Reward is profit/loss %
                profit_pct = (current_price - self.entry_price) / self.entry_price
                reward = profit_pct * 100 # Scale up reward

        # Hold (Action 0) -> No immediate reward, maybe small penalty for time?

        # Update Net Worth
        current_val = self.balance + (self.position * current_price)
        self.net_worth = current_val

        # Move to next step
        self.current_step += 1

        if self.current_step >= len(self.df) - 1:
            terminated = True

        obs = self._next_observation()

        return obs, reward, terminated, truncated, {}

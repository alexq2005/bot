"""
Portfolio Optimization using Modern Portfolio Theory
Implements efficient frontier, Sharpe ratio optimization, and portfolio analytics
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
from scipy.optimize import minimize


class PortfolioOptimizer:
    """
    Modern Portfolio Theory implementation for portfolio optimization
    
    Features:
    - Efficient frontier calculation
    - Minimum variance portfolio
    - Maximum Sharpe ratio portfolio
    - Portfolio statistics (return, risk, Sharpe)
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize portfolio optimizer
        
        Args:
            risk_free_rate: Annual risk-free rate (default: 2%)
        """
        self.risk_free_rate = risk_free_rate
    
    def calculate_portfolio_stats(
        self,
        weights: np.ndarray,
        returns_df: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Calculate portfolio statistics
        
        Args:
            weights: Asset weights (must sum to 1)
            returns_df: DataFrame with asset returns
            
        Returns:
            Dict with 'return', 'volatility', 'sharpe'
        """
        # Annualized return
        portfolio_return = np.sum(returns_df.mean() * weights) * 252
        
        # Annualized volatility
        portfolio_volatility = np.sqrt(
            np.dot(weights.T, np.dot(returns_df.cov() * 252, weights))
        )
        
        # Sharpe ratio
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
        
        return {
            'return': portfolio_return,
            'volatility': portfolio_volatility,
            'sharpe': sharpe_ratio
        }
    
    def calculate_efficient_frontier(
        self,
        returns_df: pd.DataFrame,
        num_portfolios: int = 1000
    ) -> pd.DataFrame:
        """
        Calculate efficient frontier using Monte Carlo simulation
        
        Args:
            returns_df: DataFrame with asset returns
            num_portfolios: Number of random portfolios to generate
            
        Returns:
            DataFrame with portfolio returns, volatilities, Sharpe ratios, and weights
        """
        num_assets = len(returns_df.columns)
        results = []
        
        for _ in range(num_portfolios):
            # Random weights
            weights = np.random.random(num_assets)
            weights /= np.sum(weights)
            
            # Calculate stats
            stats = self.calculate_portfolio_stats(weights, returns_df)
            
            # Store results
            result = {
                'return': stats['return'],
                'volatility': stats['volatility'],
                'sharpe': stats['sharpe']
            }
            
            # Add weights
            for i, col in enumerate(returns_df.columns):
                result[f'weight_{col}'] = weights[i]
            
            results.append(result)
        
        return pd.DataFrame(results)
    
    def get_minimum_variance_portfolio(
        self,
        returns_df: pd.DataFrame
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Find minimum variance portfolio
        
        Args:
            returns_df: DataFrame with asset returns
            
        Returns:
            (weights, stats) tuple
        """
        num_assets = len(returns_df.columns)
        
        # Objective: minimize variance
        def portfolio_variance(weights):
            return self.calculate_portfolio_stats(weights, returns_df)['volatility']
        
        # Constraints: weights sum to 1
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        
        # Bounds: each weight between 0 and 1
        bounds = tuple((0, 1) for _ in range(num_assets))
        
        # Initial guess: equal weights
        init_weights = np.array([1.0 / num_assets] * num_assets)
        
        # Optimize
        result = minimize(
            portfolio_variance,
            init_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        weights = result.x
        stats = self.calculate_portfolio_stats(weights, returns_df)
        
        return weights, stats
    
    def get_maximum_sharpe_portfolio(
        self,
        returns_df: pd.DataFrame
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Find maximum Sharpe ratio portfolio
        
        Args:
            returns_df: DataFrame with asset returns
            
        Returns:
            (weights, stats) tuple
        """
        num_assets = len(returns_df.columns)
        
        # Objective: maximize Sharpe (minimize negative Sharpe)
        def negative_sharpe(weights):
            return -self.calculate_portfolio_stats(weights, returns_df)['sharpe']
        
        # Constraints: weights sum to 1
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        
        # Bounds: each weight between 0 and 1
        bounds = tuple((0, 1) for _ in range(num_assets))
        
        # Initial guess: equal weights
        init_weights = np.array([1.0 / num_assets] * num_assets)
        
        # Optimize
        result = minimize(
            negative_sharpe,
            init_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        weights = result.x
        stats = self.calculate_portfolio_stats(weights, returns_df)
        
        return weights, stats
    
    def get_portfolio_stats(
        self,
        weights: np.ndarray,
        returns_df: pd.DataFrame
    ) -> Dict[str, float]:
        """Alias for calculate_portfolio_stats"""
        return self.calculate_portfolio_stats(weights, returns_df)

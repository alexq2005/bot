"""
Risk Analytics Engine
Comprehensive risk measurement: VaR, CVaR, correlation analysis, beta calculation
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional
from scipy import stats


class RiskAnalytics:
    """
    Comprehensive risk measurement and analytics
    
    Features:
    - Value at Risk (VaR) - Historical and Parametric methods
    - Conditional VaR (CVaR/Expected Shortfall)
    - Correlation matrix analysis
    - Beta calculation
    - Maximum drawdown
    """
    
    def __init__(self):
        """Initialize risk analytics engine"""
        pass
    
    def calculate_var_historical(
        self,
        returns: pd.Series,
        confidence: float = 0.95
    ) -> float:
        """
        Calculate Value at Risk using historical method
        
        Args:
            returns: Series of returns
            confidence: Confidence level (default: 95%)
            
        Returns:
            VaR as negative number (e.g., -0.05 means 5% loss)
        """
        if len(returns) == 0:
            return 0.0
        
        # Sort returns
        sorted_returns = np.sort(returns)
        
        # Find percentile
        index = int((1 - confidence) * len(sorted_returns))
        
        return sorted_returns[index]
    
    def calculate_var_parametric(
        self,
        returns: pd.Series,
        confidence: float = 0.95
    ) -> float:
        """
        Calculate Value at Risk using parametric (variance-covariance) method
        
        Assumes normal distribution of returns
        
        Args:
            returns: Series of returns
            confidence: Confidence level (default: 95%)
            
        Returns:
            VaR as negative number
        """
        if len(returns) == 0:
            return 0.0
        
        # Calculate mean and std
        mean = returns.mean()
        std = returns.std()
        
        # Get z-score for confidence level
        z_score = stats.norm.ppf(1 - confidence)
        
        # Calculate VaR
        var = mean + (z_score * std)
        
        return var
    
    def calculate_cvar(
        self,
        returns: pd.Series,
        confidence: float = 0.95
    ) -> float:
        """
        Calculate Conditional VaR (CVaR / Expected Shortfall)
        
        Average loss beyond VaR threshold
        
        Args:
            returns: Series of returns
            confidence: Confidence level (default: 95%)
            
        Returns:
            CVaR as negative number
        """
        if len(returns) == 0:
            return 0.0
        
        # Calculate VaR first
        var = self.calculate_var_historical(returns, confidence)
        
        # CVaR is average of all returns worse than VaR
        cvar = returns[returns <= var].mean()
        
        return cvar
    
    def calculate_correlation_matrix(
        self,
        returns_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate correlation matrix for multiple assets
        
        Args:
            returns_df: DataFrame with asset returns (columns = assets)
            
        Returns:
            Correlation matrix DataFrame
        """
        return returns_df.corr()
    
    def calculate_beta(
        self,
        asset_returns: pd.Series,
        market_returns: pd.Series
    ) -> float:
        """
        Calculate beta (systematic risk) of asset vs market
        
        Beta = Covariance(asset, market) / Variance(market)
        
        Args:
            asset_returns: Asset return series
            market_returns: Market return series
            
        Returns:
            Beta value (1.0 = same as market, >1 = more volatile, <1 = less volatile)
        """
        # Align series
        aligned = pd.DataFrame({
            'asset': asset_returns,
            'market': market_returns
        }).dropna()
        
        if len(aligned) < 2:
            return 1.0
        
        # Calculate covariance and variance
        covariance = np.cov(aligned['asset'], aligned['market'])[0][1]
        market_variance = np.var(aligned['market'])
        
        if market_variance == 0:
            return 1.0
        
        beta = covariance / market_variance
        
        return beta
    
    def calculate_maximum_drawdown(
        self,
        prices: pd.Series
    ) -> Dict[str, float]:
        """
        Calculate maximum drawdown (peak-to-trough decline)
        
        Args:
            prices: Price series
            
        Returns:
            Dict with 'max_drawdown', 'peak_idx', 'trough_idx'
        """
        if len(prices) == 0:
            return {'max_drawdown': 0.0, 'peak_idx': 0, 'trough_idx': 0}
        
        # Calculate cumulative maximum
        cummax = prices.expanding().max()
        
        # Calculate drawdown
        drawdown = (prices - cummax) / cummax
        
        # Find maximum drawdown
        max_dd = drawdown.min()
        trough_idx = drawdown.idxmin()
        
        # Find corresponding peak
        peak_idx = prices[:trough_idx].idxmax() if trough_idx > 0 else 0
        
        return {
            'max_drawdown': max_dd,
            'peak_idx': peak_idx,
            'trough_idx': trough_idx
        }
    
    def calculate_portfolio_risk_decomposition(
        self,
        weights: np.ndarray,
        returns_df: pd.DataFrame
    ) -> Dict[str, np.ndarray]:
        """
        Decompose portfolio risk into component contributions
        
        Args:
            weights: Portfolio weights
            returns_df: DataFrame with asset returns
            
        Returns:
            Dict with 'marginal_risk', 'component_risk', 'pct_contribution'
        """
        # Covariance matrix
        cov_matrix = returns_df.cov() * 252  # Annualized
        
        # Portfolio variance
        portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
        portfolio_vol = np.sqrt(portfolio_variance)
        
        # Marginal risk contribution
        marginal_risk = np.dot(cov_matrix, weights) / portfolio_vol
        
        # Component risk contribution
        component_risk = weights * marginal_risk
        
        # Percentage contribution
        pct_contribution = component_risk / portfolio_vol
        
        return {
            'marginal_risk': marginal_risk,
            'component_risk': component_risk,
            'pct_contribution': pct_contribution
        }
    
    def get_risk_summary(
        self,
        returns: pd.Series,
        confidence: float = 0.95
    ) -> Dict[str, float]:
        """
        Get comprehensive risk summary
        
        Args:
            returns: Return series
            confidence: Confidence level for VaR/CVaR
            
        Returns:
            Dict with all risk metrics
        """
        return {
            'var_historical': self.calculate_var_historical(returns, confidence),
            'var_parametric': self.calculate_var_parametric(returns, confidence),
            'cvar': self.calculate_cvar(returns, confidence),
            'volatility': returns.std() * np.sqrt(252),  # Annualized
            'mean_return': returns.mean() * 252,  # Annualized
        }

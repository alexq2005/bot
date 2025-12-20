"""
Advanced Chart Pattern Recognition
Detects complex patterns: Head & Shoulders, Triangles, Flags, Double Top/Bottom, Cup & Handle
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple


class AdvancedPatternRecognizer:
    """
    Detects advanced chart patterns in price data
    
    Patterns:
    - Head & Shoulders (reversal)
    - Triangle patterns (continuation/reversal)
    - Flag patterns (continuation)
    - Double Top/Bottom (reversal)
    - Cup & Handle (bullish continuation)
    """
    
    def __init__(self, lookback_window: int = 50):
        """
        Initialize pattern recognizer
        
        Args:
            lookback_window: Number of candles to analyze
        """
        self.lookback_window = lookback_window
    
    def detect_head_and_shoulders(
        self,
        df: pd.DataFrame,
        tolerance: float = 0.02
    ) -> Optional[Dict]:
        """
        Detect Head & Shoulders pattern
        
        Args:
            df: DataFrame with OHLC data
            tolerance: Price tolerance for shoulder matching (2%)
            
        Returns:
            Pattern dict or None if not found
        """
        if len(df) < 20:
            return None
        
        # Use recent data
        recent = df.tail(self.lookback_window)
        highs = recent['high'].values
        
        # Find local maxima
        peaks = []
        for i in range(2, len(highs) - 2):
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and \
               highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                peaks.append((i, highs[i]))
        
        # Need at least 3 peaks for H&S
        if len(peaks) < 3:
            return None
        
        # Check last 3 peaks for H&S pattern
        if len(peaks) >= 3:
            left_shoulder_idx, left_shoulder = peaks[-3]
            head_idx, head = peaks[-2]
            right_shoulder_idx, right_shoulder = peaks[-1]
            
            # Head should be higher than shoulders
            if head > left_shoulder and head > right_shoulder:
                # Shoulders should be similar height
                shoulder_diff = abs(left_shoulder - right_shoulder) / left_shoulder
                
                if shoulder_diff < tolerance:
                    return {
                        'pattern': 'head_and_shoulders',
                        'type': 'bearish',
                        'confidence': 1.0 - shoulder_diff,
                        'index': head_idx,
                        'neckline': min(left_shoulder, right_shoulder),
                        'target': min(left_shoulder, right_shoulder) - (head - min(left_shoulder, right_shoulder))
                    }
        
        return None
    
    def detect_triangles(
        self,
        df: pd.DataFrame
    ) -> List[Dict]:
        """
        Detect triangle patterns (ascending, descending, symmetrical)
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            List of detected triangle patterns
        """
        patterns = []
        
        if len(df) < 20:
            return patterns
        
        recent = df.tail(self.lookback_window)
        highs = recent['high'].values
        lows = recent['low'].values
        
        # Simple triangle detection using trendlines
        # Ascending: flat resistance, rising support
        # Descending: falling resistance, flat support
        # Symmetrical: converging trendlines
        
        # Calculate simple slopes for last 10 highs and lows
        if len(highs) >= 10:
            high_slope = np.polyfit(range(10), highs[-10:], 1)[0]
            low_slope = np.polyfit(range(10), lows[-10:], 1)[0]
            
            # Ascending triangle
            if abs(high_slope) < 0.5 and low_slope > 0.5:
                patterns.append({
                    'pattern': 'ascending_triangle',
                    'type': 'bullish',
                    'confidence': 0.75,
                    'breakout_level': highs[-1]
                })
            
            # Descending triangle
            elif high_slope < -0.5 and abs(low_slope) < 0.5:
                patterns.append({
                    'pattern': 'descending_triangle',
                    'type': 'bearish',
                    'confidence': 0.75,
                    'breakout_level': lows[-1]
                })
            
            # Symmetrical triangle
            elif high_slope < 0 and low_slope > 0:
                patterns.append({
                    'pattern': 'symmetrical_triangle',
                    'type': 'neutral',
                    'confidence': 0.70
                })
        
        return patterns
    
    def detect_flags(
        self,
        df: pd.DataFrame,
        pole_threshold: float = 0.10
    ) -> List[Dict]:
        """
        Detect flag patterns (bullish/bearish continuation)
        
        Args:
            df: DataFrame with OHLC data
            pole_threshold: Minimum price movement for pole (10%)
            
        Returns:
            List of detected flag patterns
        """
        patterns = []
        
        if len(df) < 15:
            return patterns
        
        recent = df.tail(30)
        closes = recent['close'].values
        
        # Look for strong move (pole) followed by consolidation (flag)
        if len(closes) >= 15:
            # Check for bullish flag
            pole_move = (closes[10] - closes[0]) / closes[0]
            if pole_move > pole_threshold:
                # Check for consolidation
                flag_volatility = np.std(closes[10:]) / np.mean(closes[10:])
                if flag_volatility < 0.03:  # Low volatility = consolidation
                    patterns.append({
                        'pattern': 'bullish_flag',
                        'type': 'bullish',
                        'confidence': 0.80,
                        'pole_strength': pole_move,
                        'continuation_expected': pole_move
                    })
            
            # Check for bearish flag
            pole_move = (closes[0] - closes[10]) / closes[0]
            if pole_move > pole_threshold:
                flag_volatility = np.std(closes[10:]) / np.mean(closes[10:])
                if flag_volatility < 0.03:
                    patterns.append({
                        'pattern': 'bearish_flag',
                        'type': 'bearish',
                        'confidence': 0.80,
                        'pole_strength': pole_move,
                        'continuation_expected': -pole_move
                    })
        
        return patterns
    
    def detect_double_topbottom(
        self,
        df: pd.DataFrame,
        tolerance: float = 0.015
    ) -> List[Dict]:
        """
        Detect double top/bottom patterns
        
        Args:
            df: DataFrame with OHLC data
            tolerance: Price tolerance for matching peaks/troughs (1.5%)
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        if len(df) < 20:
            return patterns
        
        recent = df.tail(self.lookback_window)
        highs = recent['high'].values
        lows = recent['low'].values
        
        # Find peaks for double top
        peaks = []
        for i in range(2, len(highs) - 2):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                peaks.append((i, highs[i]))
        
        # Check for double top (last 2 peaks)
        if len(peaks) >= 2:
            peak1_idx, peak1 = peaks[-2]
            peak2_idx, peak2 = peaks[-1]
            
            if abs(peak1 - peak2) / peak1 < tolerance:
                patterns.append({
                    'pattern': 'double_top',
                    'type': 'bearish',
                    'confidence': 1.0 - abs(peak1 - peak2) / peak1,
                    'resistance': max(peak1, peak2)
                })
        
        # Find troughs for double bottom
        troughs = []
        for i in range(2, len(lows) - 2):
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                troughs.append((i, lows[i]))
        
        # Check for double bottom (last 2 troughs)
        if len(troughs) >= 2:
            trough1_idx, trough1 = troughs[-2]
            trough2_idx, trough2 = troughs[-1]
            
            if abs(trough1 - trough2) / trough1 < tolerance:
                patterns.append({
                    'pattern': 'double_bottom',
                    'type': 'bullish',
                    'confidence': 1.0 - abs(trough1 - trough2) / trough1,
                    'support': min(trough1, trough2)
                })
        
        return patterns
    
    def detect_cup_and_handle(
        self,
        df: pd.DataFrame
    ) -> Optional[Dict]:
        """
        Detect cup and handle pattern
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            Pattern dict or None
        """
        if len(df) < 30:
            return None
        
        recent = df.tail(self.lookback_window)
        closes = recent['close'].values
        
        # Simplified cup & handle detection
        if len(closes) >= 30:
            # Cup: U-shaped recovery
            mid_point = len(closes) // 2
            first_half = closes[:mid_point]
            second_half = closes[mid_point:]
            
            # Check if first half declines and second half recovers
            if first_half[0] > first_half[-1] and second_half[-1] > second_half[0]:
                # Check if end price is near start
                if abs(closes[-1] - closes[0]) / closes[0] < 0.05:
                    return {
                        'pattern': 'cup_and_handle',
                        'type': 'bullish',
                        'confidence': 0.75,
                        'breakout_level': max(closes)
                    }
        
        return None
    
    def detect_all_patterns(
        self,
        df: pd.DataFrame
    ) -> Dict[str, List]:
        """
        Detect all advanced patterns
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            Dict with all detected patterns by type
        """
        all_patterns = {
            'head_and_shoulders': [],
            'triangles': [],
            'flags': [],
            'double_patterns': [],
            'cup_and_handle': []
        }
        
        # Detect each pattern type
        hs = self.detect_head_and_shoulders(df)
        if hs:
            all_patterns['head_and_shoulders'].append(hs)
        
        all_patterns['triangles'] = self.detect_triangles(df)
        all_patterns['flags'] = self.detect_flags(df)
        all_patterns['double_patterns'] = self.detect_double_topbottom(df)
        
        cup = self.detect_cup_and_handle(df)
        if cup:
            all_patterns['cup_and_handle'].append(cup)
        
        return all_patterns

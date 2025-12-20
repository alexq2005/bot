"""
Visualización de indicadores técnicos con Plotly
Crea gráficos interactivos para análisis técnico
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict


class IndicatorVisualizer:
    """Crea gráficos interactivos de indicadores técnicos"""
    
    @staticmethod
    def create_comprehensive_chart(
        prices: pd.DataFrame,
        indicators: pd.DataFrame
    ) -> go.Figure:
        """
        Crea gráfico completo con precio + todos los indicadores
        
        Args:
            prices: DataFrame con columnas ['date', 'open', 'high', 'low', 'close', 'volume']
            indicators: DataFrame con indicadores calculados
            
        Returns:
            Figura de Plotly con 4 subplots
        """
        # Ensure we have a date column
        if 'date' not in prices.columns:
            if prices.index.name == 'date' or isinstance(prices.index, pd.DatetimeIndex):
                prices = prices.reset_index()
            else:
                prices['date'] = range(len(prices))
        
        # Create subplots: Precio + BB, RSI, MACD, Volumen
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.5, 0.15, 0.2, 0.15],
            subplot_titles=(
                'Precio y Bandas de Bollinger',
                'RSI (14)',
                'MACD',
                'Volumen'
            )
        )
        
        # 1. Candlestick + Bandas de Bollinger
        fig.add_trace(
            go.Candlestick(
                x=prices['date'],
                open=prices['open'],
                high=prices['high'],
                low=prices['low'],
                close=prices['close'],
                name='Precio'
            ),
            row=1, col=1
        )
        
        # Bollinger Bands
        if 'bb_upper' in indicators.columns:
            fig.add_trace(
                go.Scatter(
                    x=prices['date'],
                    y=indicators['bb_upper'],
                    name='BB Superior',
                    line=dict(color='rgba(250, 128, 114, 0.5)', dash='dash')
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=prices['date'],
                    y=indicators['bb_middle'],
                    name='BB Media',
                    line=dict(color='rgba(128, 128, 128, 0.5)')
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=prices['date'],
                    y=indicators['bb_lower'],
                    name='BB Inferior',
                    line=dict(color='rgba(173, 216, 230, 0.5)', dash='dash'),
                    fill='tonexty'
                ),
                row=1, col=1
            )
        
        # 2. RSI
        if 'rsi' in indicators.columns:
            fig.add_trace(
                go.Scatter(
                    x=prices['date'],
                    y=indicators['rsi'],
                    name='RSI',
                    line=dict(color='purple')
                ),
                row=2, col=1
            )
            
            # Líneas de sobrecompra/sobreventa
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # 3. MACD
        if 'macd' in indicators.columns:
            fig.add_trace(
                go.Scatter(
                    x=prices['date'],
                    y=indicators['macd'],
                    name='MACD',
                    line=dict(color='blue')
                ),
                row=3, col=1
            )
            
            if 'macd_signal' in indicators.columns:
                fig.add_trace(
                    go.Scatter(
                        x=prices['date'],
                        y=indicators['macd_signal'],
                        name='Signal',
                        line=dict(color='orange')
                    ),
                    row=3, col=1
                )
            
            # Histograma MACD
            if 'macd_hist' in indicators.columns:
                colors = ['green' if val >= 0 else 'red' for val in indicators['macd_hist']]
                fig.add_trace(
                    go.Bar(
                        x=prices['date'],
                        y=indicators['macd_hist'],
                        name='Histogram',
                        marker_color=colors
                    ),
                    row=3, col=1
                )
        
        # 4. Volumen
        if 'volume' in prices.columns:
            fig.add_trace(
                go.Bar(
                    x=prices['date'],
                    y=prices['volume'],
                    name='Volumen',
                    marker_color='rgba(0, 150, 255, 0.5)'
                ),
                row=4, col=1
            )
        
        # Layout
        fig.update_layout(
            title='Análisis Técnico Completo',
            xaxis_rangeslider_visible=False,
            height=900,
            showlegend=True,
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def create_simple_chart(
        prices: pd.DataFrame,
        indicator_name: str,
        indicator_data: pd.Series
    ) -> go.Figure:
        """
        Crea gráfico simple de un indicador individual
        
        Args:
            prices: DataFrame con columna 'close' y opcionalmente 'date'
            indicator_name: Nombre del indicador
            indicator_data: Serie con datos del indicador
            
        Returns:
            Figura de Plotly
        """
        # Ensure we have a date column
        if 'date' not in prices.columns:
            if prices.index.name == 'date' or isinstance(prices.index, pd.DatetimeIndex):
                dates = prices.index
            else:
                dates = range(len(prices))
        else:
            dates = prices['date']
        
        fig = go.Figure()
        
        # Add price line
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=prices['close'],
                name='Precio',
                line=dict(color='blue')
            )
        )
        
        # Add indicator on secondary y-axis
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=indicator_data,
                name=indicator_name,
                line=dict(color='orange'),
                yaxis='y2'
            )
        )
        
        fig.update_layout(
            title=f'Precio vs {indicator_name}',
            yaxis=dict(title='Precio'),
            yaxis2=dict(title=indicator_name, overlaying='y', side='right'),
            hovermode='x unified'
        )
        
        return fig

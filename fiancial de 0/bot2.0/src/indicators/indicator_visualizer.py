"""
Visualización de indicadores técnicos con Plotly
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
        indicators: Dict
    ) -> go.Figure:
        """
        Crea gráfico completo con precio + todos los indicadores
        
        Args:
            prices: DataFrame con columnas ['date', 'open', 'high', 'low', 'close', 'volume']
            indicators: Dict con indicadores calculados
            
        Returns:
            Figura de Plotly con 4 subplots
        """
        # Crear subplots: Precio + BB, RSI, MACD, Volumen
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
        
        bb = indicators['bollinger']
        fig.add_trace(
            go.Scatter(
                x=prices['date'],
                y=bb['upper'],
                name='BB Superior',
                line=dict(color='rgba(250, 128, 114, 0.5)', dash='dash')
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=prices['date'],
                y=bb['middle'],
                name='BB Media',
                line=dict(color='rgba(128, 128, 128, 0.5)')
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=prices['date'],
                y=bb['lower'],
                name='BB Inferior',
                line=dict(color='rgba(173, 216, 230, 0.5)', dash='dash'),
                fill='tonexty'
            ),
            row=1, col=1
        )
        
        # 2. RSI
        rsi = indicators['rsi']
        fig.add_trace(
            go.Scatter(
                x=prices['date'],
                y=rsi,
                name='RSI',
                line=dict(color='purple')
            ),
            row=2, col=1
        )
        
        # Líneas de sobrecompra/sobreventa
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # 3. MACD
        macd = indicators['macd']
        fig.add_trace(
            go.Scatter(
                x=prices['date'],
                y=macd['macd'],
                name='MACD',
                line=dict(color='blue')
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=prices['date'],
                y=macd['signal'],
                name='Signal',
                line=dict(color='orange')
            ),
            row=3, col=1
        )
        
        # Histograma MACD
        colors = ['green' if val >= 0 else 'red' for val in macd['histogram']]
        fig.add_trace(
            go.Bar(
                x=prices['date'],
                y=macd['histogram'],
                name='Histogram',
                marker_color=colors
            ),
            row=3, col=1
        )
        
        # 4. Volumen
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

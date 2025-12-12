"""
Funciones auxiliares para el Command Center mejorado
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta


def generate_candlestick_data(symbol="GGAL", days=30):
    """
    Genera datos simulados de candlestick para un símbolo
    
    Args:
        symbol: Símbolo del activo
        days: Número de días de datos
        
    Returns:
        DataFrame con datos OHLCV
    """
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Generar precios simulados
    base_price = 100
    prices = []
    
    for i in range(days):
        if i == 0:
            open_price = base_price
        else:
            open_price = prices[-1]['close']
        
        # Simular movimiento del día
        change = np.random.randn() * 2
        high = open_price + abs(np.random.randn() * 3)
        low = open_price - abs(np.random.randn() * 3)
        close = open_price + change
        volume = np.random.randint(1000000, 5000000)
        
        prices.append({
            'date': dates[i],
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    
    df = pd.DataFrame(prices)
    
    # Calcular indicadores técnicos
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean() if days >= 50 else None
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    
    return df


def create_candlestick_chart(df, symbol="GGAL"):
    """
    Crea gráfico de candlestick con indicadores técnicos
    
    Args:
        df: DataFrame con datos OHLCV
        symbol: Símbolo del activo
        
    Returns:
        Figura de Plotly
    """
    # Crear subplots: Precio + Volumen + RSI
    fig = make_subplots(
        rows=3, cols=1,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(f'{symbol} - Precio', 'Volumen', 'RSI'),
        vertical_spacing=0.05,
        shared_xaxes=True
    )
    
    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Precio',
            increasing_line_color='#00FF88',
            decreasing_line_color='#FF6B6B'
        ),
        row=1, col=1
    )
    
    # SMA 20
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['sma_20'],
            name='SMA 20',
            line=dict(color='#00D9FF', width=1)
        ),
        row=1, col=1
    )
    
    # Bollinger Bands
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['bb_upper'],
            name='BB Superior',
            line=dict(color='rgba(255, 255, 255, 0.3)', width=1, dash='dash'),
            showlegend=False
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['bb_lower'],
            name='BB Inferior',
            line=dict(color='rgba(255, 255, 255, 0.3)', width=1, dash='dash'),
            fill='tonexty',
            fillcolor='rgba(0, 217, 255, 0.1)',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Volumen
    colors = ['#00FF88' if df['close'].iloc[i] >= df['open'].iloc[i] else '#FF6B6B' 
              for i in range(len(df))]
    
    fig.add_trace(
        go.Bar(
            x=df['date'],
            y=df['volume'],
            name='Volumen',
            marker_color=colors,
            showlegend=False
        ),
        row=2, col=1
    )
    
    # RSI
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['rsi'],
            name='RSI',
            line=dict(color='#FFD93D', width=2)
        ),
        row=3, col=1
    )
    
    # Líneas de referencia RSI
    fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=3, col=1)
    
    # Layout
    fig.update_layout(
        template='plotly_dark',
        height=600,
        margin=dict(l=0, r=0, t=30, b=0),
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Actualizar ejes
    fig.update_xaxes(rangeslider_visible=False)
    fig.update_yaxes(title_text="Precio", row=1, col=1)
    fig.update_yaxes(title_text="Volumen", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])
    
    return fig


def generate_top_performers(count=5):
    """
    Genera datos simulados de top performers
    
    Args:
        count: Número de símbolos a generar
        
    Returns:
        DataFrame con top performers
    """
    symbols = ['GGAL', 'YPFD', 'PAMP', 'ALUA', 'BMA', 'TXAR', 'EDN', 'LOMA', 'MIRG', 'SUPV']
    
    data = []
    for symbol in symbols[:count]:
        price = np.random.uniform(50, 500)
        change_pct = np.random.uniform(-5, 10)
        volume = np.random.randint(1000000, 10000000)
        
        # Señal basada en cambio
        if change_pct > 3:
            signal = "🟢 COMPRA"
        elif change_pct < -2:
            signal = "🔴 VENTA"
        else:
            signal = "🟡 HOLD"
        
        data.append({
            'Símbolo': symbol,
            'Precio': f"${price:.2f}",
            'Cambio %': f"{change_pct:+.2f}%",
            'Volumen': f"{volume:,}",
            'Señal': signal,
            '_sort_change': change_pct  # Para ordenar
        })
    
    df = pd.DataFrame(data)
    df = df.sort_values('_sort_change', ascending=False)
    df = df.drop('_sort_change', axis=1)
    df = df.reset_index(drop=True)
    
    return df


def create_correlation_heatmap(symbols=None):
    """
    Crea mapa de calor de correlaciones
    
    Args:
        symbols: Lista de símbolos
        
    Returns:
        Figura de Plotly
    """
    if symbols is None:
        symbols = ['GGAL', 'YPFD', 'PAMP', 'ALUA', 'BMA']
    
    # Generar matriz de correlación simulada
    n = len(symbols)
    corr_matrix = np.random.rand(n, n)
    corr_matrix = (corr_matrix + corr_matrix.T) / 2  # Hacer simétrica
    np.fill_diagonal(corr_matrix, 1)  # Diagonal = 1
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix,
        x=symbols,
        y=symbols,
        colorscale='RdYlGn',
        zmid=0,
        text=np.round(corr_matrix, 2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlación")
    ))
    
    fig.update_layout(
        template='plotly_dark',
        height=400,
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis_title="",
        yaxis_title=""
    )
    
    return fig


__all__ = [
    'generate_candlestick_data',
    'create_candlestick_chart',
    'generate_top_performers',
    'create_correlation_heatmap'
]

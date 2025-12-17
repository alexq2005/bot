"""
Dashboard Visualization Helpers
Funciones para crear gráficas interactivas con Plotly
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def create_equity_curve(trades_df: pd.DataFrame) -> go.Figure:
    """
    Crea gráfica de equity curve (capital a través del tiempo)
    
    Args:
        trades_df: DataFrame con trades (debe tener 'timestamp' y 'pnl')
    
    Returns:
        Plotly Figure
    """
    if trades_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No hay datos de trades todavía",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Calcular equity acumulado
    df = trades_df.copy()
    df = df.sort_values('timestamp')
    df['cumulative_pnl'] = df['pnl'].cumsum()
    
    # Crear figura
    fig = go.Figure()
    
    # Agregar línea de equity
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['cumulative_pnl'],
        mode='lines',
        name='Equity',
        line=dict(color='#00D9FF', width=3),
        fill='tozeroy',
        fillcolor='rgba(0, 217, 255, 0.1)'
    ))
    
    # Layout
    fig.update_layout(
        title="📈 Equity Curve - Capital a través del Tiempo",
        xaxis_title="Fecha",
        yaxis_title="P&L Acumulado ($)",
        hovermode='x unified',
        template='plotly_dark',
        height=400
    )
    
    return fig


def create_pnl_distribution(trades_df: pd.DataFrame) -> go.Figure:
    """
    Crea histograma de distribución de P&L
    
    Args:
        trades_df: DataFrame con trades
    
    Returns:
        Plotly Figure
    """
    if trades_df.empty or 'pnl' not in trades_df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="No hay datos de P&L",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    pnl = trades_df['pnl']
    
    # Crear histograma
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=pnl,
        nbinsx=30,
        marker=dict(
            color=pnl,
            colorscale=[[0, 'red'], [0.5, 'yellow'], [1, 'green']],
            showscale=False
        ),
        name='P&L'
    ))
    
    # Línea vertical en cero
    fig.add_vline(x=0, line_dash="dash", line_color="white", opacity=0.5)
    
    fig.update_layout(
        title="📊 Distribución de Ganancias/Pérdidas",
        xaxis_title="P&L ($)",
        yaxis_title="Frecuencia",
        template='plotly_dark',
        height=400
    )
    
    return fig


def create_win_rate_by_symbol(trades_df: pd.DataFrame) -> go.Figure:
    """
    Crea gráfica de barras de win rate por símbolo
    
    Args:
        trades_df: DataFrame con trades
    
    Returns:
        Plotly Figure
    """
    if trades_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No hay datos", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    # Calcular win rate por símbolo
    stats = []
    for symbol in trades_df['symbol'].unique():
        symbol_trades = trades_df[trades_df['symbol'] == symbol]
        winners = (symbol_trades['pnl'] > 0).sum()
        total = len(symbol_trades)
        win_rate = (winners / total * 100) if total > 0 else 0
        
        stats.append({
            'symbol': symbol,
            'win_rate': win_rate,
            'total_trades': total
        })
    
    stats_df = pd.DataFrame(stats).sort_values('win_rate', ascending=False)
    
    # Colores basados en win rate
    colors = ['green' if wr >= 60 else 'orange' if wr >= 50 else 'red' for wr in stats_df['win_rate']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=stats_df['symbol'],
        y=stats_df['win_rate'],
        text=[f"{wr:.1f}%" for wr in stats_df['win_rate']],
        textposition='auto',
        marker=dict(color=colors),
        name='Win Rate',
        hovertemplate='<b>%{x}</b><br>Win Rate: %{y:.1f}%<br>Trades: %{customdata}<extra></extra>',
        customdata=stats_df['total_trades']
    ))
    
    # Línea de referencia 50%
    fig.add_hline(y=50, line_dash="dash", line_color="white", opacity=0.5,
                  annotation_text="50% (break even)")
    
    fig.update_layout(
        title="🎯 Win Rate por Símbolo",
        xaxis_title="Símbolo",
        yaxis_title="Win Rate (%)",
        template='plotly_dark',
        height=400
    )
    
    return fig


def create_performance_over_time(trades_df: pd.DataFrame) -> go.Figure:
    """
    Crea gráfica de performance diaria
    
    Args:
        trades_df: DataFrame con trades
    
    Returns:
        Plotly Figure
    """
    if trades_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No hay datos", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    # Agrupar por día
    df = trades_df.copy()
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    daily_pnl = df.groupby('date')['pnl'].sum().reset_index()
    
    # Colores por resultado
    colors = ['green' if pnl > 0 else 'red' for pnl in daily_pnl['pnl']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=daily_pnl['date'],
        y=daily_pnl['pnl'],
        marker=dict(color=colors),
        name='P&L Diario'
    ))
    
    fig.add_hline(y=0, line_color="white", opacity=0.3)
    
    fig.update_layout(
        title="📅 Performance Diaria",
        xaxis_title="Fecha",
        yaxis_title="P&L ($)",
        template='plotly_dark',
        height=400
    )
    
    return fig


def create_drawdown_chart(trades_df: pd.DataFrame) -> go.Figure:
    """
    Crea gráfica de drawdown
    
    Args:
        trades_df: DataFrame con trades
    
    Returns:
        Plotly Figure
    """
    if trades_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No hay datos", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    # Calcular drawdown
    df = trades_df.copy()
    df = df.sort_values('timestamp')
    df['cumulative_pnl'] = df['pnl'].cumsum()
    
    # Running maximum
    df['peak'] = df['cumulative_pnl'].cummax()
    
    # Drawdown
    df['drawdown'] = df['cumulative_pnl'] - df['peak']
    df['drawdown_pct'] = (df['drawdown'] / df['peak'].abs()) * 100
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['drawdown'],
        mode='lines',
        name='Drawdown',
        line=dict(color='red', width=2),
        fill='tozeroy',
        fillcolor='rgba(255, 0, 0, 0.2)'
    ))
    
    fig.update_layout(
        title="📉 Drawdown - Caída desde Pico Máximo",
        xaxis_title="Fecha",
        yaxis_title="Drawdown ($)",
        template='plotly_dark',
        height=400
    )
    
    return fig


def create_trade_volume_timeline(trades_df: pd.DataFrame) -> go.Figure:
    """
    Crea gráfica de volumen de trades por día
    
    Args:
        trades_df: DataFrame con trades
    
    Returns:
        Plotly Figure
    """
    if trades_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No hay datos", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    # Contar trades por día
    df = trades_df.copy()
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    daily_count = df.groupby('date').size().reset_index(name='count')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=daily_count['date'],
        y=daily_count['count'],
        marker=dict(color='#00D9FF'),
        name='Trades'
    ))
    
    fig.update_layout(
        title="📊 Volumen de Trades por Día",
        xaxis_title="Fecha",
        yaxis_title="Número de Trades",
        template='plotly_dark',
        height=400
    )
    
    return fig


def create_hourly_heatmap(trades_df: pd.DataFrame) -> go.Figure:
    """
    Crea heatmap de win rate por hora del día
    
    Args:
        trades_df: DataFrame con trades
    
    Returns:
        Plotly Figure
    """
    if trades_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No hay datos", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    # Extraer hora
    df = trades_df.copy()
    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
    df['won'] = (df['pnl'] > 0).astype(int)
    
    # Calcular win rate por hora
    hourly_stats = df.groupby('hour').agg({
        'won': 'mean',
        'pnl': 'count'
    }).reset_index()
    hourly_stats['win_rate'] = hourly_stats['won'] * 100
    
    # Crear todas las horas del día de trading (10-17)
    all_hours = list(range(10, 18))
    for hour in all_hours:
        if hour not in hourly_stats['hour'].values:
            hourly_stats = pd.concat([
                hourly_stats,
                pd.DataFrame({'hour': [hour], 'win_rate': [0], 'pnl': [0]})
            ])
    
    hourly_stats = hourly_stats.sort_values('hour')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=[f"{h}:00" for h in hourly_stats['hour']],
        y=hourly_stats['win_rate'],
        marker=dict(
            color=hourly_stats['win_rate'],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Win Rate %")
        ),
        text=[f"{wr:.1f}%" for wr in hourly_stats['win_rate']],
        textposition='auto',
        name='Win Rate'
    ))
    
    fig.add_hline(y=50, line_dash="dash", line_color="white", opacity=0.5)
    
    fig.update_layout(
        title="🕐 Win Rate por Hora del Día",
        xaxis_title="Hora",
        yaxis_title="Win Rate (%)",
        template='plotly_dark',
        height=400
    )
    
    return fig


def create_symbol_radar(trades_df: pd.DataFrame) -> go.Figure:
    """
    Crea gráfica radar comparando símbolos
    
    Args:
        trades_df: DataFrame con trades
    
    Returns:
        Plotly Figure
    """
    if trades_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No hay datos", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    # Calcular métricas por símbolo
    stats = []
    for symbol in trades_df['symbol'].unique():
        symbol_trades = trades_df[trades_df['symbol'] == symbol]
        
        winners = symbol_trades[symbol_trades['pnl'] > 0]
        losers = symbol_trades[symbol_trades['pnl'] <= 0]
        
        win_rate = (len(winners) / len(symbol_trades) * 100) if len(symbol_trades) > 0 else 0
        avg_win = winners['pnl'].mean() if len(winners) > 0 else 0
        avg_loss = abs(losers['pnl'].mean()) if len(losers) > 0 else 1
        profit_factor = avg_win / avg_loss if avg_loss > 0 else 0
        
        # Normalizar métricas a escala 0-100
        stats.append({
            'symbol': symbol,
            'Win Rate': win_rate,
            'Profit Factor': min(profit_factor * 20, 100),  # Escalar a 0-100
            'Avg Profit': min(avg_win / 10, 100),  # Ajustar escala
            'Trades': min(len(symbol_trades) * 5, 100),  # Escalar
            'Total P&L': min((symbol_trades['pnl'].sum() / 1000) * 10, 100)  # Escalar
        })
    
    fig = go.Figure()
    
    categories = ['Win Rate', 'Profit Factor', 'Avg Profit', 'Trades', 'Total P&L']
    
    for stat in stats:
        values = [stat[cat] for cat in categories]
        values.append(values[0])  # Cerrar el polígono
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            name=stat['symbol']
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        title="🎯 Análisis Radar por Símbolo",
        template='plotly_dark',
        height=500
    )
    
    return fig

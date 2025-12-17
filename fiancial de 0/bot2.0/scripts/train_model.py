"""
Script para entrenar el agente de Reinforcement Learning
"""

import sys
import os

# Agregar directorio raíz al path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

import argparse
from datetime import datetime, timedelta

from src.ai.rl_agent import RLAgent
from src.api.mock_iol_client import MockIOLClient
from src.analysis.technical_indicators import TechnicalIndicators
from src.utils.logger import log


def main():
    parser = argparse.ArgumentParser(description='Entrenar agente PPO')
    parser.add_argument('--symbols', type=str, default='GGAL,YPFD', 
                       help='Símbolos separados por coma')
    parser.add_argument('--timesteps', type=int, default=100000,
                       help='Pasos totales de entrenamiento')
    parser.add_argument('--days', type=int, default=365,
                       help='Días de datos históricos')
    
    args = parser.parse_args()
    
    symbols = args.symbols.split(',')
    
    log.info("🚀 Iniciando entrenamiento del agente PPO...")
    log.info(f"Símbolos: {symbols}")
    log.info(f"Timesteps: {args.timesteps}")
    
    # Crear cliente mock para obtener datos
    client = MockIOLClient("", "", "", initial_capital=100000)
    ti = TechnicalIndicators()
    
    # Obtener datos históricos simulados
    to_date = datetime.now()
    from_date = to_date - timedelta(days=args.days)
    
    log.info(f"Obteniendo datos históricos ({args.days} días)...")
    df = client.get_historical_data(symbols[0], from_date, to_date)
    
    if df is None or len(df) < 50:
        log.error("❌ No se pudieron obtener datos suficientes")
        return
    
    # Calcular indicadores
    log.info("Calculando indicadores técnicos...")
    df = ti.calculate_all_indicators(df)
    df = df.dropna()
    
    # Agregar columna de sentimiento (simulado)
    df['sentiment'] = 0.0
    
    log.info(f"✓ Dataset preparado: {len(df)} filas")
    
    # Crear y entrenar agente
    agent = RLAgent()
    
    log.info("🤖 Entrenando agente...")
    agent.train(df, total_timesteps=args.timesteps)
    
    # Evaluar
    log.info("📊 Evaluando rendimiento...")
    metrics = agent.evaluate(df)
    
    log.info("\n" + "="*60)
    log.info("📈 RESULTADOS DEL ENTRENAMIENTO")
    log.info("="*60)
    log.info(f"Total Reward: {metrics['total_reward']:.2f}")
    log.info(f"Valor Final: ${metrics['final_value']:,.2f}")
    log.info(f"Retorno: {metrics['total_return_pct']:.2f}%")
    log.info(f"Pasos: {metrics['steps']}")
    log.info("="*60)
    
    log.info("✓ Entrenamiento completado exitosamente")


if __name__ == "__main__":
    main()

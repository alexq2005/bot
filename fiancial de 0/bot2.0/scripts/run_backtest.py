"""
Script para ejecutar backtesting
"""

import sys
import os

# Agregar directorio raíz al path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

import argparse
from datetime import datetime, timedelta

from src.backtest.backtester import Backtester
from src.api.mock_iol_client import MockIOLClient
from src.analysis.signal_generator import SignalGenerator
from src.strategy.hybrid_strategy import HybridStrategy
from src.utils.logger import log


def main():
    parser = argparse.ArgumentParser(description='Ejecutar backtest de estrategia')
    parser.add_argument('--symbols', type=str, default='GGAL,YPFD',
                       help='Símbolos separados por coma')
    parser.add_argument('--days', type=int, default=365,
                       help='Días de datos históricos')
    parser.add_argument('--capital', type=float, default=100000,
                       help='Capital inicial')
    parser.add_argument('--commission', type=float, default=0.001,
                       help='Comisión (0.001 = 0.1%)')
    
    args = parser.parse_args()
    
    symbols = args.symbols.split(',')
    
    log.info("🔬 Iniciando Backtest...")
    log.info(f"Símbolos: {symbols}")
    log.info(f"Período: {args.days} días")
    log.info(f"Capital: ${args.capital:,.2f}")
    
    # Crear cliente mock para obtener datos
    client = MockIOLClient("", "", "", initial_capital=args.capital)
    
    # Obtener datos históricos
    to_date = datetime.now()
    from_date = to_date - timedelta(days=args.days)
    
    data = {}
    for symbol in symbols:
        log.info(f"Obteniendo datos de {symbol}...")
        df = client.get_historical_data(symbol, from_date, to_date)
        
        if df is not None and len(df) >= 50:
            data[symbol] = df
            log.info(f"✓ {symbol}: {len(df)} días de datos")
        else:
            log.warning(f"⚠ {symbol}: Datos insuficientes")
    
    if not data:
        log.error("❌ No se pudieron obtener datos")
        return
    
    # Crear estrategia
    signal_generator = SignalGenerator()
    strategy = HybridStrategy(
        signal_generator=signal_generator,
        use_sentiment=False  # Desactivar sentimiento para backtest
    )
    
    # Crear backtester
    backtester = Backtester(
        initial_capital=args.capital,
        commission=args.commission
    )
    
    # Ejecutar backtest
    results = backtester.run(data, strategy)
    
    # Mostrar resultados
    backtester.print_results(results)
    
    # Guardar resultados
    equity_df = results['equity_curve']
    output_file = f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    equity_df.to_csv(output_file, index=False)
    log.info(f"\n✓ Resultados guardados en: {output_file}")


if __name__ == "__main__":
    main()

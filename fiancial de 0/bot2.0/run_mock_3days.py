"""
3-Day Mock Trading Runner
Script para ejecutar el bot en modo MOCK durante 3 días consecutivos

IMPORTANTE: En Windows, ejecutar así:
    export PYTHONIOENCODING=utf-8 && python run_mock_3days.py
"""

import sys
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.bot.trading_bot import TradingBot
from src.bot.config import settings
from src.utils.logger import log


def run_mock_trading_session():
    """
    Ejecuta una sesión de trading en modo MOCK
    
    Configuración:
    - Símbolos: GGAL, YPFD, CEPU (optimizados)
    - Modo: MOCK (sin dinero real)
    - Duración: 3 días
    - Intervalo: 60 segundos entre ciclos
    """
    
    print("="*70)
    print("BOT TRADING - MODO MOCK (3 DIAS)")
    print("="*70)
    print(f"Inicio: {datetime.now()}")
    print(f"Fin programado: {datetime.now() + timedelta(days=3)}")
    print(f"Simbolos: GGAL, YPFD, CEPU")
    print(f"Intervalo: 60 segundos")
    print("="*70)
    
    # Verificar que esté en modo MOCK
    if not settings.mock_mode:
        print("\n[WARNING] El bot NO esta en modo MOCK!")
        print("Para activar modo MOCK:")
        print("1. Edita el archivo .env")
        print("2. Cambia: MOCK_MODE=true")
        print("3. Reinicia este script")
        return
    
    print("\n[OK] Modo MOCK activado (sin riesgo de dinero real)\n")
    
    # Configurar símbolos
    symbols = ['GGAL', 'YPFD', 'CEPU']
    
    try:
        # Inicializar bot
        print("[*] Inicializando bot...")
        bot = TradingBot()
        
        print("[OK] Bot inicializado correctamente\n")
        
        # Configurar duración
        end_time = datetime.now() + timedelta(days=3)
        iteration = 0
        
        print("[*] Iniciando trading loop...\n")
        
        # Loop principal
        while datetime.now() < end_time:
            iteration += 1
            
            print(f"\n{'='*70}")
            print(f"[ITERATION #{iteration}]")
            print(f"[TIME] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"[REMAINING] {end_time - datetime.now()}")
            print(f"{'='*70}\n")
            
            # Analizar cada símbolo
            for symbol in symbols:
                try:
                    print(f"[ANALYZE] {symbol}...")
                    decision = bot.analyze_symbol(symbol)
                    
                    if decision:
                        # Ejecutar trade (en MOCK)
                        result = bot.execute_trade(decision)
                        
                        if result:
                            print(f"[OK] {symbol}: Trade ejecutado (MOCK)")
                        else:
                            print(f"[SKIP] {symbol}: Trade rechazado por risk manager")
                    else:
                        print(f"[SKIP] {symbol}: No hay senal")
                    
                    # Pausa entre símbolos
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"[ERROR] Error analizando {symbol}: {e}")
                    log.error(f"Error en {symbol}: {e}")
            
            # Monitorear posiciones activas
            try:
                stats = bot.position_monitor.check_all_positions()
                if stats['checked'] > 0:
                    print(f"\n[MONITOR] {stats['checked']} posiciones | "
                          f"SL: {stats['closed_sl']} | TP: {stats['closed_tp']}")
            except Exception as e:
                print(f"[ERROR] Error monitoreando posiciones: {e}")
            
            # Mostrar resumen
            try:
                bot._show_portfolio_summary()
            except Exception as e:
                print(f"[ERROR] Error mostrando resumen: {e}")
            
            # Esperar hasta siguiente iteración
            print(f"\n[WAIT] Esperando 60 segundos...")
            time.sleep(60)
        
        print("\n" + "="*70)
        print("SESION DE 3 DIAS COMPLETADA")
        print("="*70)
        print(f"Total iteraciones: {iteration}")
        print(f"Fin: {datetime.now()}")
        print("\nUsa Bot Intelligence para analizar resultados")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n[ALERT] Sesion interrumpida por el usuario")
        print(f"Iteraciones completadas: {iteration}")
        print(f"Tiempo transcurrido: {datetime.now() - (end_time - timedelta(days=3))}")
        
    except Exception as e:
        print(f"\n[ERROR] Error fatal: {e}")
        log.error(f"Error fatal en mock trading: {e}")
        raise


if __name__ == "__main__":
    run_mock_trading_session()

"""
Easy Retrain Script
Nivel 4: Reentrenamiento Manual Mejorado
Script simplificado y amigable para reentrenar el modelo
"""

import sys
import os
from pathlib import Path

# Agregar directorio raíz al path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

import argparse
from datetime import datetime, timedelta
from colorama import init, Fore, Style

# Inicializar colorama
init(autoreset=True)

from src.ai.rl_agent import RLAgent
from src.api.mock_iol_client import MockIOLClient
from src.analysis.technical_indicators import TechnicalIndicators
from src.utils.model_ab_tester import ModelABTester
from src.utils.model_version_manager import ModelVersionManager
from src.utils.training_notifier import TrainingNotifier, NotificationLevel
from src.utils.logger import log


def print_banner():
    """Imprimir banner del script"""
    print("\n" + "="*70)
    print(Fore.CYAN + "🤖 REENTRENAMIENTO FÁCIL DE MODELO RL" + Style.RESET_ALL)
    print("="*70 + "\n")


def print_section(title):
    """Imprimir título de sección"""
    print("\n" + Fore.YELLOW + f"{'─'*70}")
    print(f"  {title}")
    print(f"{'─'*70}" + Style.RESET_ALL)


def print_success(message):
    """Imprimir mensaje de éxito"""
    print(Fore.GREEN + f"✅ {message}" + Style.RESET_ALL)


def print_error(message):
    """Imprimir mensaje de error"""
    print(Fore.RED + f"❌ {message}" + Style.RESET_ALL)


def print_info(message):
    """Imprimir mensaje informativo"""
    print(Fore.CYAN + f"ℹ️  {message}" + Style.RESET_ALL)


def get_training_data(symbol, days, client, ti):
    """Obtener y preparar datos de entrenamiento"""
    print_section("1️⃣  PREPARANDO DATOS DE ENTRENAMIENTO")
    
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)
    
    print(f"   📅 Período: {from_date.date()} a {to_date.date()}")
    print(f"   📊 Símbolo: {symbol}")
    print(f"   🗓️  Días: {days}")
    
    # Obtener datos históricos
    print("\n   Obteniendo datos históricos...")
    df = client.get_historical_data(symbol, from_date, to_date)
    
    if df is None or len(df) < 50:
        print_error("No se pudieron obtener datos suficientes")
        return None
    
    print_success(f"Datos obtenidos: {len(df)} filas")
    
    # Calcular indicadores
    print("   Calculando indicadores técnicos...")
    df = ti.calculate_all_indicators(df)
    df = df.dropna()
    
    # Agregar sentimiento (simulado)
    df['sentiment'] = 0.0
    
    print_success(f"Dataset preparado: {len(df)} filas con indicadores")
    
    return df


def train_new_model(df, timesteps, agent, notifier, symbol):
    """Entrenar nuevo modelo"""
    print_section("2️⃣  ENTRENANDO NUEVO MODELO")
    
    print(f"   🎯 Timesteps: {timesteps:,}")
    print(f"   📈 Algoritmo: PPO (Proximal Policy Optimization)")
    
    print("\n   " + Fore.YELLOW + "Entrenando... (esto puede tomar varios minutos)" + Style.RESET_ALL)
    
    # Notificar inicio
    notifier.notify_training_start(timesteps, symbol)
    
    import time
    start_time = time.time()
    
    agent.train(df, total_timesteps=timesteps)
    
    duration = time.time() - start_time
    
    print_success(f"Entrenamiento completado en {duration:.1f}s")
    
    return agent, duration


def evaluate_model(df, agent):
    """Evaluar modelo"""
    print_section("3️⃣  EVALUANDO MODELO")
    
    print("   Ejecutando evaluación...")
    metrics = agent.evaluate(df)
    
    print("\n   " + Fore.CYAN + "Métricas de Rendimiento:" + Style.RESET_ALL)
    print(f"   💰 Total Return: {metrics.get('total_return_pct', 0):+.2f}%")
    print(f"   💵 Valor Final: ${metrics.get('final_value', 0):,.2f}")
    print(f"   📊 Total Reward: {metrics.get('total_reward', 0):.2f}")
    print(f"   🔢 Steps: {metrics.get('steps', 0)}")
    
    return metrics


def compare_with_current(new_agent_path, validation_data):
    """Comparar nuevo modelo con el actual"""
    print_section("4️⃣  COMPARANDO CON MODELO ACTUAL (A/B TEST)")
    
    current_model_path = "./models/ppo_trading_agent"
    
    # Verificar si existe modelo actual
    if not os.path.exists(f"{current_model_path}.zip"):
        print_info("No hay modelo actual para comparar")
        print_info("El nuevo modelo será el modelo principal")
        return {'use_new_model': True, 'reason': 'No existing model'}
    
    print("   Ejecutando A/B test...")
    
    tester = ModelABTester(validation_episodes=5)
    
    # Realizar comparación
    result = tester.auto_replace_if_better(
        current_model_path,
        new_agent_path,
        validation_data,
        backup=True
    )
    
    if result['success']:
        if result['replaced']:
            print_success("Nuevo modelo es mejor - Reemplazado automáticamente")
        else:
            print_info("Modelo actual es mejor - Sin cambios")
    
    return result


def interactive_mode():
    """Modo interactivo para usuarios"""
    print_banner()
    print(Fore.CYAN + "Modo Interactivo - Responde las siguientes preguntas:\n" + Style.RESET_ALL)
    
    # Preguntar parámetros
    try:
        symbol = input("📊 ¿Qué símbolo entrenar? (default: GGAL): ").strip() or "GGAL"
        days = int(input("🗓️  ¿Cuántos días de datos? (default: 365): ").strip() or "365")
        timesteps = int(input("🎯 ¿Cuántos timesteps? (default: 50000): ").strip() or "50000")
        
        compare = input("\n🔍 ¿Comparar con modelo actual y reemplazar si es mejor? (S/n): ").strip().lower()
        do_compare = compare != 'n'
        
        print("\n" + Fore.GREEN + "Iniciando reentrenamiento con los siguientes parámetros:" + Style.RESET_ALL)
        print(f"  Símbolo: {symbol}")
        print(f"  Días: {days}")
        print(f"  Timesteps: {timesteps:,}")
        print(f"  Comparar: {'Sí' if do_compare else 'No'}")
        
        input("\nPresiona ENTER para continuar...")
        
        return {
            'symbol': symbol,
            'days': days,
            'timesteps': timesteps,
            'compare': do_compare
        }
        
    except KeyboardInterrupt:
        print("\n\n❌ Cancelado por el usuario")
        sys.exit(0)
    except Exception as e:
        print_error(f"Error en entrada: {e}")
        sys.exit(1)


def main():
    # Inicializar sistemas mejorados
    notifier = TrainingNotifier()
    version_manager = ModelVersionManager()
    
    parser = argparse.ArgumentParser(
        description='Reentrenamiento fácil del agente PPO',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  
  # Modo interactivo (recomendado para principiantes)
  python scripts/easy_retrain.py
  
  # Entrenamiento rápido (10k timesteps)
  python scripts/easy_retrain.py --quick
  
  # Entrenamiento completo con comparación
  python scripts/easy_retrain.py --timesteps 100000 --compare
  
  # Usar datos específicos
  python scripts/easy_retrain.py --symbol YPFD --days 180 --timesteps 50000
        """
    )
    
    parser.add_argument('--symbol', type=str, default=None,
                       help='Símbolo a entrenar (default: GGAL)')
    parser.add_argument('--days', type=int, default=None,
                       help='Días de datos históricos (default: 365)')
    parser.add_argument('--timesteps', type=int, default=None,
                       help='Timesteps de entrenamiento (default: 50000)')
    parser.add_argument('--compare', action='store_true',
                       help='Comparar con modelo actual usando A/B testing')
    parser.add_argument('--quick', action='store_true',
                       help='Entrenamiento rápido (10k timesteps)')
    parser.add_argument('--interactive', action='store_true',
                       help='Modo interactivo')
    
    args = parser.parse_args()
    
    # Si no hay argumentos, usar modo interactivo
    if len(sys.argv) == 1 or args.interactive:
        params = interactive_mode()
        symbol = params['symbol']
        days = params['days']
        timesteps = params['timesteps']
        compare = params['compare']
    else:
        print_banner()
        symbol = args.symbol or 'GGAL'
        days = args.days or 365
        timesteps = args.timesteps or (10000 if args.quick else 50000)
        compare = args.compare
    
    # Crear cliente mock para obtener datos
    client = MockIOLClient("", "", "", initial_capital=100000)
    ti = TechnicalIndicators()
    
    # 1. Obtener datos
    df = get_training_data(symbol, days, client, ti)
    if df is None:
        sys.exit(1)
    
    # 2. Crear agente temporal para entrenamiento
    temp_model_path = f"./models/temp_ppo_agent_{int(datetime.now().timestamp())}"
    agent = RLAgent(model_path=temp_model_path)
    
    # 3. Entrenar
    agent, duration = train_new_model(df, timesteps, agent, notifier, symbol)
    
    # 4. Evaluar
    metrics = evaluate_model(df, agent)
    
    # Notificar fin de entrenamiento
    notifier.notify_training_complete(duration, metrics)
    
    # 5. Comparar con modelo actual si se solicita
    if compare:
        result = compare_with_current(temp_model_path, df)
        
        # Notificar resultado de A/B test
        if result.get('success'):
            improvement = result.get('comparison', {}).get('comparison', {}).get('improvement_return_pct', 0)
            notifier.notify_ab_test_result(result.get('replaced', False), improvement)
        
        if not result.get('replaced', False) and result.get('success', False):
            # Preguntar si guardar de todas formas
            print("\n" + Fore.YELLOW + "El nuevo modelo no es mejor que el actual." + Style.RESET_ALL)
            save_anyway = input("¿Deseas guardarlo de todas formas? (s/N): ").strip().lower()
            
            if save_anyway == 's':
                import shutil
                version_id = version_manager.save_version(
                    temp_model_path,
                    metrics,
                    tag="manual_backup",
                    notes=f"Entrenado manualmente con {timesteps} timesteps"
                )
                notifier.notify_version_saved(version_id, "manual_backup")
                print_success(f"Modelo guardado como versión {version_id}")
        elif result.get('replaced', False):
            # Guardar versión si fue reemplazado
            version_id = version_manager.save_version(
                "./models/ppo_trading_agent",
                metrics,
                tag="production",
                notes=f"Modelo mejorado tras A/B test (+{improvement:.1f}%)"
            )
            notifier.notify_version_saved(version_id, "production")
    else:
        # Si no se compara, guardar como modelo principal
        print_section("4️⃣  GUARDANDO MODELO")
        import shutil
        os.makedirs("./models", exist_ok=True)
        shutil.copy(f"{temp_model_path}.zip", "./models/ppo_trading_agent.zip")
        
        # Guardar versión
        version_id = version_manager.save_version(
            "./models/ppo_trading_agent",
            metrics,
            tag="manual",
            notes=f"Entrenado manualmente con {timesteps} timesteps"
        )
        notifier.notify_version_saved(version_id, "manual")
        print_success(f"Modelo guardado como versión {version_id}")
    
    # Resumen final
    print("\n" + "="*70)
    print(Fore.GREEN + "✅ PROCESO COMPLETADO" + Style.RESET_ALL)
    print("="*70)
    print(f"\n📊 Resumen:")
    print(f"   Símbolo: {symbol}")
    print(f"   Timesteps: {timesteps:,}")
    print(f"   Return: {metrics.get('total_return_pct', 0):+.2f}%")
    print(f"   Modelo guardado: {compare and result.get('replaced', False)}")
    print("\n" + Fore.CYAN + "🎉 ¡Listo para usar el bot con el nuevo modelo!" + Style.RESET_ALL)
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelado por el usuario")
        sys.exit(0)
    except Exception as e:
        print_error(f"Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

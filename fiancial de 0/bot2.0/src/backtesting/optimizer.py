
import itertools
import pandas as pd
from typing import List, Dict, Callable, Any
from .engine import BacktestEngine, BacktestResult

class StrategyOptimizer:
    """Optimizador de estrategias mediante Grid Search"""
    
    def __init__(self, initial_capital: float = 1000000.0, commission: float = 0.005):
        self.engine = BacktestEngine(initial_capital, commission)
        
    def optimize(self, 
                 data: pd.DataFrame, 
                 strategy_func: Callable, 
                 param_grid: Dict[str, List[Any]]) -> pd.DataFrame:
        """
        Ejecuta optimización probando todas las combinaciones de parámetros.
        
        Args:
            data: DataFrame de datos históricos
            strategy_func: Función de estrategia que acepta (row, context) Y parámetros **kwargs
            param_grid: Diccionario con listas de valores a probar {param: [v1, v2], ...}
            
        Returns:
            DataFrame con resultados ordenados por Retorno Total
        """
        # Generar todas las combinaciones
        keys = param_grid.keys()
        values = param_grid.values()
        combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
        
        results = []
        
        print(f"🔄 Iniciando optimización: {len(combinations)} combinaciones...")
        
        # Iterar combinaciones
        for params in combinations:
            # Crear wrapper de estrategia con parámetros fijos
            def strategy_wrapper(row, context):
                # Inyectar params en el contexto o usar partial?
                # La estrategia debe aceptar **params, asi que...
                # Pero el engine pasa (row, context).
                # Necesitamos un closure.
                return strategy_func(row, context, **params)
            
            # Ejecutar Backtest
            try:
                bt_result = self.engine.run(data, strategy_wrapper)
                
                # Guardar métricas
                res_dict = params.copy()
                res_dict.update({
                    'total_return_pct': bt_result.total_return_pct,
                    'win_rate': bt_result.win_rate,
                    'sharpe_ratio': bt_result.sharpe_ratio,
                    'max_drawdown': bt_result.max_drawdown,
                    'trades': bt_result.total_trades
                })
                results.append(res_dict)
                
            except Exception as e:
                print(f"❌ Error optimizando params {params}: {e}")
                
        # Crear DataFrame de resultados
        results_df = pd.DataFrame(results)
        
        if not results_df.empty:
            # Ordenar por retorno
            results_df = results_df.sort_values(by='total_return_pct', ascending=False)
            
        return results_df

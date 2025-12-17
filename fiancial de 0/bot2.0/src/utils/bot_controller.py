"""
Bot Controller
Controla el inicio/parada del bot desde el dashboard
"""

import os
import signal
import subprocess
import psutil
import time
from typing import Optional, Dict
from pathlib import Path


class BotController:
    """
    Controlador del bot de trading
    Permite iniciar/detener el bot desde el dashboard
    """
    
    def __init__(self, pid_file: str = "data/bot.pid"):
        """
        Inicializa el controlador
        
        Args:
            pid_file: Archivo donde se guarda el PID del bot
        """
        self.pid_file = pid_file
        self.pid_dir = os.path.dirname(pid_file)
        
        # Crear directorio si no existe
        if self.pid_dir and not os.path.exists(self.pid_dir):
            os.makedirs(self.pid_dir)
    
    def is_running(self) -> bool:
        """
        Verifica si el bot está corriendo
        
        Returns:
            True si el bot está corriendo
        """
        pid = self.get_pid()
        
        if pid is None:
            return False
        
        try:
            # Verificar si el proceso existe
            process = psutil.Process(pid)
            
            # Verificar que sea realmente el bot
            cmdline = ' '.join(process.cmdline())
            if 'main.py' in cmdline or 'python' in cmdline.lower():
                return True
            else:
                # PID existe pero no es el bot, limpiar
                self._clear_pid()
                return False
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Proceso no existe, limpiar PID
            self._clear_pid()
            return False
    
    def get_pid(self) -> Optional[int]:
        """
        Obtiene el PID del bot
        
        Returns:
            PID del bot o None si no está corriendo
        """
        if not os.path.exists(self.pid_file):
            return None
        
        try:
            with open(self.pid_file, 'r') as f:
                return int(f.read().strip())
        except (ValueError, FileNotFoundError):
            return None
    
    def _save_pid(self, pid: int) -> bool:
        """
        Guarda el PID del bot
        
        Args:
            pid: PID a guardar
        
        Returns:
            True si se guardó correctamente
        """
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(pid))
            return True
        except Exception as e:
            print(f"❌ Error guardando PID: {e}")
            return False
    
    def _clear_pid(self) -> bool:
        """
        Elimina el archivo PID
        
        Returns:
            True si se eliminó correctamente
        """
        try:
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
            return True
        except Exception as e:
            print(f"❌ Error eliminando PID: {e}")
            return False
    
    def start(self) -> Dict[str, any]:
        """
        Inicia el bot ejecutando start_bot.bat (abre ventana CMD)
        
        Returns:
            Dict con resultado
        """
        if self.is_running():
            return {
                'success': False,
                'message': 'El bot ya está corriendo',
                'pid': self.get_pid()
            }
        
        try:
            import subprocess
            
            # Ejecutar start_bot.bat que abre ventana CMD
            if os.name == 'nt':  # Windows
                # Usar 'start' para abrir en nueva ventana
                subprocess.Popen(
                    'start cmd /k start_bot.bat',
                    shell=True
                )
                
                # Esperar un momento para que se cree el proceso
                import time
                time.sleep(2)
                
                # Buscar el PID del proceso python main.py
                import psutil
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['name'] == 'python.exe':
                            cmdline = ' '.join(proc.info['cmdline'] or [])
                            if 'main.py' in cmdline:
                                pid = proc.info['pid']
                                self._save_pid(pid)
                                return {
                                    'success': True,
                                    'message': 'Bot iniciado (ventana CMD abierta)',
                                    'pid': pid
                                }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                return {
                    'success': True,
                    'message': 'Bot iniciado (busca la ventana CMD)',
                    'pid': None
                }
            else:  # Linux/Mac
                # En Linux/Mac ejecutar directamente
                process = subprocess.Popen(
                    ['python', 'main.py'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                self._save_pid(process.pid)
                
                return {
                    'success': True,
                    'message': 'Bot iniciado',
                    'pid': process.pid
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error iniciando bot: {e}',
                'pid': None
            }
    
    def stop(self) -> Dict[str, any]:
        """
        Detiene el bot
        
        Returns:
            Dict con resultado
        """
        if not self.is_running():
            self._clear_pid()
            return {
                'success': False,
                'message': 'El bot no está corriendo',
                'pid': None
            }
        
        pid = self.get_pid()
        
        try:
            # Obtener proceso
            process = psutil.Process(pid)
            
            # Intentar terminar gracefully
            process.terminate()
            
            # Esperar hasta 5 segundos
            try:
                process.wait(timeout=5)
            except psutil.TimeoutExpired:
                # Si no termina, forzar
                process.kill()
            
            # Limpiar PID
            self._clear_pid()
            
            return {
                'success': True,
                'message': 'Bot detenido correctamente',
                'pid': pid
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error deteniendo bot: {e}',
                'pid': pid
            }
    
    def restart(self) -> Dict[str, any]:
        """
        Reinicia el bot
        
        Returns:
            Dict con resultado
        """
        # Detener si está corriendo
        if self.is_running():
            stop_result = self.stop()
            if not stop_result['success']:
                return stop_result
        
        # Esperar un momento
        import time
        time.sleep(1)
        
        # Iniciar
        return self.start()
    
    def get_status(self) -> Dict[str, any]:
        """
        Obtiene estado del bot
        
        Returns:
            Dict con estado
        """
        is_running = self.is_running()
        pid = self.get_pid() if is_running else None
        
        status = {
            'running': is_running,
            'pid': pid,
            'status': 'RUNNING' if is_running else 'STOPPED'
        }
        
        if is_running and pid:
            try:
                process = psutil.Process(pid)
                status['cpu_percent'] = process.cpu_percent()
                status['memory_mb'] = process.memory_info().rss / 1024 / 1024
                status['uptime_seconds'] = time.time() - process.create_time()
            except:
                pass
        
        return status


# Instancia global
bot_controller = BotController()

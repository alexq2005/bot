"""
Telegram Service Manager
Gestiona el servicio de Telegram como proceso único
"""

import os
import subprocess
import psutil
from pathlib import Path


class TelegramServiceManager:
    """
    Gestor del servicio de Telegram
    Asegura que solo haya una instancia corriendo
    """
    
    def __init__(self, pid_file: str = "data/telegram.pid"):
        """
        Inicializa el gestor
        
        Args:
            pid_file: Archivo donde se guarda el PID
        """
        self.pid_file = pid_file
        self.pid_dir = os.path.dirname(pid_file)
        
        # Crear directorio si no existe
        if self.pid_dir and not os.path.exists(self.pid_dir):
            os.makedirs(self.pid_dir)
    
    def is_running(self) -> bool:
        """
        Verifica si el servicio está corriendo
        
        Returns:
            True si está corriendo
        """
        pid = self.get_pid()
        
        if pid is None:
            return False
        
        try:
            process = psutil.Process(pid)
            cmdline = ' '.join(process.cmdline())
            
            if 'telegram' in cmdline.lower():
                return True
            else:
                self._clear_pid()
                return False
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            self._clear_pid()
            return False
    
    def get_pid(self) -> int:
        """
        Obtiene el PID del servicio
        
        Returns:
            PID o None
        """
        if not os.path.exists(self.pid_file):
            return None
        
        try:
            with open(self.pid_file, 'r') as f:
                return int(f.read().strip())
        except (ValueError, FileNotFoundError):
            return None
    
    def _save_pid(self, pid: int):
        """Guarda el PID"""
        with open(self.pid_file, 'w') as f:
            f.write(str(pid))
    
    def _clear_pid(self):
        """Elimina el archivo PID"""
        if os.path.exists(self.pid_file):
            os.remove(self.pid_file)
    
    def start(self) -> dict:
        """
        Inicia el servicio de Telegram
        
        Returns:
            Dict con resultado
        """
        if self.is_running():
            return {
                'success': False,
                'message': 'Servicio de Telegram ya está corriendo',
                'pid': self.get_pid()
            }
        
        try:
            # Iniciar servicio
            process = subprocess.Popen(
                ['python', 'src/notifications/telegram_service.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            self._save_pid(process.pid)
            
            return {
                'success': True,
                'message': 'Servicio de Telegram iniciado',
                'pid': process.pid
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {e}',
                'pid': None
            }
    
    def stop(self) -> dict:
        """
        Detiene el servicio
        
        Returns:
            Dict con resultado
        """
        if not self.is_running():
            self._clear_pid()
            return {
                'success': False,
                'message': 'Servicio no está corriendo'
            }
        
        pid = self.get_pid()
        
        try:
            process = psutil.Process(pid)
            process.terminate()
            
            try:
                process.wait(timeout=5)
            except psutil.TimeoutExpired:
                process.kill()
            
            self._clear_pid()
            
            return {
                'success': True,
                'message': 'Servicio detenido'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {e}'
            }


# Instancia global
telegram_service_manager = TelegramServiceManager()

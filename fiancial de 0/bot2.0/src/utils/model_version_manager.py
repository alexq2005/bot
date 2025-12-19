"""
Model Version Manager
Sistema de control de versiones para modelos ML
Permite rollback, comparación entre versiones y gestión avanzada
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import hashlib

from ..utils.logger import log


class ModelVersionManager:
    """
    Gestor de versiones de modelos ML
    
    Funcionalidades:
    - Versionado automático de modelos
    - Rollback a versiones anteriores
    - Comparación de métricas entre versiones
    - Limpieza automática de versiones antiguas
    - Tags y anotaciones para cada versión
    """
    
    def __init__(
        self,
        models_dir: str = "./models",
        max_versions: int = 10,
        auto_cleanup: bool = True
    ):
        """
        Args:
            models_dir: Directorio base para modelos
            max_versions: Máximo de versiones a mantener
            auto_cleanup: Si limpiar automáticamente versiones antiguas
        """
        self.models_dir = Path(models_dir)
        self.versions_dir = self.models_dir / "versions"
        self.metadata_file = self.models_dir / "versions_metadata.json"
        self.max_versions = max_versions
        self.auto_cleanup = auto_cleanup
        
        # Crear directorios
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        
        # Cargar metadata
        self.metadata = self._load_metadata()
        
        log.info("[VERSION MANAGER] Inicializado")
        log.info(f"  Directorio: {self.models_dir}")
        log.info(f"  Máx versiones: {max_versions}")
    
    def _load_metadata(self) -> Dict:
        """Cargar metadata de versiones"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except:
                return {'versions': [], 'current': None}
        return {'versions': [], 'current': None}
    
    def _save_metadata(self):
        """Guardar metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2, default=str)
    
    def _calculate_checksum(self, filepath: Path) -> str:
        """Calcular checksum de archivo"""
        md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()
    
    def save_version(
        self,
        model_path: str,
        metrics: Dict,
        tag: Optional[str] = None,
        notes: str = ""
    ) -> str:
        """
        Guardar nueva versión del modelo
        
        Args:
            model_path: Path al modelo a guardar
            metrics: Métricas de performance
            tag: Tag opcional (ej: "production", "best")
            notes: Notas sobre esta versión
        
        Returns:
            version_id: ID de la versión guardada
        """
        timestamp = datetime.now()
        version_id = timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Crear directorio para esta versión
        version_dir = self.versions_dir / version_id
        version_dir.mkdir(exist_ok=True)
        
        # Copiar modelo
        model_file = Path(model_path + ".zip")
        if not model_file.exists():
            log.error(f"Modelo no encontrado: {model_file}")
            return None
        
        dest_file = version_dir / f"model_{version_id}.zip"
        shutil.copy(model_file, dest_file)
        
        # Calcular checksum
        checksum = self._calculate_checksum(dest_file)
        
        # Crear metadata de versión
        version_info = {
            'version_id': version_id,
            'timestamp': timestamp.isoformat(),
            'model_file': str(dest_file),
            'checksum': checksum,
            'metrics': metrics,
            'tag': tag,
            'notes': notes,
            'size_bytes': dest_file.stat().st_size
        }
        
        # Agregar a metadata
        self.metadata['versions'].append(version_info)
        self.metadata['current'] = version_id
        
        # Guardar
        self._save_metadata()
        
        log.info(f"✅ Versión guardada: {version_id}")
        if tag:
            log.info(f"   Tag: {tag}")
        log.info(f"   Métricas: {metrics}")
        
        # Limpieza automática
        if self.auto_cleanup:
            self._cleanup_old_versions()
        
        return version_id
    
    def _cleanup_old_versions(self):
        """Limpiar versiones antiguas manteniendo solo las últimas N"""
        if len(self.metadata['versions']) > self.max_versions:
            # Ordenar por timestamp
            versions = sorted(
                self.metadata['versions'],
                key=lambda x: x['timestamp'],
                reverse=True
            )
            
            # Mantener solo las últimas N
            to_keep = versions[:self.max_versions]
            to_delete = versions[self.max_versions:]
            
            # Eliminar versiones antiguas
            for version in to_delete:
                version_dir = Path(version['model_file']).parent
                if version_dir.exists():
                    shutil.rmtree(version_dir)
                    log.info(f"🗑️  Versión eliminada: {version['version_id']}")
            
            # Actualizar metadata
            self.metadata['versions'] = to_keep
            self._save_metadata()
    
    def get_version(self, version_id: str) -> Optional[Dict]:
        """Obtener información de una versión"""
        for version in self.metadata['versions']:
            if version['version_id'] == version_id:
                return version
        return None
    
    def get_current_version(self) -> Optional[Dict]:
        """Obtener versión actual"""
        if self.metadata['current']:
            return self.get_version(self.metadata['current'])
        return None
    
    def list_versions(self, limit: int = None) -> List[Dict]:
        """Listar todas las versiones"""
        versions = sorted(
            self.metadata['versions'],
            key=lambda x: x['timestamp'],
            reverse=True
        )
        
        if limit:
            return versions[:limit]
        return versions
    
    def rollback(self, version_id: str, target_path: str) -> bool:
        """
        Hacer rollback a una versión anterior
        
        Args:
            version_id: ID de la versión a restaurar
            target_path: Path donde copiar el modelo
        
        Returns:
            bool: True si éxito
        """
        version = self.get_version(version_id)
        if not version:
            log.error(f"Versión no encontrada: {version_id}")
            return False
        
        # Backup del modelo actual
        current_file = Path(target_path + ".zip")
        if current_file.exists():
            backup_file = current_file.with_suffix(f".backup_{int(datetime.now().timestamp())}.zip")
            shutil.copy(current_file, backup_file)
            log.info(f"📦 Backup creado: {backup_file.name}")
        
        # Copiar versión anterior
        source_file = Path(version['model_file'])
        shutil.copy(source_file, current_file)
        
        # Actualizar current
        self.metadata['current'] = version_id
        self._save_metadata()
        
        log.info(f"⏪ Rollback exitoso a versión: {version_id}")
        log.info(f"   Fecha: {version['timestamp']}")
        log.info(f"   Métricas: {version['metrics']}")
        
        return True
    
    def compare_versions(
        self,
        version_id_1: str,
        version_id_2: str
    ) -> Dict:
        """
        Comparar dos versiones
        
        Returns:
            dict con comparación de métricas
        """
        v1 = self.get_version(version_id_1)
        v2 = self.get_version(version_id_2)
        
        if not v1 or not v2:
            log.error("Una o ambas versiones no encontradas")
            return {}
        
        # Comparar métricas
        m1 = v1.get('metrics', {})
        m2 = v2.get('metrics', {})
        
        comparison = {
            'version_1': {
                'id': version_id_1,
                'timestamp': v1['timestamp'],
                'metrics': m1
            },
            'version_2': {
                'id': version_id_2,
                'timestamp': v2['timestamp'],
                'metrics': m2
            },
            'differences': {}
        }
        
        # Calcular diferencias
        for key in m1.keys():
            if key in m2:
                diff = m2[key] - m1[key]
                comparison['differences'][key] = {
                    'v1': m1[key],
                    'v2': m2[key],
                    'difference': diff,
                    'improvement_pct': (diff / m1[key] * 100) if m1[key] != 0 else 0
                }
        
        return comparison
    
    def tag_version(self, version_id: str, tag: str):
        """Agregar tag a una versión"""
        for version in self.metadata['versions']:
            if version['version_id'] == version_id:
                version['tag'] = tag
                self._save_metadata()
                log.info(f"🏷️  Tag '{tag}' agregado a versión {version_id}")
                return True
        return False
    
    def get_best_version(self, metric: str = 'total_return_pct') -> Optional[Dict]:
        """Obtener la mejor versión según una métrica"""
        if not self.metadata['versions']:
            return None
        
        best = max(
            self.metadata['versions'],
            key=lambda x: x.get('metrics', {}).get(metric, float('-inf'))
        )
        
        return best
    
    def get_summary(self) -> Dict:
        """Obtener resumen del estado de versiones"""
        versions = self.metadata['versions']
        
        if not versions:
            return {
                'total_versions': 0,
                'current_version': None,
                'total_size_mb': 0
            }
        
        total_size = sum(v.get('size_bytes', 0) for v in versions)
        
        # Mejor versión por métrica
        best_return = self.get_best_version('total_return_pct')
        
        summary = {
            'total_versions': len(versions),
            'current_version': self.metadata['current'],
            'total_size_mb': total_size / (1024 * 1024),
            'oldest_version': min(versions, key=lambda x: x['timestamp'])['version_id'],
            'newest_version': max(versions, key=lambda x: x['timestamp'])['version_id'],
            'best_version': best_return['version_id'] if best_return else None,
            'best_return': best_return.get('metrics', {}).get('total_return_pct') if best_return else None
        }
        
        return summary
    
    def export_version_history(self, filepath: str):
        """Exportar historial de versiones a JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.metadata, f, indent=2, default=str)
        log.info(f"📄 Historial exportado a: {filepath}")

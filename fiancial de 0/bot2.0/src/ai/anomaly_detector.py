"""
Anomaly Detection with Variational Autoencoder
Detección de comportamientos anómalos en datos de trading
"""

import numpy as np
import torch
import torch.nn as nn
from typing import Dict, Tuple, Optional
import pandas as pd
from datetime import datetime


class VariationalAutoencoder(nn.Module):
    """VAE para detección de anomalías en series temporales"""
    
    def __init__(
        self,
        input_dim: int = 10,      # Features: OHLCV + indicadores
        latent_dim: int = 5,
        hidden_dim: int = 64,
        device: str = 'cpu'
    ):
        super().__init__()
        
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.device = device
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        
        self.fc_mu = nn.Linear(hidden_dim, latent_dim)
        self.fc_logvar = nn.Linear(hidden_dim, latent_dim)
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
            nn.Sigmoid()  # Output entre 0-1
        )
        
        self.to(device)
    
    def encode(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Encode a distribución gaussiana"""
        h = self.encoder(x)
        mu = self.fc_mu(h)
        logvar = self.fc_logvar(h)
        return mu, logvar
    
    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        """Sampling using reparameterization trick"""
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        z = mu + eps * std
        return z
    
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Decode desde latent space"""
        return self.decoder(z)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Forward pass"""
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        recon_x = self.decode(z)
        return recon_x, mu, logvar
    
    def get_reconstruction_error(self, x: torch.Tensor) -> float:
        """Obtener error de reconstrucción (anomaly score)"""
        with torch.no_grad():
            recon_x, _, _ = self.forward(x)
            mse = nn.MSELoss()(recon_x, x)
        return float(mse.item())


class AnomalyDetector:
    """
    Detector de anomalías con múltiples estrategias:
    1. Reconstrucción VAE
    2. Desviación de volatilidad
    3. Detección de gaps
    4. Correlación anómala
    """
    
    def __init__(
        self,
        vae: Optional[VariationalAutoencoder] = None,
        sensitivity: float = 2.0,  # Desviaciones estándar
        device: str = 'cpu'
    ):
        """
        Args:
            vae: Modelo VAE entrenado
            sensitivity: Sensibilidad para detección
            device: 'cpu' o 'cuda'
        """
        self.vae = vae
        self.sensitivity = sensitivity
        self.device = device
        
        # Histórico para calcular estadísticas
        self.history = {
            'prices': [],
            'volatilities': [],
            'returns': [],
            'reconstruction_errors': []
        }
        
        self.thresholds = {
            'volatility': None,
            'gap': None,
            'reconstruction': None,
            'correlation': None
        }
        
        self.anomalies_detected = []
        
        print("[ANOMALY DETECTOR] Inicializado")
    
    def update(
        self,
        price_data: Dict[str, float],
        previous_price: Optional[float] = None
    ) -> Dict:
        """
        Actualizar detector con nuevo dato
        
        Args:
            price_data: Dict con OHLCV data
            previous_price: Precio anterior para detección de gaps
        
        Returns:
            Dict con anomalía detectada y detalles
        """
        
        anomalies = []
        scores = {}
        
        # 1. Detección de gap
        if previous_price is not None:
            gap_pct = abs(price_data['open'] - previous_price) / previous_price
            scores['gap'] = gap_pct
            
            if gap_pct > 0.05:  # 5% gap
                anomalies.append({
                    'type': 'PRICE_GAP',
                    'severity': 'HIGH' if gap_pct > 0.10 else 'MEDIUM',
                    'value': gap_pct,
                    'description': f'Gap de {gap_pct*100:.1f}%'
                })
        
        # 2. Detección de volatilidad extrema
        day_volatility = (price_data['high'] - price_data['low']) / price_data['close']
        scores['volatility'] = day_volatility
        self.history['volatilities'].append(day_volatility)
        
        if len(self.history['volatilities']) >= 20:
            mean_vol = np.mean(self.history['volatilities'][-20:])
            std_vol = np.std(self.history['volatilities'][-20:])
            
            if day_volatility > mean_vol + self.sensitivity * std_vol:
                anomalies.append({
                    'type': 'EXTREME_VOLATILITY',
                    'severity': 'MEDIUM',
                    'value': day_volatility,
                    'description': f'Volatilidad extrema: {day_volatility*100:.1f}%'
                })
        
        # 3. Detección de volumen anómalo
        if 'volume' in price_data:
            vol = price_data['volume']
            self.history['prices'].append(price_data.get('close', 0))
            
            if len(self.history['prices']) >= 20:
                volumes = [d.get('volume', 0) for d in self.history[-20:]]
                mean_vol_data = np.mean(volumes) if volumes else 1
                std_vol_data = np.std(volumes) if volumes else 1
                
                if vol > mean_vol_data + 3 * std_vol_data:
                    anomalies.append({
                        'type': 'VOLUME_SPIKE',
                        'severity': 'MEDIUM',
                        'value': vol / mean_vol_data if mean_vol_data > 0 else 0,
                        'description': f'Volumen {vol / mean_vol_data:.1f}x promedio'
                    })
        
        # 4. Detección VAE (si disponible)
        if self.vae is not None and 'features' in price_data:
            features_tensor = torch.tensor(
                price_data['features'],
                dtype=torch.float32,
                device=self.device
            ).unsqueeze(0)
            
            recon_error = self.vae.get_reconstruction_error(features_tensor)
            scores['reconstruction_error'] = recon_error
            self.history['reconstruction_errors'].append(recon_error)
            
            if len(self.history['reconstruction_errors']) >= 20:
                mean_error = np.mean(self.history['reconstruction_errors'][-20:])
                std_error = np.std(self.history['reconstruction_errors'][-20:])
                
                if recon_error > mean_error + 2.5 * std_error:
                    anomalies.append({
                        'type': 'PATTERN_ANOMALY',
                        'severity': 'HIGH',
                        'value': recon_error,
                        'description': f'Patrón anómalo detectado (error: {recon_error:.4f})'
                    })
        
        # Consolidar resultado
        result = {
            'timestamp': datetime.now().isoformat(),
            'is_anomaly': len(anomalies) > 0,
            'anomalies': anomalies,
            'scores': scores,
            'severity': 'CRITICAL' if any(a['severity'] == 'HIGH' for a in anomalies) else 'NORMAL'
        }
        
        if result['is_anomaly']:
            self.anomalies_detected.append(result)
        
        return result
    
    def get_action_recommendation(self, anomaly_result: Dict) -> str:
        """
        Obtener acción recomendada basada en anomalía
        
        Returns:
            'PAUSE', 'REDUCE_SIZE', 'CLOSE_POSITIONS', 'PROCEED'
        """
        
        if not anomaly_result['is_anomaly']:
            return 'PROCEED'
        
        severity_count = {
            'CRITICAL': sum(1 for a in anomaly_result['anomalies'] if a['severity'] == 'HIGH'),
            'MEDIUM': sum(1 for a in anomaly_result['anomalies'] if a['severity'] == 'MEDIUM'),
        }
        
        if severity_count['CRITICAL'] >= 2:
            return 'CLOSE_POSITIONS'
        elif severity_count['CRITICAL'] >= 1:
            return 'PAUSE'
        elif severity_count['MEDIUM'] >= 2:
            return 'REDUCE_SIZE'
        else:
            return 'PROCEED'
    
    def get_statistics(self) -> Dict:
        """Obtener estadísticas de anomalías detectadas"""
        
        total_anomalies = len(self.anomalies_detected)
        
        if total_anomalies == 0:
            return {'total': 0, 'types': {}}
        
        # Contar por tipo
        types_count = {}
        for result in self.anomalies_detected:
            for anomaly in result['anomalies']:
                atype = anomaly['type']
                types_count[atype] = types_count.get(atype, 0) + 1
        
        # Contar por severidad
        severity_count = {}
        for result in self.anomalies_detected:
            for anomaly in result['anomalies']:
                sev = anomaly['severity']
                severity_count[sev] = severity_count.get(sev, 0) + 1
        
        return {
            'total_detected': total_anomalies,
            'by_type': types_count,
            'by_severity': severity_count,
            'last_detected': self.anomalies_detected[-1]['timestamp'] if total_anomalies > 0 else None
        }


if __name__ == "__main__":
    print("Testing Anomaly Detector...")
    
    # Crear detector sin VAE
    detector = AnomalyDetector(sensitivity=2.0)
    
    # Simular datos normales + algunas anomalías
    np.random.seed(42)
    
    for i in range(100):
        base_price = 100 + np.sin(i / 20) * 5
        
        # Inyectar anomalía en i=50
        if i == 50:
            price_data = {
                'open': base_price * 1.08,    # 8% gap
                'high': base_price * 1.10,
                'low': base_price * 0.95,
                'close': base_price * 1.05,
                'volume': 10000000  # Volumen enorme
            }
        else:
            price_data = {
                'open': base_price + np.random.randn() * 0.5,
                'high': base_price + abs(np.random.randn() * 0.8),
                'low': base_price - abs(np.random.randn() * 0.8),
                'close': base_price + np.random.randn() * 0.5,
                'volume': np.random.randint(1000000, 5000000)
            }
        
        previous = base_price - 1 if i > 0 else None
        result = detector.update(price_data, previous)
        
        if result['is_anomaly']:
            print(f"\nAnomalía detectada en i={i}:")
            for anom in result['anomalies']:
                print(f"  - {anom['description']}")
    
    print("\n" + "="*60)
    print("ANOMALY DETECTION STATISTICS")
    print("="*60)
    stats = detector.get_statistics()
    print(f"Total detectadas: {stats['total_detected']}")
    print(f"Por tipo: {stats['by_type']}")
    print(f"Por severidad: {stats['by_severity']}")
    print("="*60)

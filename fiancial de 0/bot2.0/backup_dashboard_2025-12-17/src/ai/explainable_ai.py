"""
Explainable AI - Feature Importance and Attention Visualization
Sistema para explicar decisiones del modelo
"""

import numpy as np
import torch
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime


class ExplainableAI:
    """
    Módulo para explicabilidad de predicciones
    
    Métodos:
    1. Attention weights (qué features importan más)
    2. Feature importance scores (SHAP-like)
    3. Gradientes (sensibilidad a cambios)
    4. Contrafácticos (qué cambiaría la predicción)
    """
    
    def __init__(self, model, feature_names: List[str], device: str = 'cpu'):
        """
        Args:
            model: Modelo a explicar
            feature_names: Nombres de los features
            device: 'cpu' o 'cuda'
        """
        self.model = model
        self.feature_names = feature_names
        self.device = device
        
        self.explanations_cache = []
        
        print(f"[EXPLAINABLE AI] Inicializado con {len(feature_names)} features")
        print(f"Features: {', '.join(feature_names[:5])}...")
    
    def explain_prediction(
        self,
        x: torch.Tensor,
        attention_weights: Optional[Dict] = None
    ) -> Dict:
        """
        Generar explicación completa de una predicción
        
        Args:
            x: Input tensor (1, seq_len, n_features)
            attention_weights: Pesos de atención si el modelo los proporciona
        
        Returns:
            Dict con múltiples tipos de explicación
        """
        
        explanation = {
            'timestamp': datetime.now().isoformat(),
            'methods': {}
        }
        
        # 1. Feature importance basado en atención
        if attention_weights is not None:
            explanation['methods']['attention'] = self._explain_attention(
                x, attention_weights
            )
        
        # 2. Gradiente-based explanation
        explanation['methods']['gradient'] = self._explain_gradient(x)
        
        # 3. Shap-like explanation (aproximación)
        explanation['methods']['feature_importance'] = self._explain_feature_importance(x)
        
        # 4. Predicción y confianza
        with torch.no_grad():
            output = self.model(x)
            if isinstance(output, tuple):
                logits = output[0]
            else:
                logits = output
            
            probs = F.softmax(logits, dim=1)
            pred_class = torch.argmax(probs, dim=1).item()
            confidence = probs[0, pred_class].item()
        
        explanation['prediction'] = {
            'action': ['SELL', 'HOLD', 'BUY'][pred_class],
            'confidence': float(confidence),
            'probabilities': probs[0].cpu().numpy().tolist()
        }
        
        # 5. Narrativa de decisión
        explanation['narrative'] = self._generate_narrative(explanation)
        
        self.explanations_cache.append(explanation)
        
        return explanation
    
    def _explain_attention(
        self,
        x: torch.Tensor,
        attention_weights: Dict
    ) -> Dict:
        """Explicación basada en weights de atención"""
        
        # Agregar pesos de atención en capas
        if 'all_weights' in attention_weights:
            # attention_weights['all_weights'] es lista de (batch, num_heads, seq, seq)
            weights = attention_weights['all_weights']
            
            # Usar última capa
            last_attention = weights[-1][0]  # (num_heads, seq_len, seq_len)
            
            # Promediar sobre heads
            mean_attention = last_attention.mean(dim=0)  # (seq_len, seq_len)
            
            # Extraer importancia de cada posición temporal
            temporal_importance = mean_attention.mean(dim=0)  # (seq_len,)
            
            # Última posición (predicción actual)
            current_importance = temporal_importance
            
        else:
            current_importance = torch.ones(x.shape[1]) / x.shape[1]
        
        # Mapear importancia a features
        feature_importance = []
        n_features = x.shape[2]
        
        for i in range(n_features):
            # Importancia del feature en promedio de tiempo ponderado
            feature_vec = x[0, :, i]  # (seq_len,)
            weighted_importance = (current_importance * feature_vec.abs()).sum()
            feature_importance.append(float(weighted_importance.item()))
        
        # Normalizar
        feature_importance = np.array(feature_importance)
        feature_importance = feature_importance / (feature_importance.sum() + 1e-8)
        
        # Top features
        top_indices = np.argsort(feature_importance)[-5:][::-1]
        top_features = [
            {
                'feature': self.feature_names[i] if i < len(self.feature_names) else f'Feature_{i}',
                'importance': float(feature_importance[i]),
                'value': float(x[0, -1, i].item())
            }
            for i in top_indices
        ]
        
        return {
            'method': 'Multi-head Attention',
            'top_features': top_features,
            'all_importance': feature_importance.tolist()
        }
    
    def _explain_gradient(self, x: torch.Tensor) -> Dict:
        """Explicación basada en gradientes"""
        
        # Clonar y requiere gradientes
        x_grad = x.clone().detach().requires_grad_(True)
        
        # Forward pass
        output = self.model(x_grad)
        if isinstance(output, tuple):
            logits = output[0]
        else:
            logits = output
        
        # Backward pass
        loss = logits.sum()
        loss.backward()
        
        # Gradientes
        gradients = x_grad.grad  # (1, seq_len, n_features)
        
        # Importancia = abs(gradient) * input
        importance = (gradients.abs() * x).mean(dim=1)[0]  # (n_features,)
        importance = importance / (importance.sum() + 1e-8)
        
        top_indices = torch.argsort(importance, descending=True)[:5]
        top_features = [
            {
                'feature': self.feature_names[i.item()] if i.item() < len(self.feature_names) else f'Feature_{i.item()}',
                'importance': float(importance[i.item()].item()),
                'gradient': float(gradients[0, -1, i.item()].item())
            }
            for i in top_indices
        ]
        
        return {
            'method': 'Gradient-based',
            'top_features': top_features
        }
    
    def _explain_feature_importance(self, x: torch.Tensor) -> Dict:
        """Explicación tipo SHAP (aproximación)"""
        
        # Calcular baseline (promedio de valores anteriores)
        baseline = x[0, :-1, :].mean(dim=0)
        current = x[0, -1, :]
        
        # Diferencia del baseline
        delta = current - baseline
        
        # Normalizar
        importance = delta.abs()
        importance = importance / (importance.sum() + 1e-8)
        
        top_indices = torch.argsort(importance, descending=True)[:5]
        top_features = [
            {
                'feature': self.feature_names[i.item()] if i.item() < len(self.feature_names) else f'Feature_{i.item()}',
                'current_value': float(current[i.item()].item()),
                'baseline_value': float(baseline[i.item()].item()),
                'change': float(delta[i.item()].item()),
                'importance': float(importance[i.item()].item())
            }
            for i in top_indices
        ]
        
        return {
            'method': 'SHAP-like (Delta from Baseline)',
            'top_features': top_features
        }
    
    def _generate_narrative(self, explanation: Dict) -> str:
        """Generar narrativa en lenguaje natural"""
        
        pred = explanation['prediction']
        
        # Obtener top features de atención
        top_feature = None
        if 'attention' in explanation['methods']:
            if explanation['methods']['attention']['top_features']:
                top_feature = explanation['methods']['attention']['top_features'][0]
        
        action = pred['action']
        confidence = pred['confidence']
        
        if action == 'BUY':
            base_narrative = f"Recomendación: COMPRAR (confianza: {confidence*100:.0f}%)"
        elif action == 'SELL':
            base_narrative = f"Recomendación: VENDER (confianza: {confidence*100:.0f}%)"
        else:
            base_narrative = f"Recomendación: MANTENER (confianza: {confidence*100:.0f}%)"
        
        if top_feature:
            base_narrative += f"\n\nRazón principal: {top_feature['feature'].upper()} ({top_feature['importance']*100:.1f}% importancia)"
            base_narrative += f"\nValor actual: {top_feature['value']:.4f}"
        
        # Agregar features secundarios
        if 'gradient' in explanation['methods']:
            if len(explanation['methods']['gradient']['top_features']) > 1:
                base_narrative += "\n\nFactores secundarios:"
                for feat in explanation['methods']['gradient']['top_features'][1:3]:
                    base_narrative += f"\n  - {feat['feature']}"
        
        return base_narrative
    
    def get_report(self, explanation: Dict) -> str:
        """Generar reporte formateado de la explicación"""
        
        report = "="*70 + "\n"
        report += "EXPLICACION DE PREDICCION DEL MODELO\n"
        report += "="*70 + "\n\n"
        
        # Predicción
        report += "PREDICCION:\n"
        report += "-"*70 + "\n"
        report += f"Acción: {explanation['prediction']['action']}\n"
        report += f"Confianza: {explanation['prediction']['confidence']*100:.1f}%\n"
        report += f"Probabilidades: "
        report += f"SELL={explanation['prediction']['probabilities'][0]:.1%}, "
        report += f"HOLD={explanation['prediction']['probabilities'][1]:.1%}, "
        report += f"BUY={explanation['prediction']['probabilities'][2]:.1%}\n\n"
        
        # Narrativa
        report += "NARRATIVA:\n"
        report += "-"*70 + "\n"
        report += explanation['narrative'] + "\n\n"
        
        # Top features de atención
        if 'attention' in explanation['methods']:
            report += "TOP FEATURES (Attention):\n"
            report += "-"*70 + "\n"
            for i, feat in enumerate(explanation['methods']['attention']['top_features'], 1):
                report += f"{i}. {feat['feature']}: {feat['importance']*100:.1f}% (valor: {feat['value']:.4f})\n"
            report += "\n"
        
        # Top features de gradiente
        if 'gradient' in explanation['methods']:
            report += "TOP FEATURES (Gradiente):\n"
            report += "-"*70 + "\n"
            for i, feat in enumerate(explanation['methods']['gradient']['top_features'], 1):
                report += f"{i}. {feat['feature']}: {feat['importance']*100:.1f}%\n"
            report += "\n"
        
        report += "="*70 + "\n"
        
        return report
    
    def save_explanation(self, explanation: Dict, filepath: str) -> None:
        """Guardar explicación a archivo JSON"""
        
        # Convertir numpy arrays a listas
        def make_json_serializable(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: make_json_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_json_serializable(item) for item in obj]
            return obj
        
        serializable = make_json_serializable(explanation)
        
        with open(filepath, 'w') as f:
            json.dump(serializable, f, indent=2, default=str)


if __name__ == "__main__":
    print("Testing Explainable AI...")
    
    # Crear modelo dummy
    class DummyModel(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.fc = torch.nn.Linear(30, 3)
        
        def forward(self, x):
            x = x.mean(dim=1)  # Agregar seq dimension
            return self.fc(x)
    
    model = DummyModel()
    feature_names = [f"Feature_{i}" for i in range(30)]
    
    explainer = ExplainableAI(model, feature_names)
    
    # Predicción dummy
    x = torch.randn(1, 60, 30)
    
    explanation = explainer.explain_prediction(x)
    
    report = explainer.get_report(explanation)
    print(report)
    
    print("\nExplanation saved to cache")
    print(f"Total cached explanations: {len(explainer.explanations_cache)}")

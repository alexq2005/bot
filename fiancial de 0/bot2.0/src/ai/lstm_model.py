"""
LSTM Network
Red neuronal recurrente para capturar patrones temporales
"""

import numpy as np
import torch
import torch.nn as nn
from typing import Dict
import os


class LSTMNetwork(nn.Module):
    """Red LSTM para predicción de trading"""
    
    def __init__(self, input_size: int = 6, hidden_size: int = 64, num_layers: int = 2, output_size: int = 3):
        """
        Inicializa la red LSTM
        
        Args:
            input_size: Tamaño del input (features)
            hidden_size: Tamaño de la capa oculta
            num_layers: Número de capas LSTM
            output_size: Tamaño del output (3 acciones)
        """
        super(LSTMNetwork, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # Capas LSTM
        self.lstm = nn.LSTM(
            input_size,
            hidden_size,
            num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0
        )
        
        # Capa fully connected
        self.fc = nn.Linear(hidden_size, output_size)
        
        # Softmax para probabilidades
        self.softmax = nn.Softmax(dim=1)
    
    def forward(self, x):
        """Forward pass"""
        # Inicializar estados ocultos
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        
        # LSTM
        out, _ = self.lstm(x, (h0, c0))
        
        # Tomar último output
        out = out[:, -1, :]
        
        # Fully connected
        out = self.fc(out)
        
        return out


class LSTMTradingModel:
    """
    Modelo LSTM para predicción de trading
    
    Ventajas:
    - Captura dependencias temporales
    - Memoria de largo plazo
    - Excelente para series de tiempo
    """
    
    def __init__(self, model_path: str = "./models/lstm_model.pth", sequence_length: int = 10):
        """
        Inicializa el modelo LSTM
        
        Args:
            model_path: Ruta para guardar/cargar modelo
            sequence_length: Longitud de la secuencia temporal
        """
        self.model_path = model_path
        self.sequence_length = sequence_length
        self.model = LSTMNetwork()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.CrossEntropyLoss()
        self.is_trained = False
        
        if os.path.exists(model_path):
            self.load_model()
    
    def prepare_sequence(self, state: np.ndarray) -> torch.Tensor:
        """
        Prepara secuencia para LSTM
        
        Args:
            state: Estado actual
        
        Returns:
            Tensor con secuencia
        """
        # Si es un solo estado, replicar para crear secuencia
        if len(state.shape) == 1:
            # Replicar estado para crear secuencia
            sequence = np.tile(state, (self.sequence_length, 1))
        else:
            sequence = state
        
        # Convertir a tensor
        tensor = torch.FloatTensor(sequence).unsqueeze(0)  # Agregar batch dimension
        
        return tensor
    
    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 50):
        """
        Entrena el modelo
        
        Args:
            X: Secuencias de estados
            y: Labels (acciones)
            epochs: Número de épocas
        """
        print(f"🎓 Entrenando modelo LSTM ({epochs} épocas)...")
        
        self.model.train()
        
        for epoch in range(epochs):
            # Forward pass
            X_tensor = torch.FloatTensor(X)
            y_tensor = torch.LongTensor(y)
            
            outputs = self.model(X_tensor)
            loss = self.criterion(outputs, y_tensor)
            
            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            
            if (epoch + 1) % 10 == 0:
                print(f"  Época {epoch+1}/{epochs}, Loss: {loss.item():.4f}")
        
        self.is_trained = True
        print("✓ Entrenamiento completado")
    
    def predict(self, state: np.ndarray) -> Dict:
        """
        Predice acción
        
        Args:
            state: Estado actual
        
        Returns:
            Dict con acción y confianza
        """
        if not self.is_trained:
            return {'action': 'HOLD', 'confidence': 0.0}
        
        self.model.eval()
        
        with torch.no_grad():
            # Preparar secuencia
            sequence = self.prepare_sequence(state)
            
            # Predicción
            output = self.model(sequence)
            probabilities = self.model.softmax(output)[0]
            
            # Acción predicha
            prediction = torch.argmax(probabilities).item()
            
            # Mapear a acción
            action_map = {0: 'HOLD', 1: 'BUY', 2: 'SELL'}
            action = action_map.get(prediction, 'HOLD')
            
            # Confianza
            confidence = float(probabilities[prediction])
        
        return {
            'action': action,
            'confidence': confidence,
            'probabilities': {
                'HOLD': float(probabilities[0]),
                'BUY': float(probabilities[1]),
                'SELL': float(probabilities[2])
            }
        }
    
    def save_model(self, path: str = None):
        """Guarda el modelo"""
        save_path = path or self.model_path
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }, save_path)
        print(f"✓ Modelo LSTM guardado en {save_path}")
    
    def load_model(self, path: str = None):
        """Carga el modelo"""
        load_path = path or self.model_path
        try:
            checkpoint = torch.load(load_path)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.is_trained = True
            print(f"✓ Modelo LSTM cargado desde {load_path}")
        except Exception as e:
            print(f"⚠ No se pudo cargar modelo LSTM: {e}")
            self.is_trained = False

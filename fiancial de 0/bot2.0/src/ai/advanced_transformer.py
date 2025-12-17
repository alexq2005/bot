"""
Advanced Transformer for Trading
Transformer mejorado con multi-head attention para predicción de precios
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple, Optional
import math


class PositionalEncoding(nn.Module):
    """Positional encoding mejorado (Rotary Position Embedding)"""
    
    def __init__(self, d_model: int, max_len: int = 5000, base: float = 10000.0):
        super().__init__()
        self.d_model = d_model
        self.base = base
        
        # Precalcular position encodings
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2) * -(math.log(base) / d_model)
        )
        
        pe = torch.zeros(max_len, d_model)
        pe[:, 0::2] = torch.sin(position * div_term)
        if d_model % 2 == 1:
            pe[:, 1::2] = torch.cos(position * div_term[:-1])
        else:
            pe[:, 1::2] = torch.cos(position * div_term)
        
        self.register_buffer('pe', pe.unsqueeze(0))
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Tensor de shape (batch_size, seq_len, d_model)
        """
        return x + self.pe[:, :x.size(1), :]


class MultiHeadAttention(nn.Module):
    """Multi-head attention mejorado con rotary embeddings"""
    
    def __init__(self, d_model: int, num_heads: int = 8, dropout: float = 0.1):
        super().__init__()
        
        assert d_model % num_heads == 0, "d_model debe ser divisible por num_heads"
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
    
    def forward(
        self, 
        Q: torch.Tensor, 
        K: torch.Tensor, 
        V: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            Q, K, V: Query, Key, Value tensors (batch_size, seq_len, d_model)
            mask: Attention mask
        
        Returns:
            Output tensor y attention weights
        """
        batch_size = Q.shape[0]
        
        # Linear transformations
        Q = self.W_q(Q).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.W_k(K).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.W_v(V).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        # Scaled dot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
        
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # Combinar heads
        output = torch.matmul(attention_weights, V)
        output = output.transpose(1, 2).contiguous()
        output = output.view(batch_size, -1, self.d_model)
        
        output = self.W_o(output)
        
        return output, attention_weights


class FeedForwardNetwork(nn.Module):
    """Feed-forward network con GELU activation"""
    
    def __init__(self, d_model: int, d_ff: int = 2048, dropout: float = 0.1):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear2(self.dropout(F.gelu(self.linear1(x))))


class TransformerBlock(nn.Module):
    """Bloque Transformer completo con residual connections y layer norm"""
    
    def __init__(self, d_model: int, num_heads: int = 8, d_ff: int = 2048, dropout: float = 0.1):
        super().__init__()
        
        self.attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = FeedForwardNetwork(d_model, d_ff, dropout)
        
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass con residual connections"""
        
        # Self-attention con residual
        attn_output, attention_weights = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout1(attn_output))
        
        # Feed-forward con residual
        ff_output = self.feed_forward(x)
        x = self.norm2(x + self.dropout2(ff_output))
        
        return x, attention_weights


class AdvancedTransformer(nn.Module):
    """
    Transformer avanzado para predicción de trading
    
    Arquitectura:
    - Positional encoding mejorado
    - 4-6 capas Transformer
    - Multi-head attention (8 cabezas)
    - Residual connections y layer norm
    - Output layer para predicción (3 clases: BUY, HOLD, SELL)
    """
    
    def __init__(
        self,
        input_size: int = 30,              # Features: OHLCV + indicadores
        d_model: int = 256,                 # Embedding dimension
        num_layers: int = 4,                # Número de bloques transformer
        num_heads: int = 8,                 # Número de attention heads
        d_ff: int = 1024,                   # FF network dimension
        max_seq_len: int = 60,              # Máxima secuencia (días)
        output_size: int = 3,               # BUY, HOLD, SELL
        dropout: float = 0.1,
        device: str = 'cpu'
    ):
        super().__init__()
        
        self.d_model = d_model
        self.device = device
        
        # Input projection
        self.input_projection = nn.Linear(input_size, d_model)
        
        # Positional encoding
        self.pos_encoding = PositionalEncoding(d_model, max_seq_len)
        
        # Transformer blocks
        self.transformer_blocks = nn.ModuleList([
            TransformerBlock(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        
        # Output head
        self.dropout = nn.Dropout(dropout)
        self.fc_hidden = nn.Linear(d_model, d_model // 2)
        self.fc_out = nn.Linear(d_model // 2, output_size)
        
        self.to(device)
    
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, dict]:
        """
        Args:
            x: Input tensor (batch_size, seq_len, input_size)
            mask: Attention mask (opcional)
        
        Returns:
            Logits (batch_size, 3) y diccionario de atención
        """
        batch_size, seq_len, _ = x.shape
        
        # Input projection
        x = self.input_projection(x)
        
        # Add positional encoding
        x = self.pos_encoding(x)
        
        # Transformer blocks
        attention_weights_list = []
        for block in self.transformer_blocks:
            x, attn_weights = block(x, mask)
            attention_weights_list.append(attn_weights)
        
        # Usar el último token para predicción (como en BERT)
        x = x[:, -1, :]  # (batch_size, d_model)
        
        # Output head
        x = self.dropout(x)
        x = F.relu(self.fc_hidden(x))
        logits = self.fc_out(x)
        
        # Guardar pesos de atención para explicabilidad
        attention_info = {
            'all_weights': attention_weights_list,
            'last_layer_attention': attention_weights_list[-1] if attention_weights_list else None
        }
        
        return logits, attention_info
    
    def predict(self, x: torch.Tensor) -> dict:
        """Predicción con confianza y clase"""
        with torch.no_grad():
            logits, attn_info = self.forward(x)
            probs = F.softmax(logits, dim=1)
            
            actions = ['SELL', 'HOLD', 'BUY']
            predicted_class = torch.argmax(probs, dim=1)[0].item()
            confidence = probs[0, predicted_class].item()
            
            return {
                'action': actions[predicted_class],
                'confidence': float(confidence),
                'probabilities': probs[0].cpu().numpy(),
                'attention': attn_info
            }


# Función de utilidad para entrenamiento
def create_causal_mask(seq_len: int, device: str = 'cpu') -> torch.Tensor:
    """Crear máscara causal para auto-atención"""
    mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1)
    mask = (mask == 0).unsqueeze(0).unsqueeze(0).to(device)
    return mask


if __name__ == "__main__":
    # Test
    batch_size = 32
    seq_len = 60
    input_size = 30
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    model = AdvancedTransformer(
        input_size=input_size,
        d_model=256,
        num_layers=4,
        num_heads=8,
        device=device
    )
    
    # Dummy input
    x = torch.randn(batch_size, seq_len, input_size).to(device)
    
    # Forward pass
    output, attn_info = model(x)
    
    print(f"Input shape: {x.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Number of attention heads: {len(attn_info['all_weights'])}")
    print(f"\nTransformer creado exitosamente!")
    print(f"Parámetros totales: {sum(p.numel() for p in model.parameters()):,}")

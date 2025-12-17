"""
Sentiment Analyzer using FinBERT
Análisis de sentimiento financiero con comprensión de contexto
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict, List
import numpy as np


class SentimentAnalyzer:
    """Analizador de sentimiento usando FinBERT"""
    
    def __init__(self, model_name: str = "ProsusAI/finbert"):
        """
        Inicializa el analizador de sentimiento
        
        Args:
            model_name: Nombre del modelo de HuggingFace (default: FinBERT)
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"🤖 Cargando modelo FinBERT... (dispositivo: {self.device})")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            
            print(f"✓ FinBERT cargado exitosamente")
            
        except Exception as e:
            print(f"⚠ Error cargando FinBERT: {e}")
            print(f"⚠ Usando análisis de sentimiento simplificado")
            self.model = None
            self.tokenizer = None
    
    def analyze(self, text: str) -> Dict:
        """
        Analiza el sentimiento de un texto
        
        Args:
            text: Texto a analizar (titular de noticia, tweet, etc.)
        
        Returns:
            Dict con: sentiment_score (-1.0 a 1.0), label, confidence
        """
        if not self.model or not self.tokenizer:
            # Fallback: análisis simple por palabras clave
            return self._simple_sentiment(text)
        
        try:
            # Tokenizar
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            ).to(self.device)
            
            # Inferencia
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=1)[0]
            
            # FinBERT devuelve: [positive, negative, neutral]
            probs = probabilities.cpu().numpy()
            
            # Mapear a score -1 a 1
            # positive=0, negative=1, neutral=2 (depende del modelo)
            labels = ["positive", "negative", "neutral"]
            predicted_label = labels[np.argmax(probs)]
            confidence = float(np.max(probs))
            
            # Calcular score: positive=1, neutral=0, negative=-1
            if predicted_label == "positive":
                sentiment_score = float(probs[0])
            elif predicted_label == "negative":
                sentiment_score = -float(probs[1])
            else:  # neutral
                sentiment_score = 0.0
            
            return {
                "sentiment_score": sentiment_score,
                "label": predicted_label,
                "confidence": confidence,
                "probabilities": {
                    "positive": float(probs[0]),
                    "negative": float(probs[1]),
                    "neutral": float(probs[2])
                }
            }
            
        except Exception as e:
            print(f"⚠ Error en análisis FinBERT: {e}")
            return self._simple_sentiment(text)
    
    def _simple_sentiment(self, text: str) -> Dict:
        """
        Análisis de sentimiento simplificado basado en palabras clave
        (Fallback cuando FinBERT no está disponible)
        """
        text_lower = text.lower()
        
        # Palabras positivas financieras
        positive_words = [
            "sube", "alza", "gana", "crece", "récord", "positivo", "beneficio",
            "profit", "gain", "rally", "bull", "upgrade", "strong", "growth"
        ]
        
        # Palabras negativas financieras
        negative_words = [
            "baja", "cae", "pierde", "crisis", "negativo", "pérdida", "riesgo",
            "loss", "fall", "drop", "bear", "downgrade", "weak", "decline"
        ]
        
        # Contar palabras
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        # Calcular score
        total = pos_count + neg_count
        if total == 0:
            sentiment_score = 0.0
            label = "neutral"
        elif pos_count > neg_count:
            sentiment_score = pos_count / (total + 1)
            label = "positive"
        else:
            sentiment_score = -neg_count / (total + 1)
            label = "negative"
        
        return {
            "sentiment_score": sentiment_score,
            "label": label,
            "confidence": 0.5,  # Baja confianza para método simple
            "probabilities": {
                "positive": pos_count / (total + 1),
                "negative": neg_count / (total + 1),
                "neutral": 1 - (total / (total + 1))
            }
        }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """
        Analiza múltiples textos en batch (más eficiente)
        
        Args:
            texts: Lista de textos a analizar
        
        Returns:
            Lista de resultados de sentimiento
        """
        if not self.model or not self.tokenizer:
            return [self._simple_sentiment(text) for text in texts]
        
        try:
            # Tokenizar batch
            inputs = self.tokenizer(
                texts,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            ).to(self.device)
            
            # Inferencia
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=1)
            
            # Procesar resultados
            results = []
            probs_np = probabilities.cpu().numpy()
            
            for i, probs in enumerate(probs_np):
                labels = ["positive", "negative", "neutral"]
                predicted_label = labels[np.argmax(probs)]
                confidence = float(np.max(probs))
                
                if predicted_label == "positive":
                    sentiment_score = float(probs[0])
                elif predicted_label == "negative":
                    sentiment_score = -float(probs[1])
                else:
                    sentiment_score = 0.0
                
                results.append({
                    "sentiment_score": sentiment_score,
                    "label": predicted_label,
                    "confidence": confidence,
                    "probabilities": {
                        "positive": float(probs[0]),
                        "negative": float(probs[1]),
                        "neutral": float(probs[2])
                    }
                })
            
            return results
            
        except Exception as e:
            print(f"⚠ Error en análisis batch: {e}")
            return [self._simple_sentiment(text) for text in texts]
    
    def aggregate_sentiment(self, sentiments: List[Dict]) -> float:
        """
        Agrega múltiples sentimientos en un score único
        
        Args:
            sentiments: Lista de resultados de sentimiento
        
        Returns:
            float: Score agregado ponderado por confianza (-1.0 a 1.0)
        """
        if not sentiments:
            return 0.0
        
        # Ponderar por confianza
        weighted_sum = sum(
            s['sentiment_score'] * s['confidence'] 
            for s in sentiments
        )
        total_confidence = sum(s['confidence'] for s in sentiments)
        
        if total_confidence == 0:
            return 0.0
        
        return weighted_sum / total_confidence

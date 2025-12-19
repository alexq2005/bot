"""
LLM Reasoner
Razonamiento avanzado usando Large Language Models (GPT-4/Claude/DeepSeek/Gemini)
"""

import os
from typing import Dict, Optional
from datetime import datetime


class LLMReasoner:
    """
    Razonador basado en LLM
    
    Usa GPT-4, Claude, DeepSeek o Gemini para:
    - Razonamiento en lenguaje natural
    - Explicaciones detalladas
    - Detección de contradicciones
    - Validación de coherencia
    """
    
    def __init__(
        self,
        api_key: str = "",
        model: str = "gpt-4",
        provider: str = "openai"
    ):
        """
        Inicializa el reasoner
        
        Args:
            api_key: API key de OpenAI, Anthropic, DeepSeek o Gemini
            model: Modelo a usar (gpt-4, gpt-3.5-turbo, claude-3, deepseek-chat, gemini-pro)
            provider: Proveedor (openai, anthropic, deepseek, gemini)
        """
        # Detectar provider y API key adecuados
        if provider == "deepseek":
            self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY', '')
        elif provider == "anthropic":
            self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY', '')
        elif provider == "gemini":
            self.api_key = api_key or os.getenv('GEMINI_API_KEY', '')
        else:  # openai por defecto
            self.api_key = api_key or os.getenv('OPENAI_API_KEY', '')
        
        self.model = model
        self.provider = provider
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            if provider == "openai":
                try:
                    from openai import OpenAI
                    self.client = OpenAI(api_key=self.api_key)
                    print(f"✓ LLM Reasoner activado (OpenAI {model})")
                except ImportError:
                    print("⚠ openai no instalado. Ejecuta: pip install openai")
                    self.enabled = False
            elif provider == "anthropic":
                try:
                    from anthropic import Anthropic
                    self.client = Anthropic(api_key=self.api_key)
                    print(f"✓ LLM Reasoner activado (Anthropic {model})")
                except ImportError:
                    print("⚠ anthropic no instalado. Ejecuta: pip install anthropic")
                    self.enabled = False
            elif provider == "deepseek":
                try:
                    from openai import OpenAI
                    # DeepSeek usa la API compatible con OpenAI
                    self.client = OpenAI(
                        api_key=self.api_key,
                        base_url="https://api.deepseek.com"
                    )
                    # Usar modelo deepseek-chat por defecto si no se especifica
                    if model == "gpt-4" or model == "gpt-3.5-turbo":
                        self.model = "deepseek-chat"
                    print(f"✓ LLM Reasoner activado (DeepSeek {self.model})")
                except ImportError:
                    print("⚠ openai no instalado. Ejecuta: pip install openai")
                    self.enabled = False
            elif provider == "gemini":
                try:
                    from google import genai
                    # Configurar Gemini con nuevo SDK
                    self.client = genai.Client(api_key=self.api_key)
                    # Usar gemini-2.0-flash-exp por defecto (más rápido y gratis)
                    if model in ["gpt-4", "gpt-3.5-turbo", "deepseek-chat", "gemini-pro"]:
                        self.model = "gemini-2.0-flash-exp"
                    print(f"✓ LLM Reasoner activado (Google Gemini {self.model})")
                except ImportError:
                    print("⚠ google-genai no instalado. Ejecuta: pip install google-genai")
                    self.enabled = False
        else:
            print("⚠ LLM Reasoner desactivado (falta API key)")
    
    def analyze_trading_decision(
        self,
        symbol: str,
        market_data: Dict,
        signals: Dict,
        regime: Dict,
        alt_data: Dict
    ) -> Dict:
        """
        Analiza una decisión de trading usando razonamiento LLM
        
        Args:
            symbol: Símbolo del activo
            market_data: Datos de mercado
            signals: Señales de los modelos
            regime: Información del régimen
            alt_data: Datos alternativos
        
        Returns:
            Dict con análisis y decisión
        """
        if not self.enabled:
            return {
                'action': signals.get('ensemble', {}).get('action', 'HOLD'),
                'confidence': 0.5,
                'reasoning': 'LLM no disponible',
                'available': False
            }
        
        # Construir prompt
        prompt = self._build_analysis_prompt(
            symbol, market_data, signals, regime, alt_data
        )
        
        try:
            # Llamar a LLM
            if self.provider in ["openai", "deepseek"]:
                # OpenAI y DeepSeek usan la misma API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Eres un trader experto con 20 años de experiencia. Analiza situaciones de trading de forma lógica y estructurada."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                
                analysis = response.choices[0].message.content
            
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                
                analysis = response.content[0].text
            
            elif self.provider == "gemini":
                # Gemini con nuevo SDK
                full_prompt = f"""Eres un trader experto con 20 años de experiencia. Analiza situaciones de trading de forma lógica y estructurada.

{prompt}"""
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=full_prompt,
                    config={
                        'temperature': 0.3,
                        'max_output_tokens': 1000,
                    }
                )
                
                analysis = response.text
            
            # Parsear respuesta
            result = self._parse_llm_response(analysis)
            result['available'] = True
            result['full_reasoning'] = analysis
            
            return result
            
        except Exception as e:
            print(f"⚠ Error en LLM Reasoner: {e}")
            return {
                'action': signals.get('ensemble', {}).get('action', 'HOLD'),
                'confidence': 0.5,
                'reasoning': f'Error: {str(e)}',
                'available': False
            }
    
    def _build_analysis_prompt(
        self,
        symbol: str,
        market_data: Dict,
        signals: Dict,
        regime: Dict,
        alt_data: Dict
    ) -> str:
        """Construye el prompt para el LLM"""
        
        prompt = f"""Analiza esta situación de trading para {symbol}:

DATOS DE MERCADO:
- Precio actual: ${market_data.get('price', 0):,.2f}
- RSI: {market_data.get('rsi', 0):.1f}
- MACD: {market_data.get('macd', 0):.2f}
- Volatilidad (ATR): {market_data.get('atr', 0):.2f}

SEÑALES DE LOS MODELOS:
- Análisis Técnico: {signals.get('technical', {}).get('action', 'N/A')} (confianza: {signals.get('technical', {}).get('confidence', 0):.0%})
- Ensemble ML: {signals.get('ensemble', {}).get('action', 'N/A')} (confianza: {signals.get('ensemble', {}).get('confidence', 0):.0%})
  Votos: {signals.get('ensemble', {}).get('votes', {})}
- Sentimiento: {signals.get('sentiment', {}).get('action', 'N/A')} (score: {signals.get('sentiment', {}).get('score', 0):.2f})

RÉGIMEN DE MERCADO:
- Tipo: {regime.get('regime', 'N/A')}
- Descripción: {regime.get('description', 'N/A')}
- Confianza: {regime.get('confidence', 0):.0%}

DATOS ALTERNATIVOS:
- Google Trends: {alt_data.get('google_trends', {}).get('trend', 'N/A')} (interés: {alt_data.get('google_trends', {}).get('interest', 0):.0f})
- Twitter: {alt_data.get('twitter', {}).get('sentiment', 0):.2f}
- Reddit: {alt_data.get('reddit', {}).get('mentions', 0)} menciones

RAZONA PASO A PASO:
1. ¿Qué indica cada señal individualmente?
2. ¿Hay contradicciones entre las señales?
3. ¿El régimen de mercado apoya o contradice las señales?
4. ¿Los datos alternativos confirman o contradicen?
5. ¿Cuál es el nivel de consenso general?
6. ¿Cuál es la mejor decisión considerando TODO?

FORMATO DE RESPUESTA:
ACCIÓN: [BUY/SELL/HOLD]
CONFIANZA: [0-100]%
RAZONAMIENTO: [Explicación detallada de 2-3 líneas]
RIESGOS: [Principales riesgos identificados]
"""
        
        return prompt
    
    def _parse_llm_response(self, response: str) -> Dict:
        """Parsea la respuesta del LLM"""
        
        lines = response.strip().split('\n')
        
        action = 'HOLD'
        confidence = 0.5
        reasoning = response
        risks = ''
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('ACCIÓN:') or line.startswith('ACTION:'):
                action_text = line.split(':', 1)[1].strip().upper()
                if 'BUY' in action_text or 'COMPRA' in action_text:
                    action = 'BUY'
                elif 'SELL' in action_text or 'VENTA' in action_text:
                    action = 'SELL'
                else:
                    action = 'HOLD'
            
            elif line.startswith('CONFIANZA:') or line.startswith('CONFIDENCE:'):
                conf_text = line.split(':', 1)[1].strip()
                # Extraer número
                import re
                numbers = re.findall(r'\d+', conf_text)
                if numbers:
                    confidence = float(numbers[0]) / 100
            
            elif line.startswith('RAZONAMIENTO:') or line.startswith('REASONING:'):
                reasoning = line.split(':', 1)[1].strip()
            
            elif line.startswith('RIESGOS:') or line.startswith('RISKS:'):
                risks = line.split(':', 1)[1].strip()
        
        return {
            'action': action,
            'confidence': confidence,
            'reasoning': reasoning,
            'risks': risks
        }
    
    def explain_decision(self, decision: Dict) -> str:
        """
        Genera explicación en lenguaje natural de una decisión
        
        Args:
            decision: Decisión del bot
        
        Returns:
            str: Explicación detallada
        """
        if not self.enabled:
            return f"Decisión: {decision.get('action', 'HOLD')} (LLM no disponible)"
        
        prompt = f"""Explica esta decisión de trading de forma clara y concisa:

DECISIÓN: {decision.get('action', 'HOLD')}
CONFIANZA: {decision.get('confidence', 0):.0%}
SEÑALES: {decision.get('signals', {})}
RÉGIMEN: {decision.get('regime', 'N/A')}

Genera una explicación de 2-3 líneas que un trader principiante pueda entender."""
        
        try:
            if self.provider in ["openai", "deepseek"]:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=200
                )
                return response.choices[0].message.content
            
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=200,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            elif self.provider == "gemini":
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config={
                        'temperature': 0.5,
                        'max_output_tokens': 200,
                    }
                )
                return response.text
        
        except Exception as e:
            return f"Error generando explicación: {e}"

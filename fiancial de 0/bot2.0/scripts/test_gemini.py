"""
Test Google Gemini AI Integration
Tests de integración para Google Gemini
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai.llm_reasoner import LLMReasoner


def test_gemini_connection():
    """Test 1: Verificar conexión con Gemini"""
    print("\n" + "="*60)
    print("TEST 1: Conexión con Google Gemini")
    print("="*60)
    
    api_key = "AIzaSyBQbHiAqUKAVI5P9T3-zDG6PqMZ_iR19-U"
    
    reasoner = LLMReasoner(
        api_key=api_key,
        model="gemini-pro",
        provider="gemini"
    )
    
    if reasoner.enabled:
        print("✅ Cliente Gemini inicializado correctamente")
        print(f"   Modelo: {reasoner.model}")
        print(f"   Provider: {reasoner.provider}")
        return True
    else:
        print("❌ Error: Cliente no se pudo inicializar")
        return False


def test_simple_reasoning():
    """Test 2: Razonamiento simple"""
    print("\n" + "="*60)
    print("TEST 2: Razonamiento Simple")
    print("="*60)
    
    api_key = "AIzaSyBQbHiAqUKAVI5P9T3-zDG6PqMZ_iR19-U"
    
    reasoner = LLMReasoner(
        api_key=api_key,
        model="gemini-pro",
        provider="gemini"
    )
    
    # Simular datos de mercado
    market_data = {
        'price': 1250.50,
        'rsi': 68.5,
        'macd': 15.3,
        'atr': 25.8
    }
    
    signals = {
        'technical': {'action': 'BUY', 'confidence': 0.72},
        'ensemble': {'action': 'BUY', 'confidence': 0.68, 'votes': {'buy': 3, 'hold': 1, 'sell': 0}},
        'sentiment': {'action': 'HOLD', 'score': 0.15}
    }
    
    regime = {
        'regime': 'BULLISH',
        'description': 'Mercado alcista con alta volatilidad',
        'confidence': 0.75
    }
    
    alt_data = {
        'google_trends': {'trend': 'RISING', 'interest': 85},
        'twitter': {'sentiment': 0.65},
        'reddit': {'mentions': 150}
    }
    
    try:
        start_time = datetime.now()
        result = reasoner.analyze_trading_decision(
            symbol="GGAL",
            market_data=market_data,
            signals=signals,
            regime=regime,
            alt_data=alt_data
        )
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n✅ Análisis completado en {duration:.2f} segundos")
        print(f"\n📊 RESULTADO:")
        print(f"   Acción: {result.get('action', 'N/A')}")
        print(f"   Confianza: {result.get('confidence', 0):.0%}")
        print(f"   Razonamiento: {result.get('reasoning', 'N/A')[:200]}...")
        
        if result.get('risks'):
            print(f"   Riesgos: {result.get('risks', '')[:150]}...")
        
        return result.get('available', False)
    
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        return False


def test_trading_analysis():
    """Test 3: Análisis completo de trading"""
    print("\n" + "="*60)
    print("TEST 3: Análisis Completo de Trading")
    print("="*60)
    
    api_key = "AIzaSyBQbHiAqUKAVI5P9T3-zDG6PqMZ_iR19-U"
    
    reasoner = LLMReasoner(
        api_key=api_key,
        model="gemini-pro",
        provider="gemini"
    )
    
    # Escenario: YPFD con señales mixtas
    market_data = {
        'price': 850.25,
        'rsi': 45.2,  # Neutral
        'macd': -5.8,  # Negativo
        'atr': 18.5
    }
    
    signals = {
        'technical': {'action': 'SELL', 'confidence': 0.55},
        'ensemble': {'action': 'HOLD', 'confidence': 0.48, 'votes': {'buy': 1, 'hold': 2, 'sell': 1}},
        'sentiment': {'action': 'BUY', 'score': 0.35}
    }
    
    regime = {
        'regime': 'SIDEWAYS',
        'description': 'Mercado lateral sin dirección clara',
        'confidence': 0.62
    }
    
    alt_data = {
        'google_trends': {'trend': 'STABLE', 'interest': 45},
        'twitter': {'sentiment': 0.05},
        'reddit': {'mentions': 25}
    }
    
    try:
        result = reasoner.analyze_trading_decision(
            symbol="YPFD",
            market_data=market_data,
            signals=signals,
            regime=regime,
            alt_data=alt_data
        )
        
        print(f"\n✅ Análisis de YPFD completado")
        print(f"\n📊 DECISIÓN FINAL:")
        print(f"   Símbolo: YPFD")
        print(f"   Acción Recomendada: {result.get('action', 'N/A')}")
        print(f"   Nivel de Confianza: {result.get('confidence', 0):.0%}")
        print(f"\n💭 RAZONAMIENTO:")
        print(f"   {result.get('reasoning', 'N/A')}")
        
        if result.get('full_reasoning'):
            print(f"\n📝 ANÁLISIS COMPLETO:")
            print(f"   {result.get('full_reasoning', '')[:400]}...")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_explain_decision():
    """Test 4: Explicación de decisiones"""
    print("\n" + "="*60)
    print("TEST 4: Explicación de Decisiones")
    print("="*60)
    
    api_key = "AIzaSyBQbHiAqUKAVI5P9T3-zDG6PqMZ_iR19-U"
    
    reasoner = LLMReasoner(
        api_key=api_key,
        model="gemini-pro",
        provider="gemini"
    )
    
    decision = {
        'action': 'BUY',
        'confidence': 0.78,
        'signals': {
            'technical': 'BUY',
            'ensemble': 'BUY',
            'sentiment': 'HOLD'
        },
        'regime': 'BULLISH'
    }
    
    try:
        explanation = reasoner.explain_decision(decision)
        
        print(f"\n✅ Explicación generada")
        print(f"\n📖 EXPLICACIÓN:")
        print(f"   {explanation}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_cost_estimation():
    """Test 5: Estimación de costos"""
    print("\n" + "="*60)
    print("TEST 5: Estimación de Costos con Gemini")
    print("="*60)
    
    # Costos aproximados de Gemini (gratis hasta cierto límite)
    # Gemini Pro: GRATIS hasta 60 requests/minuto
    # Luego: $0.00025 por 1K tokens input, $0.0005 por 1K tokens output
    
    analyses_per_day = 100
    tokens_per_analysis_input = 800  # Promedio
    tokens_per_analysis_output = 200  # Promedio
    
    # Costo después del límite gratuito
    cost_per_1k_input = 0.00025
    cost_per_1k_output = 0.0005
    
    daily_tokens_input = analyses_per_day * tokens_per_analysis_input / 1000
    daily_tokens_output = analyses_per_day * tokens_per_analysis_output / 1000
    
    daily_cost = (daily_tokens_input * cost_per_1k_input) + (daily_tokens_output * cost_per_1k_output)
    monthly_cost = daily_cost * 30
    
    print(f"\n💰 COSTO ESTIMADO (después de límite gratuito):")
    print(f"   Análisis por día: {analyses_per_day}")
    print(f"   Tokens input por análisis: ~{tokens_per_analysis_input}")
    print(f"   Tokens output por análisis: ~{tokens_per_analysis_output}")
    print(f"   Costo por análisis: ${(daily_cost/analyses_per_day):.6f}")
    print(f"   Costo diario: ${daily_cost:.4f}")
    print(f"   Costo mensual: ${monthly_cost:.2f}")
    
    print(f"\n📊 COMPARACIÓN CON OTROS PROVEEDORES:")
    print(f"   {'Proveedor':<15} {'Costo/Análisis':<20} {'Costo Mensual':<15}")
    print(f"   {'-'*50}")
    print(f"   {'OpenAI GPT-4':<15} {'$0.003':<20} {'$9.00':<15}")
    print(f"   {'DeepSeek':<15} {'$0.0002':<20} {'$0.60':<15}")
    print(f"   {'Gemini Pro':<15} {'GRATIS*':<20} {'GRATIS*':<15}")
    print(f"   {' '*15} {'(límite: 60/min)':<20} {'':<15}")
    
    print(f"\n⭐ GEMINI VENTAJAS:")
    print(f"   ✅ Gratis hasta 60 requests/minuto")
    print(f"   ✅ Excelente calidad de respuestas")
    print(f"   ✅ Rápido (promedio 1.5s)")
    print(f"   ✅ Soporta contextos largos (32K tokens)")
    print(f"   ✅ Multimodal (puede procesar imágenes también)")
    
    return True


def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "🧪"*30)
    print("SUITE DE TESTS - GOOGLE GEMINI INTEGRATION")
    print("🧪"*30)
    
    results = []
    
    # Test 1: Conexión
    results.append(("Conexión", test_gemini_connection()))
    
    # Test 2: Razonamiento simple
    if results[0][1]:  # Solo si conexión exitosa
        results.append(("Razonamiento Simple", test_simple_reasoning()))
    
    # Test 3: Análisis de trading
    if len(results) >= 2 and results[1][1]:
        results.append(("Análisis Trading", test_trading_analysis()))
    
    # Test 4: Explicación
    if len(results) >= 3 and results[2][1]:
        results.append(("Explicación", test_explain_decision()))
    
    # Test 5: Costos
    results.append(("Estimación Costos", test_cost_estimation()))
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE TESTS")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n📊 Total: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("\n🎉 ¡Todos los tests pasaron! Gemini está listo para usar.")
    else:
        print("\n⚠️  Algunos tests fallaron. Revisa los errores arriba.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

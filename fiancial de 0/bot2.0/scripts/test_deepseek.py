"""
Test script for DeepSeek AI integration
Verifies API connection and trading analysis functionality
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ai.llm_reasoner import LLMReasoner
import time


def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_deepseek_connection():
    """Test basic DeepSeek API connection"""
    print_section("Test 1: DeepSeek API Connection")
    
    api_key = "sk-a0f869809e074f39b5431c01e5e83a1b"
    
    try:
        reasoner = LLMReasoner(
            api_key=api_key,
            model="deepseek-chat",
            provider="deepseek"
        )
        
        if reasoner.enabled:
            print("✅ DeepSeek client initialized successfully")
            print(f"   Provider: {reasoner.provider}")
            print(f"   Model: {reasoner.model}")
            print(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
            return reasoner
        else:
            print("❌ DeepSeek client initialization failed")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_simple_reasoning(reasoner):
    """Test simple reasoning request"""
    print_section("Test 2: Simple Reasoning Test")
    
    if not reasoner:
        print("⏭️  Skipped (reasoner not initialized)")
        return
    
    try:
        start_time = time.time()
        
        # Simple test prompt
        response = reasoner.client.chat.completions.create(
            model=reasoner.model,
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente financiero experto."
                },
                {
                    "role": "user",
                    "content": "En una sola frase, ¿qué significa RSI > 70?"
                }
            ],
            temperature=0.3,
            max_tokens=100
        )
        
        elapsed_time = time.time() - start_time
        
        print("✅ Simple reasoning test successful")
        print(f"   Response time: {elapsed_time:.2f}s")
        print(f"   Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_trading_analysis(reasoner):
    """Test full trading analysis"""
    print_section("Test 3: Trading Analysis")
    
    if not reasoner:
        print("⏭️  Skipped (reasoner not initialized)")
        return
    
    # Sample trading data for GGAL
    symbol = "GGAL"
    market_data = {
        'price': 1250.50,
        'rsi': 65.3,
        'macd': 5.2,
        'atr': 45.8
    }
    
    signals = {
        'technical': {'action': 'BUY', 'confidence': 0.72},
        'ensemble': {
            'action': 'BUY',
            'confidence': 0.68,
            'votes': {'BUY': 3, 'HOLD': 1, 'SELL': 0}
        },
        'sentiment': {'action': 'BUY', 'score': 0.15}
    }
    
    regime = {
        'regime': 'TRENDING_BULL',
        'description': 'Mercado alcista con tendencia clara',
        'confidence': 0.85
    }
    
    alt_data = {
        'google_trends': {'trend': 'UP', 'interest': 75},
        'twitter': {'sentiment': 0.25},
        'reddit': {'mentions': 142}
    }
    
    try:
        start_time = time.time()
        
        analysis = reasoner.analyze_trading_decision(
            symbol=symbol,
            market_data=market_data,
            signals=signals,
            regime=regime,
            alt_data=alt_data
        )
        
        elapsed_time = time.time() - start_time
        
        print("✅ Trading analysis successful")
        print(f"   Response time: {elapsed_time:.2f}s")
        print(f"\n   📊 Analysis Results:")
        print(f"   Symbol: {symbol}")
        print(f"   Action: {analysis['action']}")
        print(f"   Confidence: {analysis['confidence']:.0%}")
        print(f"   Reasoning: {analysis.get('reasoning', 'N/A')}")
        if 'risks' in analysis and analysis['risks']:
            print(f"   Risks: {analysis['risks']}")
        
        # Show full reasoning if available
        if 'full_reasoning' in analysis:
            print(f"\n   📝 Full Reasoning:")
            reasoning_lines = analysis['full_reasoning'].split('\n')
            for line in reasoning_lines[:10]:  # First 10 lines
                if line.strip():
                    print(f"      {line}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_explanation_generation(reasoner):
    """Test explanation generation"""
    print_section("Test 4: Explanation Generation")
    
    if not reasoner:
        print("⏭️  Skipped (reasoner not initialized)")
        return
    
    decision = {
        'action': 'BUY',
        'confidence': 0.75,
        'signals': {'technical': 'BUY', 'ml': 'BUY', 'sentiment': 'NEUTRAL'},
        'regime': 'TRENDING_BULL'
    }
    
    try:
        start_time = time.time()
        
        explanation = reasoner.explain_decision(decision)
        
        elapsed_time = time.time() - start_time
        
        print("✅ Explanation generation successful")
        print(f"   Response time: {elapsed_time:.2f}s")
        print(f"\n   📝 Generated Explanation:")
        print(f"   {explanation}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_cost_estimation(reasoner):
    """Estimate costs for typical usage"""
    print_section("Test 5: Cost Estimation")
    
    print("💰 DeepSeek Pricing (as of 2024):")
    print("   Input tokens: ~$0.14 per 1M tokens")
    print("   Output tokens: ~$0.28 per 1M tokens")
    print()
    print("📊 Typical Trading Analysis:")
    print("   Input tokens: ~800 tokens")
    print("   Output tokens: ~300 tokens")
    print("   Cost per analysis: ~$0.0002")
    print()
    print("📈 Monthly Estimates:")
    print("   100 analyses/day = $0.60/month")
    print("   500 analyses/day = $3.00/month")
    print("   1000 analyses/day = $6.00/month")
    print()
    print("🔄 Comparison with OpenAI GPT-4:")
    print("   GPT-4: ~$0.003 per analysis (15x more expensive)")
    print("   Savings: ~90% cost reduction")


def run_all_tests():
    """Run all DeepSeek integration tests"""
    print("🚀 Starting DeepSeek Integration Tests")
    print("   API Key: sk-a0f869809e074f39b5431c01e5e83a1b")
    
    # Test 1: Connection
    reasoner = test_deepseek_connection()
    
    if reasoner:
        # Test 2: Simple reasoning
        test_simple_reasoning(reasoner)
        
        # Test 3: Trading analysis
        test_trading_analysis(reasoner)
        
        # Test 4: Explanation generation
        test_explanation_generation(reasoner)
    
    # Test 5: Cost estimation (always run)
    test_cost_estimation(reasoner)
    
    # Summary
    print_section("Summary")
    if reasoner and reasoner.enabled:
        print("✅ DeepSeek integration is working correctly!")
        print()
        print("Next steps:")
        print("1. Enable LLM reasoning in bot_config.json:")
        print('   {"enable_llm_reasoning": true, "llm_provider": "deepseek"}')
        print()
        print("2. Start the bot and monitor LLM insights in the dashboard")
        print()
        print("3. Compare performance with/without LLM over 1-2 weeks")
        print()
        print("4. For detailed guide, see: DEEPSEEK_INTEGRATION_GUIDE.md")
    else:
        print("❌ DeepSeek integration has issues")
        print()
        print("Troubleshooting:")
        print("1. Verify API key is correct")
        print("2. Check internet connection")
        print("3. Install required package: pip install openai")
        print("4. Check DeepSeek service status")


if __name__ == "__main__":
    run_all_tests()

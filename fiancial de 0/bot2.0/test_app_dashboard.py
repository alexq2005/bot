"""
Comprehensive Test Suite for Dashboard app.py
Tests all critical functionality of the Streamlit dashboard
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.api.mock_iol_client import MockIOLClient
from src.utils.market_manager import MarketManager

print("\n" + "="*70)
print("COMPREHENSIVE TEST SUITE FOR DASHBOARD APP.PY")
print("="*70 + "\n")

# ==============================================================================
# TEST 1: AppSettings Configuration
# ==============================================================================
print("TEST 1: AppSettings Configuration Management")
print("-" * 70)

try:
    # Import AppSettings from app.py
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'dashboard'))
    from app import AppSettings
    
    # Create config directory if it doesn't exist
    config_dir = Path("data")
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Test 1.1: Initialize AppSettings
    print("1.1 Testing AppSettings initialization...")
    settings = AppSettings()
    assert settings is not None, "AppSettings should initialize"
    print("   ✅ AppSettings initialized")
    
    # Test 1.2: Check default values
    print("\n1.2 Testing default configuration values...")
    assert settings.mock_mode is not None, "mock_mode should be set"
    assert settings.paper_mode is not None, "paper_mode should be set"
    assert settings.mock_initial_capital > 0, "Initial capital should be positive"
    assert settings.trading_interval > 0, "Trading interval should be positive"
    print(f"   ✅ Mock Mode: {settings.mock_mode}")
    print(f"   ✅ Paper Mode: {settings.paper_mode}")
    print(f"   ✅ Initial Capital: ${settings.mock_initial_capital:,.2f}")
    print(f"   ✅ Trading Interval: {settings.trading_interval}s")
    
    # Test 1.3: Mode switching
    print("\n1.3 Testing mode switching...")
    original_mode = settings.get_current_mode()
    print(f"   Original mode: {original_mode}")
    
    # Test MOCK mode
    settings.set_mode("MOCK")
    assert settings.get_current_mode() == "MOCK", "Should be in MOCK mode"
    assert settings.mock_mode == True, "mock_mode should be True"
    assert settings.paper_mode == False, "paper_mode should be False"
    print("   ✅ MOCK mode set correctly")
    
    # Test PAPER mode
    settings.set_mode("PAPER")
    assert settings.get_current_mode() == "PAPER", "Should be in PAPER mode"
    assert settings.mock_mode == False, "mock_mode should be False"
    assert settings.paper_mode == True, "paper_mode should be True"
    print("   ✅ PAPER mode set correctly")
    
    # Test LIVE mode
    settings.set_mode("LIVE")
    assert settings.get_current_mode() == "LIVE", "Should be in LIVE mode"
    assert settings.mock_mode == False, "mock_mode should be False"
    assert settings.paper_mode == False, "paper_mode should be False"
    print("   ✅ LIVE mode set correctly")
    
    # Restore original mode
    settings.set_mode(original_mode)
    print(f"   ✅ Restored to {original_mode} mode")
    
    # Test 1.4: Save and load config
    print("\n1.4 Testing configuration persistence...")
    settings.risk_per_trade = 3.5
    settings.save_config()
    print("   ✅ Configuration saved")
    
    # Load new instance to verify persistence
    settings2 = AppSettings()
    assert settings2.risk_per_trade == 3.5, "Risk per trade should persist"
    print("   ✅ Configuration loaded correctly")
    
    print("\n✅ TEST 1 PASSED: AppSettings working correctly\n")
    
except Exception as e:
    print(f"\n❌ TEST 1 FAILED: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==============================================================================
# TEST 2: Client Initialization (get_client function)
# ==============================================================================
print("TEST 2: Client Initialization and Management")
print("-" * 70)

try:
    from app import get_client
    
    # Create a mock session state
    class MockSessionState:
        def __init__(self):
            self.data = {}
        
        def __contains__(self, key):
            return key in self.data
        
        def __getattr__(self, key):
            if key == 'data':
                return object.__getattribute__(self, 'data')
            return self.data.get(key)
        
        def __setattr__(self, key, value):
            if key == 'data':
                object.__setattr__(self, key, value)
            else:
                self.data[key] = value
        
        def __delitem__(self, key):
            if key in self.data:
                del self.data[key]
    
    # Test 2.1: Initialize client in MOCK mode
    print("2.1 Testing client initialization in MOCK mode...")
    settings = AppSettings()
    settings.set_mode("MOCK")
    
    # Create mock session state
    import streamlit as st
    if not hasattr(st, 'session_state'):
        st.session_state = MockSessionState()
    
    client = get_client(settings)
    assert client is not None, "Client should initialize"
    assert type(client).__name__ == "MockIOLClient", "Should be MockIOLClient"
    print(f"   ✅ Client type: {type(client).__name__}")
    print(f"   ✅ Client authenticated: {client.authenticated}")
    
    # Test 2.2: Verify client has required methods
    print("\n2.2 Testing client has all required methods...")
    required_methods = [
        'authenticate',
        'get_account_balance',
        'get_position',
        'buy',
        'sell',
        'get_historical_data',
        'get_performance',
        'get_current_price',
        'get_last_price',
        'get_portfolio',
        'place_market_order'
    ]
    
    for method in required_methods:
        assert hasattr(client, method), f"Client should have {method} method"
        print(f"   ✅ Has method: {method}")
    
    # Test 2.3: Test client methods work
    print("\n2.3 Testing client methods functionality...")
    
    balance = client.get_account_balance()
    assert balance > 0, "Balance should be positive"
    print(f"   ✅ get_account_balance(): ${balance:,.2f}")
    
    position = client.get_position("GGAL")
    assert position >= 0, "Position should be non-negative"
    print(f"   ✅ get_position('GGAL'): {position}")
    
    price = client.get_current_price("GGAL")
    assert price > 0, "Price should be positive"
    print(f"   ✅ get_current_price('GGAL'): ${price:,.2f}")
    
    portfolio = client.get_portfolio()
    assert portfolio is not None, "Portfolio should not be None"
    print(f"   ✅ get_portfolio(): {type(portfolio)}")
    
    perf = client.get_performance()
    assert 'initial_capital' in perf, "Performance should have initial_capital"
    assert 'current_value' in perf, "Performance should have current_value"
    print(f"   ✅ get_performance(): {len(perf)} metrics")
    
    print("\n✅ TEST 2 PASSED: Client initialization working correctly\n")
    
except Exception as e:
    print(f"\n❌ TEST 2 FAILED: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==============================================================================
# TEST 3: MarketManager Integration
# ==============================================================================
print("TEST 3: MarketManager Integration")
print("-" * 70)

try:
    print("3.1 Testing MarketManager initialization...")
    market_manager = MarketManager()
    assert market_manager is not None, "MarketManager should initialize"
    print("   ✅ MarketManager initialized")
    
    print("\n3.2 Testing market status...")
    status = market_manager.get_market_status()
    assert 'is_open' in status, "Status should have is_open"
    assert 'status' in status, "Status should have status"
    assert 'current_time' in status, "Status should have current_time"
    print(f"   ✅ Market status: {status['status']}")
    print(f"   ✅ Market open: {status['is_open']}")
    print(f"   ✅ Current time: {status['current_time']}")
    
    print("\n3.3 Testing symbol retrieval...")
    categories = ['acciones', 'cedears']
    symbols = market_manager.get_symbols_by_category(categories)
    assert symbols is not None, "Symbols should not be None"
    assert len(symbols) > 0, "Should have at least one symbol"
    print(f"   ✅ Retrieved {len(symbols)} symbols from {categories}")
    print(f"   ✅ Sample symbols: {', '.join(symbols[:5])}")
    
    print("\n✅ TEST 3 PASSED: MarketManager working correctly\n")
    
except Exception as e:
    print(f"\n❌ TEST 3 FAILED: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==============================================================================
# TEST 4: Order Execution Simulation
# ==============================================================================
print("TEST 4: Order Execution Workflow")
print("-" * 70)

try:
    print("4.1 Testing buy order execution...")
    client = MockIOLClient("test", "test", "https://api.iol", 1000000)
    client.authenticate()
    
    initial_balance = client.get_account_balance()
    initial_position = client.get_position("GGAL")
    
    # Execute buy order
    result = client.place_market_order("GGAL", 100, "compra")
    assert result is not None, "Order result should not be None"
    assert result.get("success") == True, "Order should succeed"
    print(f"   ✅ Buy order executed: {result.get('message')}")
    
    new_balance = client.get_account_balance()
    new_position = client.get_position("GGAL")
    
    assert new_balance < initial_balance, "Balance should decrease"
    assert new_position > initial_position, "Position should increase"
    print(f"   ✅ Balance: ${initial_balance:,.2f} → ${new_balance:,.2f}")
    print(f"   ✅ Position: {initial_position} → {new_position}")
    
    print("\n4.2 Testing sell order execution...")
    mid_balance = new_balance
    mid_position = new_position
    
    # Execute sell order
    result = client.place_market_order("GGAL", 50, "venta")
    assert result is not None, "Order result should not be None"
    assert result.get("success") == True, "Order should succeed"
    print(f"   ✅ Sell order executed: {result.get('message')}")
    
    final_balance = client.get_account_balance()
    final_position = client.get_position("GGAL")
    
    assert final_balance > mid_balance, "Balance should increase"
    assert final_position < mid_position, "Position should decrease"
    print(f"   ✅ Balance: ${mid_balance:,.2f} → ${final_balance:,.2f}")
    print(f"   ✅ Position: {mid_position} → {final_position}")
    
    print("\n4.3 Testing portfolio after trades...")
    portfolio = client.get_portfolio()
    assert portfolio is not None, "Portfolio should not be None"
    
    if "activos" in portfolio:
        activos = portfolio["activos"]
        print(f"   ✅ Portfolio has {len(activos)} active positions")
        for activo in activos:
            symbol = activo.get("titulo", {}).get("simbolo", "N/A")
            cantidad = activo.get("cantidad", 0)
            print(f"   ✅ Position: {symbol} x {cantidad}")
    
    print("\n4.4 Testing performance metrics after trades...")
    perf = client.get_performance()
    assert perf['positions'] > 0, "Should have at least one position"
    print(f"   ✅ Initial Capital: ${perf['initial_capital']:,.2f}")
    print(f"   ✅ Current Value: ${perf['current_value']:,.2f}")
    print(f"   ✅ Total Return: ${perf['total_return']:,.2f} ({perf['total_return_pct']:.2f}%)")
    print(f"   ✅ Active Positions: {perf['positions']}")
    
    print("\n✅ TEST 4 PASSED: Order execution working correctly\n")
    
except Exception as e:
    print(f"\n❌ TEST 4 FAILED: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==============================================================================
# TEST 5: Historical Data for Analysis
# ==============================================================================
print("TEST 5: Historical Data Generation for Dashboard Analysis")
print("-" * 70)

try:
    client = MockIOLClient("test", "test", "https://api.iol", 1000000)
    client.authenticate()
    
    print("5.1 Testing historical data retrieval...")
    to_date = datetime.now()
    from_date = to_date - timedelta(days=100)
    
    df = client.get_historical_data("GGAL", from_date, to_date)
    assert df is not None, "DataFrame should not be None"
    assert len(df) >= 50, "Should have sufficient data"
    print(f"   ✅ Retrieved {len(df)} days of data")
    
    print("\n5.2 Validating OHLCV data structure...")
    required_columns = ['open', 'high', 'low', 'close', 'volume']
    for col in required_columns:
        assert col in df.columns, f"Should have {col} column"
        print(f"   ✅ Column present: {col}")
    
    print("\n5.3 Validating data quality...")
    # Check no NaN values
    assert not df.isnull().any().any(), "Should not have NaN values"
    print("   ✅ No NaN values")
    
    # Check all prices are positive
    assert (df['close'] > 0).all(), "All closing prices should be positive"
    assert (df['high'] >= df['low']).all(), "High should be >= low"
    assert (df['high'] >= df['open']).all(), "High should be >= open"
    assert (df['high'] >= df['close']).all(), "High should be >= close"
    assert (df['low'] <= df['open']).all(), "Low should be <= open"
    assert (df['low'] <= df['close']).all(), "Low should be <= close"
    print("   ✅ Price relationships valid")
    
    # Check volume is positive
    assert (df['volume'] > 0).all(), "Volume should be positive"
    print("   ✅ Volume data valid")
    
    print(f"\n5.4 Data statistics:")
    print(f"   ✅ Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    print(f"   ✅ Average price: ${df['close'].mean():.2f}")
    print(f"   ✅ Average volume: {df['volume'].mean():,.0f}")
    
    print("\n✅ TEST 5 PASSED: Historical data generation working correctly\n")
    
except Exception as e:
    print(f"\n❌ TEST 5 FAILED: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==============================================================================
# TEST 6: Configuration Persistence
# ==============================================================================
print("TEST 6: Configuration Persistence Across Sessions")
print("-" * 70)

try:
    print("6.1 Testing configuration file creation...")
    config_file = Path("data/app_config.json")
    
    # Create new settings
    settings1 = AppSettings()
    settings1.set_mode("PAPER")
    settings1.risk_per_trade = 4.5
    settings1.mock_initial_capital = 2000000
    settings1.save_config()
    
    assert config_file.exists(), "Config file should exist"
    print("   ✅ Config file created")
    
    print("\n6.2 Testing configuration reload...")
    # Load settings in new instance
    settings2 = AppSettings()
    
    assert settings2.get_current_mode() == "PAPER", "Mode should persist"
    assert settings2.risk_per_trade == 4.5, "Risk should persist"
    assert settings2.mock_initial_capital == 2000000, "Capital should persist"
    print("   ✅ All configuration values persisted correctly")
    print(f"   ✅ Mode: {settings2.get_current_mode()}")
    print(f"   ✅ Risk: {settings2.risk_per_trade}%")
    print(f"   ✅ Capital: ${settings2.mock_initial_capital:,.2f}")
    
    print("\n6.3 Testing configuration JSON structure...")
    with open(config_file, 'r') as f:
        config_data = json.load(f)
    
    required_keys = [
        'mock_mode', 'paper_mode', 'mock_initial_capital',
        'trading_interval', 'risk_per_trade', 'max_position_size',
        'stop_loss_percent', 'take_profit_percent'
    ]
    
    for key in required_keys:
        assert key in config_data, f"Config should have {key}"
        print(f"   ✅ Has key: {key}")
    
    print("\n✅ TEST 6 PASSED: Configuration persistence working correctly\n")
    
except Exception as e:
    print(f"\n❌ TEST 6 FAILED: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==============================================================================
# FINAL SUMMARY
# ==============================================================================
print("="*70)
print("✅ ALL DASHBOARD TESTS PASSED!")
print("="*70)
print("\nTest Summary:")
print("  ✅ TEST 1: AppSettings Configuration - PASSED")
print("  ✅ TEST 2: Client Initialization - PASSED")
print("  ✅ TEST 3: MarketManager Integration - PASSED")
print("  ✅ TEST 4: Order Execution Workflow - PASSED")
print("  ✅ TEST 5: Historical Data Generation - PASSED")
print("  ✅ TEST 6: Configuration Persistence - PASSED")
print("\n🎉 Dashboard app.py is fully functional!")
print("="*70 + "\n")

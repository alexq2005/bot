"""
Test script for new MockIOLClient methods
Validates all the newly added methods work correctly
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from src.api.mock_iol_client import MockIOLClient

def test_new_methods():
    """Test all newly added methods"""
    print("\n" + "="*70)
    print("TEST NEW MOCKIOLCLIENT METHODS")
    print("="*70 + "\n")
    
    # Create client
    client = MockIOLClient("test", "test", "https://mock.iol", initial_capital=1000000)
    client.authenticate()
    
    # Test 1: get_account_balance
    print("1. Testing get_account_balance()...")
    balance = client.get_account_balance()
    print(f"   ✅ Balance: ${balance:,.2f}")
    assert balance == 1000000, "Initial balance should be 1,000,000"
    
    # Test 2: get_position
    print("\n2. Testing get_position()...")
    position = client.get_position("GGAL")
    print(f"   ✅ Initial position: {position}")
    assert position == 0, "Initial position should be 0"
    
    # Test 3: buy
    print("\n3. Testing buy()...")
    success = client.buy("GGAL", 100)
    print(f"   ✅ Buy result: {success}")
    assert success == True, "Buy should succeed"
    
    new_position = client.get_position("GGAL")
    print(f"   ✅ New position: {new_position}")
    assert new_position == 100, "Position should be 100 after buy"
    
    new_balance = client.get_account_balance()
    print(f"   ✅ New balance: ${new_balance:,.2f}")
    assert new_balance < 1000000, "Balance should decrease after buy"
    
    # Test 4: sell
    print("\n4. Testing sell()...")
    success = client.sell("GGAL", 50)
    print(f"   ✅ Sell result: {success}")
    assert success == True, "Sell should succeed"
    
    final_position = client.get_position("GGAL")
    print(f"   ✅ Final position: {final_position}")
    assert final_position == 50, "Position should be 50 after selling 50"
    
    # Test 5: get_historical_data
    print("\n5. Testing get_historical_data()...")
    to_date = datetime.now()
    from_date = to_date - timedelta(days=100)
    df = client.get_historical_data("GGAL", from_date, to_date)
    print(f"   ✅ DataFrame shape: {df.shape}")
    print(f"   ✅ Columns: {list(df.columns)}")
    assert df is not None, "DataFrame should not be None"
    assert len(df) > 50, "Should have enough historical data"
    assert 'close' in df.columns, "Should have 'close' column"
    assert 'open' in df.columns, "Should have 'open' column"
    assert 'high' in df.columns, "Should have 'high' column"
    assert 'low' in df.columns, "Should have 'low' column"
    assert 'volume' in df.columns, "Should have 'volume' column"
    
    # Test 6: get_performance
    print("\n6. Testing get_performance()...")
    perf = client.get_performance()
    print(f"   ✅ Initial Capital: ${perf['initial_capital']:,.2f}")
    print(f"   ✅ Current Value: ${perf['current_value']:,.2f}")
    print(f"   ✅ Total Return: ${perf['total_return']:,.2f}")
    print(f"   ✅ Total Return %: {perf['total_return_pct']:.2f}%")
    print(f"   ✅ Cash: ${perf['cash']:,.2f}")
    print(f"   ✅ Invested: ${perf['invested']:,.2f}")
    print(f"   ✅ Positions: {perf['positions']}")
    
    assert 'initial_capital' in perf, "Should have initial_capital"
    assert 'current_value' in perf, "Should have current_value"
    assert 'total_return' in perf, "Should have total_return"
    assert 'total_return_pct' in perf, "Should have total_return_pct"
    assert 'cash' in perf, "Should have cash"
    assert 'invested' in perf, "Should have invested"
    assert 'positions' in perf, "Should have positions"
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        test_new_methods()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")
        sys.exit(1)

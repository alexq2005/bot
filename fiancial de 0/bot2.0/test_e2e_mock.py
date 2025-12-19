"""
End-to-end test for MockIOLClient integration with TradingBot
Tests that all new methods work correctly in the full bot context
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from src.api.mock_iol_client import MockIOLClient

def test_e2e_mock_methods():
    """Test all methods in a realistic scenario"""
    print("\n" + "="*70)
    print("END-TO-END TEST: MockIOLClient Full Integration")
    print("="*70 + "\n")
    
    # Initialize client
    print("1. Initializing MockIOLClient...")
    client = MockIOLClient(
        username="test_user",
        password="test_pass",
        base_url="https://api.mock.iol",
        initial_capital=1000000
    )
    
    # Authenticate
    print("2. Authenticating...")
    auth_result = client.authenticate()
    assert auth_result == True, "Authentication failed"
    print("   ✅ Authenticated successfully")
    
    # Test get_account_balance
    print("\n3. Checking initial balance...")
    balance = client.get_account_balance()
    assert balance == 1000000, f"Expected 1000000, got {balance}"
    print(f"   ✅ Initial balance: ${balance:,.2f}")
    
    # Test get_historical_data for technical analysis
    print("\n4. Fetching historical data for GGAL...")
    to_date = datetime.now()
    from_date = to_date - timedelta(days=100)
    df = client.get_historical_data("GGAL", from_date, to_date)
    assert df is not None and len(df) >= 50, "Insufficient historical data"
    print(f"   ✅ Historical data fetched: {len(df)} days")
    print(f"   ✅ Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    
    # Test get_position before trade
    print("\n5. Checking position before trade...")
    position = client.get_position("GGAL")
    assert position == 0, f"Expected 0, got {position}"
    print(f"   ✅ Position: {position} shares")
    
    # Test buy operation
    print("\n6. Executing BUY order...")
    current_price = client.get_current_price("GGAL")
    print(f"   Current price: ${current_price:.2f}")
    buy_result = client.buy("GGAL", 100)
    assert buy_result == True, "Buy operation failed"
    print("   ✅ BUY successful: 100 shares")
    
    # Verify position after buy
    position_after_buy = client.get_position("GGAL")
    assert position_after_buy == 100, f"Expected 100, got {position_after_buy}"
    print(f"   ✅ Position after buy: {position_after_buy} shares")
    
    # Verify balance decreased
    balance_after_buy = client.get_account_balance()
    assert balance_after_buy < 1000000, "Balance should decrease after buy"
    print(f"   ✅ Balance after buy: ${balance_after_buy:,.2f}")
    
    # Test sell operation
    print("\n7. Executing SELL order...")
    sell_result = client.sell("GGAL", 50)
    assert sell_result == True, "Sell operation failed"
    print("   ✅ SELL successful: 50 shares")
    
    # Verify position after sell
    position_after_sell = client.get_position("GGAL")
    assert position_after_sell == 50, f"Expected 50, got {position_after_sell}"
    print(f"   ✅ Position after sell: {position_after_sell} shares")
    
    # Verify balance increased
    balance_after_sell = client.get_account_balance()
    assert balance_after_sell > balance_after_buy, "Balance should increase after sell"
    print(f"   ✅ Balance after sell: ${balance_after_sell:,.2f}")
    
    # Test get_performance
    print("\n8. Getting portfolio performance...")
    perf = client.get_performance()
    
    # Verify all required fields
    required_fields = [
        'initial_capital', 'current_value', 'total_return', 
        'total_return_pct', 'cash', 'invested', 'positions'
    ]
    for field in required_fields:
        assert field in perf, f"Missing field: {field}"
    
    print(f"   ✅ Initial Capital: ${perf['initial_capital']:,.2f}")
    print(f"   ✅ Current Value: ${perf['current_value']:,.2f}")
    print(f"   ✅ Total Return: ${perf['total_return']:,.2f} ({perf['total_return_pct']:.2f}%)")
    print(f"   ✅ Cash: ${perf['cash']:,.2f}")
    print(f"   ✅ Invested: ${perf['invested']:,.2f}")
    print(f"   ✅ Active Positions: {perf['positions']}")
    
    # Validate performance calculations
    assert perf['initial_capital'] == 1000000, "Initial capital mismatch"
    assert perf['positions'] == 1, f"Expected 1 position, got {perf['positions']}"
    assert perf['cash'] == balance_after_sell, "Cash mismatch"
    assert abs(perf['current_value'] - (perf['cash'] + perf['invested'])) < 0.01, \
        "Current value calculation error"
    
    print("\n" + "="*70)
    print("✅ ALL E2E TESTS PASSED!")
    print("="*70)
    print("\nSummary:")
    print("  • Authentication: WORKING")
    print("  • get_account_balance(): WORKING")
    print("  • get_position(): WORKING")
    print("  • buy(): WORKING")
    print("  • sell(): WORKING")
    print("  • get_historical_data(): WORKING")
    print("  • get_performance(): WORKING")
    print("\n✅ MockIOLClient is fully functional for TradingBot integration")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        test_e2e_mock_methods()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

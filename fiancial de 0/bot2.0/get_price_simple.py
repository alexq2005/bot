"""
Versión simplificada de get_market_price_by_mode para debugging
"""

def get_market_price_DIRECT(symbol: str) -> dict:
    """Obtiene precio directamente de MockIOLClient sin complejidad"""
    
    # Importar directamente MockIOLClient
    from src.api.mock_iol_client import MockIOLClient
    
    # Crear cliente
    client = MockIOLClient("test", "test", "https://mock")
    
    # Autenticar
    if not client.authenticate():
        return {'price': 0}
    
    # Obtener quote
    quote = client.get_last_price(symbol, "bCBA")
    
    if quote and quote.get('price', 0) > 0:
        return {
            'price': quote.get('price', 0),
            'variation': quote.get('variationRate', 0),
            'volume': quote.get('amount', 0),
            'opening': quote.get('opening', 0),
            'high': quote.get('maxDay', 0),
            'low': quote.get('minDay', 0),
            'previous_close': quote.get('settlementPrice', 0),
            'is_market_open': True
        }
    
    return {'price': 0}


# Prueba rápida
if __name__ == "__main__":
    result = get_market_price_DIRECT("GGAL")
    print(f"Resultado: {result}")
    print(f"Precio: ${result.get('price', 0)}")

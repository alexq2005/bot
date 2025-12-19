"""
Cliente IOL (Invertir Online)

Integración con la API de IOL para:
- Autenticación
- Obtención de datos de mercado
- Ejecución de órdenes
- Consulta de portafolio

Documentación IOL API: https://api.invertironline.com/
"""

import logging
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)

class IOLClient:
    """Cliente para integración con API de Invertir Online"""

    BASE_URL = "https://api.invertironline.com"
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Inicializa el cliente IOL.
        
        Args:
            username: Usuario de IOL
            password: Contraseña de IOL
        """
        self.username = username
        self.password = password
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        
        # Cache de símbolos inválidos para evitar reintentos innecesarios
        self.invalid_symbols = set()  # Símbolos que no existen en IOL

        # Modo Mock si no hay credenciales
        self.mock_mode = not (username and password)
        if self.mock_mode:
            logger.warning("⚠️ Credenciales no proporcionadas. Iniciando en MOCK MODE.")

    def _is_token_valid(self) -> bool:
        """Verifica si el token actual es válido"""
        if not self.access_token or not self.token_expiry:
            return False
        return datetime.now().timestamp() < self.token_expiry

    def _refresh_token(self) -> bool:
        """
        Refresca el bearer token usando el refresh token.
        Según documentación de IOL: POST /token con refresh_token y grant_type=refresh_token
        """
        if not self.refresh_token:
            logger.warning("⚠️ No hay refresh token disponible. Se requiere autenticación completa.")
            return False
        
        logger.info("🔄 Refrescando token de IOL...")
        endpoint = f"{self.BASE_URL}/token"
        
        data = {
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token"
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            response = requests.post(endpoint, data=data, headers=headers, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in", 300)
            
            # Calcular expiración (con margen de seguridad de 60s)
            self.token_expiry = datetime.now().timestamp() + expires_in - 60
            
            logger.info("✅ Token refrescado exitosamente")
            return True
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Error HTTP al refrescar token: {e.response.status_code} - {e.response.text}")
            # Si el refresh token también expiró, necesitamos autenticación completa
            if e.response.status_code == 401:
                logger.info("🔄 Refresh token expirado. Se requiere autenticación completa.")
                self.refresh_token = None
            return False
        except Exception as e:
            logger.error(f"❌ Error al refrescar token: {str(e)}")
            return False

    def authenticate(self) -> bool:
        """
        Autentica con IOL y obtiene el Bearer Token.
        """
        if self.mock_mode:
            logger.info("🔐 [MOCK] Autenticación simulada exitosa")
            return True

        logger.info("🔐 Autenticando con IOL...")
        endpoint = f"{self.BASE_URL}/token"
        
        # Según la documentación de IOL, debe ser application/x-www-form-urlencoded
        data = {
            "username": self.username,
            "password": self.password,
            "grant_type": "password"
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            # Enviar como form-urlencoded según documentación de IOL
            response = requests.post(endpoint, data=data, headers=headers, timeout=10)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in", 300)

            # Calcular expiración (con margen de seguridad de 60s)
            self.token_expiry = datetime.now().timestamp() + expires_in - 60

            logger.info("✅ Autenticación exitosa")
            logger.debug(f"Token obtenido: {self.access_token[:20]}..." if self.access_token else "Token no obtenido")
            return True

        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Error HTTP en autenticación: {e.response.status_code} - {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"❌ Error de autenticación: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return False

    def _get_headers(self) -> Dict:
        """Obtiene headers para requests"""
        if not self.mock_mode:
            if not self._is_token_valid():
                # Intentar refrescar el token primero si hay refresh_token
                if self.refresh_token:
                    if not self._refresh_token():
                        # Si el refresh falla, intentar autenticación completa
                        self.authenticate()
                else:
                    # No hay refresh token, autenticación completa
                    self.authenticate()

        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def get_market_data(self, symbol: str, market: str = "bCBA") -> Optional[Dict]:
        """
        Obtiene datos de mercado en tiempo real (Cotización).
        
        Args:
            symbol: Símbolo del activo
            market: Mercado (bCBA, bNYP, etc.)
        
        Returns:
            Dict con datos de mercado o None si no se encuentra
        """
        if self.mock_mode:
            # Generar datos simulados
            import random
            base_price = 1000.0 if symbol == "GGAL" else 500.0
            variation = random.uniform(-0.02, 0.02)
            price = base_price * (1 + variation)
            
            return {
                "symbol": symbol,
                "last_price": round(price, 2),
                "bid": round(price * 0.99, 2),
                "ask": round(price * 1.01, 2),
                "volume": random.randint(1000, 50000),
                "timestamp": datetime.now().isoformat()
            }

        # Verificar si el símbolo ya está marcado como inválido
        if symbol in self.invalid_symbols:
            return None
        
        # Normalizar símbolo: Para acciones argentinas en BCBA, IOL generalmente requiere .BA
        # Intentar primero con .BA si no tiene sufijo, luego sin .BA si falla
        symbol_normalized = symbol
        symbol_to_try_first = symbol
        
        # Para acciones argentinas en BCBA, intentar primero con .BA
        # NO agregar .BA para bonos (AL30, GD30, etc.) ni para CEDEARs
        if market == "bCBA" and not symbol.endswith(".BA") and not symbol.endswith(".USD"):
            # Detectar si es un bono (empieza con AL, GD, AE, o contiene CUAP, DICA, PARP)
            is_bono = (
                symbol.upper().startswith("AL") or 
                symbol.upper().startswith("GD") or 
                symbol.upper().startswith("AE") or
                any(x in symbol.upper() for x in ["CUAP", "DICA", "PARP"])
            )
            # Solo agregar .BA si parece ser una acción argentina (no CEDEAR, no ON, no BONO)
            if not is_bono and not any(x in symbol.upper() for x in ["CEDEAR", "ON", "BONO"]):
                # Intentar primero CON .BA (formato más común para acciones argentinas)
                symbol_to_try_first = f"{symbol}.BA"
        
        logger.debug(f"Consultando IOL: {symbol_to_try_first} en mercado {market}")
        # Según documentación IOL v2: GET /api/v2/{Mercado}/Titulos/{Simbolo}/Cotizacion
        # También acepta query parameters: model.simbolo y model.mercado
        # Intentar primero con v2, luego con v1 como fallback
        endpoint_v2 = f"{self.BASE_URL}/api/v2/{market}/Titulos/{symbol_to_try_first}/Cotizacion"
        endpoint_v1 = f"{self.BASE_URL}/api/{market}/Titulos/{symbol_to_try_first}/Cotizacion"
        
        # Agregar query parameters según documentación (opcional pero puede ayudar)
        params = {
            "model.simbolo": symbol_to_try_first,
            "model.mercado": market
        }
        
        data = None
        try:
            # Intentar primero con v2
            headers = self._get_headers()
            logger.debug(f"🔍 Consultando IOL v2: {endpoint_v2} con params: {params}")
            response = requests.get(endpoint_v2, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info(f"✅ Datos obtenidos desde IOL v2 para {symbol_to_try_first}")
        except requests.exceptions.HTTPError as e:
            error_status = e.response.status_code
            error_text = e.response.text[:200] if hasattr(e.response, 'text') else str(e)
            logger.warning(f"⚠️ Error HTTP {error_status} con v2 para {symbol_to_try_first}: {error_text}")
            
            if error_status == 404:
                # Si v2 falla con 404, intentar con v1
                logger.debug(f"🔄 Intentando con v1 como fallback para {symbol_to_try_first}...")
                try:
                    response_v1 = requests.get(endpoint_v1, headers=headers, params=params, timeout=10)
                    response_v1.raise_for_status()
                    data = response_v1.json()
                    logger.info(f"✅ Datos obtenidos desde IOL v1 para {symbol_to_try_first}")
                except Exception as e_v1:
                    logger.debug(f"⚠️ v1 también falló: {e_v1}")
                    # Re-lanzar el error original de v2 para que se maneje más abajo
                    raise e
            else:
                # Para otros errores HTTP, re-lanzar
                raise e
        except Exception as e:
            logger.error(f"❌ Error al consultar IOL para {symbol_to_try_first}: {str(e)}")
            # Re-lanzar para que se maneje más abajo
            raise e
        
        if not data:
            logger.warning(f"⚠️ No se obtuvieron datos para {symbol_to_try_first}")
            return None
        
        # Normalizar respuesta de IOL para asegurar que siempre tenga last_price
        if isinstance(data, dict):
            # IOL puede retornar el precio en diferentes campos
            # Normalizar a last_price para consistencia
            if "last_price" not in data or data.get("last_price") is None:
                # Intentar obtener precio desde diferentes campos de IOL
                price = (
                    data.get("ultimoPrecio") or
                    data.get("precio") or
                    data.get("close") or
                    data.get("cierre") or
                    data.get("ultimo") or
                    0
                )
                if price and price > 0:
                    data["last_price"] = float(price)
            
            # Normalizar bid/ask desde punta compra/venta
            # Según documentación IOL, las puntas vienen en un array "puntas"
            if "puntas" in data and isinstance(data["puntas"], list) and len(data["puntas"]) > 0:
                # Tomar la primera punta (mejor precio)
                primera_punta = data["puntas"][0]
                if "precioCompra" in primera_punta and primera_punta["precioCompra"] > 0:
                    data["bid"] = float(primera_punta["precioCompra"])
                if "precioVenta" in primera_punta and primera_punta["precioVenta"] > 0:
                    data["ask"] = float(primera_punta["precioVenta"])
            
            # Si aún no hay bid/ask, intentar campos directos
            if "bid" not in data or data.get("bid") is None or data.get("bid") == 0:
                bid = (
                    data.get("compra") or
                    data.get("puntaCompra") or
                    0
                )
                if bid and bid > 0:
                    data["bid"] = float(bid)
            
            if "ask" not in data or data.get("ask") is None or data.get("ask") == 0:
                ask = (
                    data.get("venta") or
                    data.get("puntaVenta") or
                    0
                )
                if ask and ask > 0:
                    data["ask"] = float(ask)
        
        return data

    def get_available_instruments(self, pais: str = "argentina") -> List[str]:
        """
        Obtiene la lista de instrumentos disponibles en IOL.
        Según documentación: GET /api/v2/{pais}/Titulos/Cotizacion/Instrumentos
        
        Args:
            pais: País (argentina, estados_Unidos, etc.)
        
        Returns:
            Lista de símbolos disponibles
        """
        if self.mock_mode:
            # Retornar lista básica simulada
            return ["GGAL", "YPFD", "PAMP", "ALUA", "BMA", "TXAR", "EDN", "CRES"]
        
        # Mapear país a formato IOL
        pais_map = {
            "argentina": "argentina",
            "estados_unidos": "estados_Unidos",
            "usa": "estados_Unidos"
        }
        pais_iol = pais_map.get(pais.lower(), pais)
        
        endpoint = f"{self.BASE_URL}/api/v2/{pais_iol}/Titulos/Cotizacion/Instrumentos"
        
        try:
            headers = self._get_headers()
            response = requests.get(endpoint, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extraer símbolos de la respuesta
            symbols = []
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "instrumento" in item:
                        symbols.append(item["instrumento"])
                    elif isinstance(item, str):
                        symbols.append(item)
            
            logger.info(f"✅ Obtenidos {len(symbols)} instrumentos desde IOL para {pais_iol}")
            return symbols
            
        except requests.exceptions.HTTPError as e:
            logger.warning(f"⚠️ Error HTTP obteniendo instrumentos: {e.response.status_code} - {e.response.text[:200]}")
            return []
        except Exception as e:
            logger.error(f"❌ Error obteniendo instrumentos desde IOL: {e}")
            return []

    def get_all_quotations(self, instrumento: str, pais: str = "argentina") -> List[Dict]:
        """
        Obtiene todas las cotizaciones para un instrumento específico.
        Según documentación: GET /api/v2/Cotizaciones/{Instrumento}/{Pais}/Todos
        
        Args:
            instrumento: Tipo de instrumento (acciones, cedears, bonos, etc.)
            pais: País (argentina, estados_Unidos, etc.)
        
        Returns:
            Lista de títulos con sus cotizaciones
        """
        if self.mock_mode:
            return []
        
        # Mapear país a formato IOL
        pais_map = {
            "argentina": "argentina",
            "estados_unidos": "estados_Unidos",
            "usa": "estados_Unidos"
        }
        pais_iol = pais_map.get(pais.lower(), pais)
        
        endpoint = f"{self.BASE_URL}/api/v2/Cotizaciones/{instrumento}/{pais_iol}/Todos"
        
        try:
            headers = self._get_headers()
            params = {
                "cotizacionInstrumentoModel.instrumento": instrumento,
                "cotizacionInstrumentoModel.pais": pais_iol
            }
            response = requests.get(endpoint, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Extraer símbolos de los títulos
            symbols = []
            if isinstance(data, dict) and "titulos" in data:
                for titulo in data["titulos"]:
                    if isinstance(titulo, dict) and "simbolo" in titulo:
                        symbols.append(titulo["simbolo"])
            
            logger.info(f"✅ Obtenidos {len(symbols)} símbolos con cotizaciones para {instrumento} en {pais_iol}")
            return symbols
            
        except requests.exceptions.HTTPError as e:
            logger.warning(f"⚠️ Error HTTP obteniendo cotizaciones: {e.response.status_code} - {e.response.text[:200]}")
            return []
        except Exception as e:
            logger.error(f"❌ Error obteniendo cotizaciones desde IOL: {e}")
            return []

    def get_historical_data(self, symbol: str, start_date: str, end_date: str, market: str = "bCBA") -> List[Dict]:
        """
        Obtiene datos históricos para análisis técnico.
        """
        if self.mock_mode:
            # Simular una lista de velas históricas
            # Esto es necesario para que pandas-ta funcione en la demo
            data = []
            import random
            current_price = 1000.0
            
            # Generar 100 velas
            for i in range(100):
                change = random.uniform(-0.02, 0.02)
                open_p = current_price
                close_p = open_p * (1 + change)
                high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.01))
                low_p = min(open_p, close_p) * (1 - random.uniform(0, 0.01))
                vol = random.randint(1000, 10000)

                data.append({
                    "fecha": f"2024-01-{i+1:02d}", # Fecha simulada
                    "apertura": open_p,
                    "cierre": close_p,
                    "maximo": high_p,
                    "minimo": low_p,
                    "volumen": vol
                })
                current_price = close_p
            return data

        endpoint = f"{self.BASE_URL}/api/v2/{market}/Titulos/{symbol}/Cotizacion/seriehistorica/{start_date}/{end_date}/ajustada"
        try:
            response = requests.get(endpoint, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error obteniendo histórico de {symbol}: {e}")
            return []
    
    def get_last_close_price(self, symbol: str, market: str = "bCBA") -> Optional[Dict]:
        """
        Obtiene el último precio de cierre disponible para un símbolo.
        Útil cuando el mercado está cerrado y no hay cotización en tiempo real.
        
        Args:
            symbol: Símbolo del activo
            market: Mercado (bCBA, nYSE, etc.)
        
        Returns:
            Dict con último precio de cierre o None si no se encuentra
        """
        if self.mock_mode:
            import random
            base_price = 1000.0
            return {
                "symbol": symbol,
                "last_price": round(base_price * random.uniform(0.95, 1.05), 2),
                "close_date": "2024-01-15",
                "is_historical": True
            }
        
        try:
            # Obtener últimos 5 días de datos históricos
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=10)  # 10 días para asegurar datos
            
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
            
            logger.debug(f"Obteniendo último cierre para {symbol} desde {start_str} hasta {end_str}")
            
            historical_data = self.get_historical_data(symbol, start_str, end_str, market)
            
            if historical_data and len(historical_data) > 0:
                # Tomar el último registro disponible
                last_record = historical_data[-1]
                
                # Extraer precio de cierre (IOL puede usar diferentes nombres de campo)
                close_price = (
                    last_record.get("cierre") or
                    last_record.get("close") or
                    last_record.get("ultimoPrecio") or
                    last_record.get("last_price") or
                    0
                )
                
                if close_price and close_price > 0:
                    logger.info(f"✅ Último cierre obtenido para {symbol}: ${close_price} (fecha: {last_record.get('fecha', 'N/A')})")
                    
                    return {
                        "symbol": symbol,
                        "last_price": float(close_price),
                        "ultimoPrecio": float(close_price),
                        "close_date": last_record.get("fecha", end_str),
                        "is_historical": True,
                        "volume": last_record.get("volumen", 0),
                        # Calcular bid/ask aproximados con spread del 0.5%
                        "bid": round(float(close_price) * 0.995, 2),
                        "ask": round(float(close_price) * 1.005, 2)
                    }
            
            logger.warning(f"⚠️ No se encontraron datos históricos para {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo último cierre para {symbol}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None


    def place_order(self, symbol: str, side: str, quantity: int, price: float, order_type: str = "Limit") -> Optional[Dict]:
        """
        Coloca una orden de compra o venta.
        side: 'comprar' o 'vender'
        """
        # Validar parámetros
        if not price or price <= 0:
            logger.error(f"❌ Precio inválido para orden: {price}")
            return None
        
        if quantity <= 0:
            logger.error(f"❌ Cantidad inválida para orden: {quantity}")
            return None
        
        if not symbol:
            logger.error(f"❌ Símbolo inválido para orden: {symbol}")
            return None
        
        if self.mock_mode:
            logger.info(f"📝 [MOCK] Orden enviada: {side} {quantity} {symbol} @ {price}")
            return {"orderId": 12345, "status": "pending", "message": "Orden simulada exitosa"}

        # Normalizar side a formato de IOL
        side_normalized = "Comprar" if side.lower() in ["comprar", "buy", "compra"] else "Vender"
        
        # Asegurar que el símbolo tenga el sufijo .BA si es necesario (para acciones argentinas)
        symbol_normalized = symbol
        if not symbol.endswith(".BA") and not any(x in symbol.upper() for x in ["CEDEAR", "ON", "BONO"]):
            # Agregar .BA solo si parece ser una acción argentina
            symbol_normalized = f"{symbol}.BA"
        
        endpoint = f"{self.BASE_URL}/api/v2/operar/{side_normalized.lower()}"
        payload = {
            "simbolo": symbol_normalized,
            "cantidad": int(quantity),
            "precio": float(price),
            "plazo": "t0",  # Contado Inmediato
            "mercado": "bCBA"
        }
        
        try:
            logger.info(f"📤 Enviando orden: {side_normalized} {quantity} {symbol_normalized} @ ${price:.2f}")
            response = requests.post(endpoint, json=payload, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"✅ Orden enviada exitosamente: {symbol_normalized} - ID: {result.get('numero', 'N/A')}")
            return result
        except requests.exceptions.HTTPError as e:
            # Log detallado del error
            error_detail = ""
            try:
                error_detail = response.json() if hasattr(e, 'response') and e.response else str(e)
                logger.error(f"❌ Error HTTP al enviar orden: {e.response.status_code} - {error_detail}")
            except:
                logger.error(f"❌ Error HTTP al enviar orden: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error al enviar orden: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def get_portfolio(self) -> Dict:
        """Obtiene el estado del portafolio"""
        if self.mock_mode:
            return {
                "total_value": 1000000.0,
                "available_cash": 250000.0,
                "assets": [
                    {"symbol": "GGAL", "quantity": 100, "last_price": 2500.0, "avg_price": 2400.0},
                    {"symbol": "YPFD", "quantity": 50, "last_price": 18000.0, "avg_price": 17500.0}
                ]
            }

        # Endpoint correcto para obtener portafolio
        endpoint = f"{self.BASE_URL}/api/v2/portafolio/argentina"
        try:
            response = requests.get(endpoint, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            
            # Parsear respuesta de IOL al formato esperado
            assets = []
            total_value = 0
            available_cash = 0
            
            # IOL devuelve estructura: {"activos": [...], "totales": {...}}
            if "activos" in data:
                for item in data["activos"]:
                    asset = {
                        "symbol": item.get("titulo", {}).get("simbolo", ""),
                        "quantity": item.get("cantidad", 0),
                        "last_price": item.get("ultimoPrecio", 0),
                        "avg_price": item.get("ppc", 0),  # Precio Promedio de Compra
                        "current_value": item.get("valorizado", 0)
                    }
                    assets.append(asset)
                    total_value += asset["current_value"]
            
            # Obtener efectivo disponible - Intentar múltiples ubicaciones
            available_cash = 0
            if "totales" in data:
                # Intentar diferentes estructuras de respuesta de IOL
                totales = data["totales"]
                if isinstance(totales, dict):
                    # Estructura: {"saldos": {"disponible": X}}
                    if "saldos" in totales:
                        saldos = totales["saldos"]
                        if isinstance(saldos, dict):
                            available_cash = saldos.get("disponible", saldos.get("disponibleEnCuenta", 0))
                    # Estructura alternativa: {"disponible": X} directamente en totales
                    if available_cash == 0:
                        available_cash = totales.get("disponible", totales.get("disponibleEnCuenta", 0))
            
            # Si aún es 0, intentar buscar en la raíz del response
            if available_cash == 0:
                available_cash = data.get("disponible", data.get("disponibleEnCuenta", data.get("saldoDisponible", 0)))
            
            # Si available_cash es 0, intentar obtenerlo desde estado de cuenta
            if available_cash == 0:
                try:
                    account_status = self.get_account_status()
                    available_cash = account_status.get("available_cash", 0)
                except:
                    pass  # Si falla, mantener 0
            
            return {
                "total_value": total_value,
                "available_cash": available_cash,
                "assets": assets,
                "raw_data": data  # Incluir datos raw para debugging
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo portafolio: {e}")
            return {"total_value": 0, "available_cash": 0, "assets": []}
    
    def get_account_status(self) -> Dict:
        """
        Obtiene el estado de cuenta completo, incluyendo saldo disponible.
        Este endpoint tiene información más detallada que el portfolio.
        
        Estructura real de IOL:
        {
            "cuentas": [
                {
                    "tipo": "inversion_Argentina_Pesos",
                    "moneda": "peso_Argentino",
                    "disponible": 787.02,  # <-- AQUÍ ESTÁ
                    "saldos": [
                        {
                            "liquidacion": "inmediato",
                            "disponible": 787.02,
                            "disponibleOperar": 787.02
                        }
                    ]
                }
            ]
        }
        """
        if self.mock_mode:
            return {
                "available_cash": 250000.0,
                "total_value": 1000000.0,
                "currency": "ARS"
            }
        
        endpoint = f"{self.BASE_URL}/api/v2/estadocuenta"
        try:
            response = requests.get(endpoint, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            
            # Buscar saldo disponible en la estructura real de IOL
            available_cash = 0
            
            # La estructura real: buscar en cuentas, específicamente en la cuenta de pesos argentinos
            if "cuentas" in data and isinstance(data["cuentas"], list):
                for cuenta in data["cuentas"]:
                    if isinstance(cuenta, dict):
                        # Buscar cuenta en pesos argentinos
                        moneda = cuenta.get("moneda", "")
                        tipo = cuenta.get("tipo", "")
                        
                        # Priorizar cuenta de inversión en pesos argentinos
                        if "peso_Argentino" in moneda or "inversion_Argentina_Pesos" in tipo:
                            # Primero intentar desde el campo "disponible" directo
                            cash = cuenta.get("disponible", 0)
                            if cash > 0:
                                available_cash = cash
                                break
                            
                            # Si no, buscar en saldos[0].disponible (liquidación inmediata)
                            if available_cash == 0 and "saldos" in cuenta:
                                saldos = cuenta.get("saldos", [])
                                if isinstance(saldos, list) and len(saldos) > 0:
                                    # Buscar saldo de liquidación inmediata
                                    for saldo in saldos:
                                        if saldo.get("liquidacion") == "inmediato":
                                            cash = saldo.get("disponible") or saldo.get("disponibleOperar", 0)
                                            if cash > 0:
                                                available_cash = cash
                                                break
                            
                            if available_cash > 0:
                                break
                
                # Si no se encontró en pesos, tomar la primera cuenta con saldo disponible
                if available_cash == 0:
                    for cuenta in data["cuentas"]:
                        if isinstance(cuenta, dict):
                            cash = cuenta.get("disponible", 0)
                            if cash > 0:
                                available_cash = cash
                                break
            
            return {
                "available_cash": available_cash,
                "raw_data": data  # Incluir para debugging
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estado de cuenta: {e}")
            return {"available_cash": 0}
    
    def get_available_cash(self) -> float:
        """
        Obtiene el saldo disponible para operar.
        Intenta desde estado de cuenta primero, luego desde portfolio.
        """
        # Intentar desde estado de cuenta (más confiable)
        try:
            account_status = self.get_account_status()
            cash = account_status.get("available_cash", 0)
            if cash > 0:
                return float(cash)
        except Exception as e:
            logger.debug(f"No se pudo obtener saldo desde estado de cuenta: {e}")
        
        # Fallback: intentar desde portfolio
        try:
            portfolio = self.get_portfolio()
            cash = portfolio.get("available_cash", 0)
            return float(cash) if cash else 0.0
        except Exception as e:
            logger.debug(f"No se pudo obtener saldo desde portfolio: {e}")
            return 0.0

__all__ = ['IOLClient']

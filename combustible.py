from __future__ import annotations
import json
from typing import Any, Dict, List, Optional, Tuple
import requests 
from geopy.distance import geodesic

API_URL = "https://integracion.copec.cl/stations?codEs=-1&company=-1&region=-1&comuna=-1"

class InputValidationError(ValueError):
    pass

class ExternalAPIError(RuntimeError):
    pass

# Mapeo productos
def map_product(product: str) -> str:
    if not isinstance(product, str) or not product.strip():
        raise InputValidationError("Parámetro 'product' inválido")
    p = product.strip().lower()
    mapping = {
        "93": "Gasolina 93",
        "95": "Gasolina 95",
        "97": "Gasolina 97",
        "diesel": "Diesel",
        "kerosene": "Kerosene"
    }
    if p not in mapping:
        raise InputValidationError("Producto inválido. Opciones válidas: 93, 95, 97, Diesel, Kerosene.")
    return mapping[p]

# Distancia (geodesic) 
def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return geodesic((lat1, lon1), (lat2, lon2)).km

def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(str(value).strip().replace(",", "."))
    except Exception:
        return None

# Obtener data estaciones de combustible
def data_stations(timeout: int) -> List[Dict[str, Any]]:
    try:
        resp = requests.get(API_URL, timeout=timeout)
    except requests.RequestException as e:
        raise ExternalAPIError(f"Error al llamar API externa: {e}")
    if not resp.ok:
        raise ExternalAPIError(f"API externa respondió {resp.status_code}")

    try:
        data = resp.json()
    except json.JSONDecodeError:
        raise ExternalAPIError("La API no devolvió JSON válido")

    if not isinstance(data, list):
        raise ExternalAPIError("Formato inesperado de respuesta API Copec")
    return data

# Obtener precio según el producto
def get_station_price(station: Dict[str, Any], product: str) -> Optional[int]:
    prices = station.get("Prices") or []
    if not isinstance(prices, list):
        return None
    for item in prices:
        name = str(item.get("Producto") or "").strip()
        price_raw = item.get("Precio")
        if name.lower() == product.lower():
            try:
                return int(str(price_raw).strip())
            except (ValueError, TypeError):
                return None
    return None


def has_store(station: Dict[str, Any]) -> bool:
    tienda = station.get("Tienda")
    if not isinstance(tienda, dict):
        return False
    return any([
        str(tienda.get("NombreTienda") or "").strip(),
        str(tienda.get("CodigoTienda") or "").strip(),
        str(tienda.get("Tipo") or "").strip()
    ])

def _station_coords(st: Dict[str, Any]) -> Optional[Tuple[float, float]]:
    lat = _to_float(st.get("Latitud") or st.get("latitud"))
    lng = _to_float(st.get("Longitud") or st.get("longitud"))
    return None if (lat is None or lng is None) else (lat, lng)

# Formato de salida (json)
def build_response(station: Dict[str, Any], product: str, dist_km: float, price: Optional[int]) -> Dict[str, Any]:
    tienda = station.get("Tienda") or {}
    return {
        "id": str(station.get("CodEs") or ""),
        "compania": station.get("Compania") or "",
        "direccion": station.get("Direccion") or "",
        "comuna": station.get("Comuna") or "",
        "region": station.get("Region") or "",
        "latitud": _to_float(station.get("Latitud")),
        "longitud": _to_float(station.get("Longitud")),
        "distancia_lineal": round(dist_km, 3),
        "precio_producto": price,
        "tienda": {
            "codigo": tienda.get("CodigoTienda") or "",
            "nombre": tienda.get("NombreTienda") or "",
            "tipo": tienda.get("Tipo") or "",
        },
        "tiene_tienda": has_store(station),
        "producto": product,
    }

def search_station(
    lat: float,
    lng: float,
    product: str,
    nearest: bool = False,
    store: bool = False,
    cheapest: bool = False,
    timeout: int = 5,
) -> Dict[str, Any]:
    
    product = map_product(product)
    if not any([nearest, store, cheapest]):  
        nearest = True

    stations = data_stations(timeout=timeout)

    candidates = []
    for st in stations:
        coords = _station_coords(st)
        if not coords:
            continue
        price = get_station_price(st, product)
        if price is None:
            continue
        if store and not has_store(st):
            continue
        dist = distance_km(float(lat), float(lng), coords[0], coords[1])
        candidates.append((st, price, dist))

    if not candidates:
        return {
            "success": False,
            "data": {
                "error": "NO_RESULTS",
                "message": "No se encontraron estaciones que cumplan los criterios."
            }
        }

    if cheapest:
        min_price = min(p for _, p, _ in candidates)
        candidates = [(st, p, d) for st, p, d in candidates if p == min_price]

    candidates.sort(key=lambda x: x[2]) 
    st, price, dist = candidates[0]
    return {"success": True, "data": build_response(st, product, dist, price)}

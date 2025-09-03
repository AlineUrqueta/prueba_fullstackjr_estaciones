import json
from combustible import search_station, map_product,InputValidationError, ExternalAPIError

def _leer_float(prompt: str) -> float:
    while True:
        txt = input(prompt).strip().replace(",", ".")
        try:
            return float(txt)
        except ValueError:
            print("Ingresa un número válido (usa punto decimal).")

def _leer_producto(prompt: str) -> str:
    while True:
        p = input(prompt).strip().lower()
        try:
            map_product(p)
            return p
        except InputValidationError as e:
            print(e)

def _leer_opcion(prompt: str, opciones_validas):
    while True:
        op = input(prompt).strip()
        if op in opciones_validas:
            return op
        print(f"Opción inválida. Elige una de: {', '.join(sorted(opciones_validas))}")

def main():
    print(
        "\n" +
        "============================================================\n"
        "=====      Búsqueda de Estaciones de Combustible       =====\n"
        "============================================================\n"
    )

    print("\nIngrese los siguientes datos:")
    while True:
        lat = _leer_float("Latitud  (ej: -33.4489): ")
        if -90 <= lat <= 90:
            break
        print("Latitud fuera de rango (-90 a 90). Inténtalo de nuevo.")

    while True:
        lng = _leer_float("Longitud (ej: -70.6693): ")
        if -180 <= lng <= 180:
            break
        print("Longitud fuera de rango (-180 a 180). Inténtalo de nuevo.")
    
    producto = _leer_producto("Producto (93 | 95 | 97 | Diesel | Kerosene): ")

    print("\nCasos de búsqueda:\n")
    print("  1) Estación más cercana")
    print("  2) Estación más cercana entre las más baratas")
    print("  3) Estación más cercana con tienda")
    print("  4) Estación más cercana con tienda entre las más baratas\n")
    opcion = _leer_opcion("Elige 1/2/3/4: ", {"1", "2", "3", "4"})

    nearest = False
    cheapest = False
    store = False

    if opcion == "1":
        nearest = True
    elif opcion == "2":
        cheapest = True
        nearest = True 
    elif opcion == "3":
        store = True
        nearest = True
    elif opcion == "4":
        store = True
        cheapest = True
        nearest = True

    try:
        res = search_station(
            lat=lat, lng=lng, product=producto,
            nearest=nearest, store=store, cheapest=cheapest,
            timeout=5
        )
        print("\n======================= Resultados =======================")
        print(json.dumps(res, ensure_ascii=False, indent=2))
        print("\n==========================================================")
    except InputValidationError as ex:
        print(json.dumps({
            "success": False,
            "data": {"error": "VALIDATION_ERROR", "message": str(ex)}
        }, ensure_ascii=False, indent=2))
    except ExternalAPIError:
        print(json.dumps({
            "success": False,
            "data": {"error": "API_ERROR", "message": "Hubo un error al conectarse con la API. Inténtelo más tarde."}
        }, ensure_ascii=False, indent=2))
    except Exception as ex:
        print(json.dumps({
            "success": False,
            "data": {"error": "UNEXPECTED_ERROR", "message": f"Error inesperado: {ex}"}
        }, ensure_ascii=False, indent=2))
    
if __name__ == "__main__":
    main()

# Prueba Técnica – Búsqueda de Estaciones de Combustible

Este proyecto implementa un script en **Python 3** que permite buscar estaciones de combustible en Chile basándose en **coordenadas geográficas (latitud/longitud)**, **tipo de combustible** y un **criterio de búsqueda**, utilizando la API pública de **Bencina en Línea (Copec)**.

---

## Requisitos

- Python 3.9 o superior  
- Librerías externas: `requests`, `geopy`

Instalar dependencias:

```bash
pip install -r requirements.txt

Uso

Ejecutar el script interactivo:

python main.py


El programa solicitará:

Latitud (ejemplo: -33.4489)

Longitud (ejemplo: -70.6693)

Producto (93 | 95 | 97 | diesel | kerosene)

Caso de búsqueda:

1 → Estación más cercana

2 → Estación más cercana entre las más baratas

3 → Estación más cercana con tienda

4 → Estación más cercana con tienda entre las más baratas

 Casos de búsqueda

Estación más cercana
Busca la estación más próxima según latitud/longitud y producto.

Estación más cercana entre las más baratas
Encuentra la estación más próxima de entre las que tengan el menor precio del producto.

Estación más cercana con tienda
Filtra solo estaciones que tengan tienda y retorna la más cercana.

Estación más cercana con tienda entre las más baratas
Combina ambos filtros: estación con tienda + menor precio.


Estructura del proyecto
.
├── combustible.py     # Módulo con la lógica (API + filtros + formateo)
├── main.py            # Script interactivo por consola
├── requirements.txt   # Dependencias del proyecto
├── .gitignore         # Archivos/carpetas ignoradas en Git
└── README.md          # Documentación

Ejemplo de salida
Éxito
{
  "success": true,
  "data": {
    "id": "10056",
    "compania": "COPEC",
    "direccion": "San Martin Esq. Uribe",
    "comuna": "Antofagasta",
    "region": "ANTOFAGASTA",
    "latitud": -23.6491868026,
    "longitud": -70.4011811037,
    "distancia_lineal": 0.5,
    "precio_producto": 1328,
    "tienda": {
      "codigo": "2510",
      "nombre": "Pronto Antofagasta",
      "tipo": "Pronto"
    },
    "tiene_tienda": true,
    "producto": "Gasolina 93"
  }
}

Error
{
  "success": false,
  "data": {
    "error": "NO_RESULTS",
    "message": "No se encontraron estaciones que cumplan los criterios."
  }
}

📖 Documentación técnica
combustible.py

map_product(product) → Normaliza el nombre del producto.

distance_km(lat1, lon1, lat2, lon2) → Calcula distancia en km (geopy).

_to_float(value) → Convierte un valor a float seguro.

_station_coords(station) → Extrae coordenadas de una estación.

data_stations(timeout) → Llama a la API Copec y retorna estaciones.

station_prices(station, product) → Obtiene el precio de un producto.

has_store(station) → Verifica si la estación tiene tienda.

build_response(...) → Formatea la salida en JSON.

search_station(...) → Función principal: implementa los 4 criterios.

main.py

Script interactivo que:

Pide datos al usuario (lat, lng, producto, caso).

Valida entradas.

Llama a search_station.

Muestra resultados en formato JSON.



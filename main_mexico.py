import os
from datetime import datetime
import pandas as pd
import requests
from dotenv import load_dotenv

# Carga variables locales de .env si existe
load_dotenv()

API_KEY = os.getenv("IQAIR_API_KEY")
PAIS = "Mexico"

# Lista de estados a monitorear (puedes agregar más estados de México)
ESTADOS = [
    "Nuevo Leon",
    "Ciudad de Mexico",
    "Jalisco",
    "Guanajuato",
    "Puebla",
    "Baja California",
    "Coahuila",
    "Chihuahua",
    "Veracruz",
    "Yucatan",
]


def obtener_ciudades_por_estado(estado):
    """Obtiene la lista de ciudades disponibles en un estado."""
    url = f"http://api.airvisual.com/v2/cities?state={estado}&country={PAIS}&key={API_KEY}"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        if data.get("status") == "success":
            return [item["city"] for item in data["data"]]
    except Exception as e:
        print(f"Error consultando ciudades de {estado}: {e}")
    return []


def obtener_datos_ciudad(ciudad, estado):
    """Consulta la calidad del aire y coordenadas de una ciudad específica."""
    url = f"http://api.airvisual.com/v2/city?city={ciudad}&state={estado}&country={PAIS}&key={API_KEY}"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()

        if data.get("status") == "success":
            info = data["data"]
            coords = info["location"]["coordinates"]  # [longitud, latitud]
            pollution = info["current"]["pollution"]
            weather = info["current"]["weather"]

            ahora = datetime.now()

            return {
                "Fecha": ahora.strftime("%Y-%m-%d"),
                "Hora": ahora.strftime("%H:%M:%S"),
                "Pais": PAIS,
                "Estado": estado,
                "Ciudad": ciudad,
                "Latitud": coords[1],
                "Longitud": coords[0],
                "AQI_US": pollution["aqius"],
                "Contaminante_Principal": pollution["mainus"],
                "Temperatura_C": weather["tp"],
                "Humedad_%": weather["hu"],
            }
        else:
            print(f"No hay datos para {ciudad}, {estado}")
    except Exception as e:
        print(f"Error al consultar {ciudad}, {estado}: {e}")

    return None


def ejecutar_monitoreo_nacional():
    if not API_KEY:
        print("Error: No se ha configurado la IQAIR_API_KEY.")
        return

    registros = []
    print("Iniciando recolección de calidad del aire en México...")

    for estado in ESTADOS:
        ciudades = obtener_ciudades_por_estado(estado)
        # Para cuidar la cuota de peticiones gratuitas, consultamos hasta 2 ciudades por estado
        for ciudad in ciudades[:2]:
            print(f"Consultando: {ciudad}, {estado}...")
            datos = obtener_datos_ciudad(ciudad, estado)
            if datos:
                registros.append(datos)

    if registros:
        guardar_en_csv(registros)


def guardar_en_csv(registros):
    filepath = "data/calidad_aire_mexico.csv"
    os.makedirs("data", exist_ok=True)

    df_nuevos = pd.DataFrame(registros)

    if os.path.exists(filepath):
        df_nuevos.to_csv(filepath, mode="a", header=False, index=False)
    else:
        df_nuevos.to_csv(filepath, mode="w", header=True, index=False)

    print(
        f"Se agregaron {len(registros)} registros exitosamente en {filepath}"
    )


if __name__ == "__main__":
    ejecutar_monitoreo_nacional()
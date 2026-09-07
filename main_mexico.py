import os
import time
from datetime import datetime
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("IQAIR_API_KEY")
PAIS = "Mexico"

# Nombres corregidos según el estándar de IQAir
ESTADOS = [
    "Nuevo Leon",
    "Jalisco",
    "Mexico City",  # Nombre correcto para CDMX en IQAir
    "Guanajuato",
    "Puebla",
    "Baja California",
    "Coahuila",
    "Chihuahua",
    "Veracruz",
    "Yucatan",
]


def obtener_ciudades_por_estado(estado):
    url = f"http://api.airvisual.com/v2/cities?state={estado}&country={PAIS}&key={API_KEY}"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        if data.get("status") == "success":
            return [item["city"] for item in data["data"]]
        else:
            msg = data.get("data", {}).get("message", "Sin detalles")
            print(f"Aviso al buscar ciudades de {estado}: {msg}")
    except Exception as e:
        print(f"Error consultando ciudades de {estado}: {e}")
    return []


def obtener_datos_ciudad(ciudad, estado):
    url = f"http://api.airvisual.com/v2/city?city={ciudad}&state={estado}&country={PAIS}&key={API_KEY}"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()

        if data.get("status") == "success":
            info = data["data"]
            coords = info["location"]["coordinates"]
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
            msg = data.get("data", {}).get("message", "Sin detalles")
            print(f"No hay datos para {ciudad}, {estado} ({msg})")
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
        print(f"\n--- Procesando Estado: {estado} ---")
        ciudades = obtener_ciudades_por_estado(estado)

        # Pausa de 3 segundos para evitar 'Too Many Requests'
        time.sleep(3)

        for ciudad in ciudades[:1]:
            print(f"Consultando: {ciudad}, {estado}...")
            datos = obtener_datos_ciudad(ciudad, estado)

            if datos:
                registros.append(datos)

            time.sleep(3)

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
        f"\n¡Éxito! Se agregaron {len(registros)} registros en {filepath}"
    )


if __name__ == "__main__":
    ejecutar_monitoreo_nacional()
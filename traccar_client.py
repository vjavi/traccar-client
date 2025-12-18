import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

# ==============================
# CONFIG
# ==============================
TRACCAR_BASE_URL = "https://TU_TRACCAR_URL"  # ej: https://demo.traccar.org
TRACCAR_USER = "TU_USUARIO"
TRACCAR_PASSWORD = "TU_PASSWORD"

# ==============================
# CLIENT
# ==============================
def get_devices():
    url = f"{TRACCAR_BASE_URL}/api/devices"
    r = requests.get(url, auth=HTTPBasicAuth(TRACCAR_USER, TRACCAR_PASSWORD))
    r.raise_for_status()
    return r.json()


def get_last_positions(device_id=None):
    url = f"{TRACCAR_BASE_URL}/api/positions"
    params = {}
    if device_id:
        params["deviceId"] = device_id

    r = requests.get(
        url,
        params=params,
        auth=HTTPBasicAuth(TRACCAR_USER, TRACCAR_PASSWORD)
    )
    r.raise_for_status()
    return r.json()


# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    print("📡 Conectando a Traccar...\n")

    devices = get_devices()
    print("🚗 Dispositivos encontrados:")
    for d in devices:
        print(f"- ID={d['id']} | Nombre={d['name']} | IMEI={d['uniqueId']}")

    if not devices:
        print("❌ No hay dispositivos asociados a este usuario")
        exit(1)

    device_id = devices[0]["id"]
    print(f"\n📍 Obteniendo última posición del dispositivo {device_id}...\n")

    positions = get_last_positions(device_id)

    if not positions:
        print("⚠️ No hay posiciones todavía")
        exit(0)

    p = positions[0]

    print("✅ Última posición:")
    print(f"  Fecha UTC : {p['fixTime']}")
    print(f"  Lat/Lon   : {p['latitude']}, {p['longitude']}")
    print(f"  Velocidad : {p['speed']} km/h")
    print(f"  Atributos :")

    for k, v in p.get("attributes", {}).items():
        print(f"    - {k}: {v}")

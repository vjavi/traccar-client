"""
Servicio de IA para chat con el vehículo usando OpenAI
"""
import os
from openai import OpenAI
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """Eres AutoAssist, un asistente experto en vehículos y análisis de datos GPS.
Tu rol es ayudar al usuario a entender los datos de su vehículo rastreado por GPS.

CAPACIDADES:
- Analizar patrones de conducción y uso del vehículo
- Detectar comportamientos anómalos (excesos de velocidad, frenados bruscos, paradas inusuales)
- Calcular estadísticas de uso (distancia, tiempo de uso)
- Interpretar eventos y alertas del vehículo
- Informar sobre el estado del vehículo (batería, voltaje, ignición)

REGLAS DE FORMATO:
- Responde SIEMPRE en español
- Sé conciso y directo
- Usa **texto** solo para datos importantes
- Si detectas algo preocupante (alarmas, excesos de velocidad), menciónalo
- Usa km y km/h para distancias y velocidades
- Fechas en formato legible: "18 de diciembre a las 14:30"

DATOS DEL VEHÍCULO:
{vehicle_context}

Analiza los datos y responde las preguntas del usuario."""


def knots_to_kmh(knots: float) -> float:
    """Convierte nudos a km/h"""
    return round(knots * 1.852, 1)


def format_datetime(iso_string: str) -> str:
    """Formatea fecha ISO a formato legible"""
    if not iso_string or iso_string == 'N/A':
        return 'N/A'
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y %H:%M')
    except:
        return iso_string


def format_duration(ms: int) -> str:
    """Formatea duración en milisegundos a formato legible"""
    if not ms:
        return "0 min"
    total_seconds = ms / 1000
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    if hours > 0:
        return f"{hours}h {minutes}min"
    return f"{minutes} min"


def format_device_for_context(device: dict) -> str:
    """Formatea la información del dispositivo"""
    if not device:
        return "No hay información del dispositivo."
    
    status = "En línea" if device.get('status') == 'online' else "Desconectado"
    last_update = format_datetime(device.get('lastUpdate', 'N/A'))
    
    lines = [
        "=== INFORMACIÓN DEL VEHÍCULO ===",
        f"Nombre: {device.get('name', 'N/A')}",
        f"IMEI: {device.get('uniqueId', 'N/A')}",
        f"Estado: {status}",
        f"Última conexión: {last_update}",
    ]
    
    if device.get('model'):
        lines.append(f"Modelo: {device.get('model')}")
    if device.get('category'):
        lines.append(f"Categoría: {device.get('category')}")
    
    return "\n".join(lines)


def calculate_obd_statistics(positions: list) -> dict:
    """
    Calcula estadísticas completas de los datos OBD del historial de posiciones.
    Retorna min, max, promedio y último valor para cada campo OBD numérico.
    """
    # Campos OBD numéricos para calcular estadísticas
    numeric_fields = {
        'io31': 'Carga del motor (%)',
        'io32': 'Temperatura refrigerante (°C)',
        'io35': 'Temperatura aire admisión (°C)',
        'io36': 'RPM del motor',
        'io37': 'Velocidad OBD (km/h)',
        'io39': 'Posición acelerador (%)',
        'io43': 'Nivel combustible (%)',
        'io48': 'Carga calculada (%)',
    }
    
    # Campos que solo necesitan el último valor
    single_fields = ['io30', 'io33', 'io38', 'io60', 'io250', 'io252', 'io389', 'vin']
    
    stats = {}
    last_values = {}
    last_times = {}
    
    # Recolectar todos los valores para cada campo
    field_values = {field: [] for field in numeric_fields}
    
    for p in positions:
        attrs = p.get('attributes', {})
        fix_time = p.get('fixTime', '')
        
        # Recolectar valores numéricos para estadísticas
        for field in numeric_fields:
            if field in attrs and attrs[field] is not None:
                value = attrs[field]
                if isinstance(value, (int, float)) and value > 0:  # Solo valores positivos válidos
                    field_values[field].append(value)
        
        # Guardar últimos valores de campos simples
        for field in single_fields:
            if field in attrs and attrs[field] is not None:
                if field not in last_values or fix_time > last_times.get(field, ''):
                    last_values[field] = attrs[field]
                    last_times[field] = fix_time
    
    # Calcular estadísticas para campos numéricos
    for field, description in numeric_fields.items():
        values = field_values[field]
        if values:
            stats[field] = {
                'description': description,
                'min': round(min(values), 1),
                'max': round(max(values), 1),
                'avg': round(sum(values) / len(values), 1),
                'last': round(values[-1], 1) if values else None,
                'count': len(values)
            }
    
    # Agregar campos simples
    for field in single_fields:
        if field in last_values:
            stats[field] = {'last': last_values[field]}
    
    return stats


def format_current_position(positions: list) -> str:
    """Formatea la posición actual con todos los atributos importantes"""
    if not positions:
        return "\n=== POSICIÓN ACTUAL ===\nNo hay datos de posición."
    
    # Tomar la posición más reciente (última del array, ordenado por tiempo)
    if isinstance(positions, list) and len(positions) > 0:
        # Ordenar por fixTime y tomar la más reciente
        sorted_positions = sorted(positions, key=lambda x: x.get('fixTime', ''), reverse=True)
        p = sorted_positions[0]
        # Calcular estadísticas OBD de todo el historial
        obd_stats = calculate_obd_statistics(positions)
    else:
        p = positions
        obd_stats = {}
    
    lines = ["\n=== POSICIÓN ACTUAL ==="]
    lines.append(f"Fecha/Hora: {format_datetime(p.get('fixTime'))}")
    lines.append(f"Coordenadas: {p.get('latitude', 'N/A')}, {p.get('longitude', 'N/A')}")
    lines.append(f"Velocidad: {knots_to_kmh(p.get('speed', 0))} km/h")
    lines.append(f"Altitud: {p.get('altitude', 0)} m")
    lines.append(f"Rumbo: {p.get('course', 0)}°")
    lines.append(f"GPS válido: {'Sí' if p.get('valid') else 'No'}")
    
    # Atributos de la posición actual
    attrs = p.get('attributes', {})
    
    lines.append("\nEstado actual del vehículo:")
    
    # Datos básicos (de la posición actual)
    if 'vin' in obd_stats and 'last' in obd_stats['vin']:
        lines.append(f"  - VIN (número de chasis): {obd_stats['vin']['last']}")
    elif 'vin' in attrs:
        lines.append(f"  - VIN (número de chasis): {attrs['vin']}")
    
    if 'ignition' in attrs:
        lines.append(f"  - Ignición: {'Encendida' if attrs['ignition'] else 'Apagada'}")
    if 'motion' in attrs:
        lines.append(f"  - En movimiento: {'Sí' if attrs['motion'] else 'No'}")
    
    # Datos eléctricos
    if 'power' in attrs:
        lines.append(f"  - Voltaje batería vehículo: {round(attrs['power'], 2)}V")
    if 'battery' in attrs:
        lines.append(f"  - Batería del GPS: {round(attrs['battery'], 2)}V")
    
    # Odómetro
    odometer_found = False
    if 'io389' in obd_stats and 'last' in obd_stats['io389'] and obd_stats['io389']['last'] > 0:
        lines.append(f"  - Odómetro del vehículo (OBD): {obd_stats['io389']['last']} km")
        odometer_found = True
    if not odometer_found and 'odometer' in attrs and attrs['odometer'] > 0:
        odometer_km = round(attrs['odometer'] / 1000, 1)
        lines.append(f"  - Odómetro configurado: {odometer_km} km")
        odometer_found = True
    if not odometer_found and 'totalDistance' in attrs:
        total_km = round(attrs['totalDistance'] / 1000, 1)
        lines.append(f"  - Distancia GPS acumulada: {total_km} km (no es el odómetro real)")
    
    # Códigos de error
    if 'io30' in obd_stats and 'last' in obd_stats['io30']:
        dtc = obd_stats['io30']['last']
        if dtc > 0:
            lines.append(f"  - ⚠️ CÓDIGOS DE ERROR (DTC): {dtc} errores detectados en el motor")
        else:
            lines.append(f"  - Códigos de error (DTC): Sin errores")
    
    # === ESTADÍSTICAS DEL MOTOR (OBD) ===
    lines.append("\n=== ESTADÍSTICAS DEL MOTOR (datos OBD del período) ===")
    
    # RPM del motor (io36)
    if 'io36' in obd_stats:
        s = obd_stats['io36']
        lines.append(f"\nRPM del motor ({s['count']} registros):")
        lines.append(f"  - Mínimo: {s['min']} RPM")
        lines.append(f"  - Máximo: {s['max']} RPM" + (" ⚠️ ALTO" if s['max'] > 5000 else ""))
        lines.append(f"  - Promedio: {s['avg']} RPM")
    
    # Carga del motor (io31)
    if 'io31' in obd_stats:
        s = obd_stats['io31']
        lines.append(f"\nCarga del motor ({s['count']} registros):")
        lines.append(f"  - Mínimo: {s['min']}%")
        lines.append(f"  - Máximo: {s['max']}%" + (" ⚠️ ALTA EXIGENCIA" if s['max'] > 80 else ""))
        lines.append(f"  - Promedio: {s['avg']}%")
    
    # Temperatura refrigerante (io32)
    if 'io32' in obd_stats:
        s = obd_stats['io32']
        temp_warning = " ⚠️ SOBRECALENTAMIENTO" if s['max'] > 100 else ""
        lines.append(f"\nTemperatura del refrigerante ({s['count']} registros):")
        lines.append(f"  - Mínimo: {s['min']}°C")
        lines.append(f"  - Máximo: {s['max']}°C{temp_warning}")
        lines.append(f"  - Promedio: {s['avg']}°C")
    
    # Temperatura aire admisión (io35)
    if 'io35' in obd_stats:
        s = obd_stats['io35']
        lines.append(f"\nTemperatura aire de admisión ({s['count']} registros):")
        lines.append(f"  - Mínimo: {s['min']}°C")
        lines.append(f"  - Máximo: {s['max']}°C")
        lines.append(f"  - Promedio: {s['avg']}°C")
    
    # Velocidad OBD (io37)
    if 'io37' in obd_stats:
        s = obd_stats['io37']
        lines.append(f"\nVelocidad del vehículo - OBD ({s['count']} registros):")
        lines.append(f"  - Mínimo: {s['min']} km/h")
        lines.append(f"  - Máximo: {s['max']} km/h")
        lines.append(f"  - Promedio: {s['avg']} km/h")
    
    # Posición acelerador (io39)
    if 'io39' in obd_stats:
        s = obd_stats['io39']
        lines.append(f"\nPosición del acelerador ({s['count']} registros):")
        lines.append(f"  - Mínimo: {s['min']}%")
        lines.append(f"  - Máximo: {s['max']}%" + (" (aceleración fuerte)" if s['max'] > 80 else ""))
        lines.append(f"  - Promedio: {s['avg']}%")
    
    # Nivel de combustible (io43)
    if 'io43' in obd_stats:
        s = obd_stats['io43']
        fuel_warning = " ⚠️ BAJO" if s['min'] < 15 else ""
        lines.append(f"\nNivel de combustible ({s['count']} registros):")
        lines.append(f"  - Mínimo: {s['min']}%{fuel_warning}")
        lines.append(f"  - Máximo: {s['max']}%")
        lines.append(f"  - Último valor: {s['last']}%")
    
    # Carga calculada (io48)
    if 'io48' in obd_stats:
        s = obd_stats['io48']
        lines.append(f"\nCarga calculada del motor ({s['count']} registros):")
        lines.append(f"  - Mínimo: {s['min']}%")
        lines.append(f"  - Máximo: {s['max']}%")
        lines.append(f"  - Promedio: {s['avg']}%")
    
    # Datos del GPS
    if 'sat' in attrs or 'hdop' in attrs:
        lines.append(f"\nDatos GPS:")
        if 'sat' in attrs:
            lines.append(f"  - Satélites conectados: {attrs['sat']}")
        if 'hdop' in attrs:
            hdop = attrs['hdop']
            precision = "Excelente" if hdop < 1 else "Buena" if hdop < 2 else "Moderada" if hdop < 5 else "Baja"
            lines.append(f"  - Precisión GPS (HDOP): {round(hdop, 1)} ({precision})")
    
    return "\n".join(lines)


def format_positions_summary(positions: list) -> str:
    """Formatea un resumen del historial de posiciones"""
    if not positions:
        return "\n=== HISTORIAL DE POSICIONES ===\nNo hay historial disponible."
    
    lines = [f"\n=== HISTORIAL DE POSICIONES ({len(positions)} registros) ==="]
    
    # Calcular estadísticas de velocidad
    speeds_kmh = [knots_to_kmh(p.get('speed', 0)) for p in positions if p.get('speed', 0) > 0]
    if speeds_kmh:
        lines.append(f"Velocidad máxima registrada: {max(speeds_kmh)} km/h")
        lines.append(f"Velocidad promedio (en movimiento): {round(sum(speeds_kmh)/len(speeds_kmh), 1)} km/h")
    
    # Mostrar últimas 5 posiciones con movimiento
    moving_positions = [p for p in positions if p.get('speed', 0) > 0][-10:]
    if moving_positions:
        lines.append("\nÚltimas posiciones con movimiento:")
        for p in moving_positions[-5:]:
            time = format_datetime(p.get('fixTime'))
            speed = knots_to_kmh(p.get('speed', 0))
            lines.append(f"  - {time}: {speed} km/h")
    
    return "\n".join(lines)


def format_events_for_context(events: list) -> str:
    """Formatea los eventos para incluir en el contexto"""
    if not events:
        return "\n=== EVENTOS ===\nNo hay eventos recientes."
    
    event_labels = {
        'deviceOnline': 'Dispositivo conectado',
        'deviceOffline': 'Dispositivo desconectado',
        'deviceMoving': 'Vehículo en movimiento',
        'deviceStopped': 'Vehículo detenido',
        'deviceOverspeed': 'EXCESO DE VELOCIDAD',
        'deviceFuelDrop': 'Caída de combustible',
        'geofenceEnter': 'Entrada a zona',
        'geofenceExit': 'Salida de zona',
        'alarm': 'ALARMA',
        'ignitionOn': 'Ignición encendida',
        'ignitionOff': 'Ignición apagada',
        'maintenance': 'Mantenimiento requerido'
    }
    
    lines = [f"\n=== EVENTOS ({len(events)} registros) ==="]
    
    # Agrupar eventos por tipo
    event_counts = {}
    alarms = []
    important_events = []
    
    for e in events:
        event_type = e.get('type', 'unknown')
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Guardar alarmas y eventos importantes
        if event_type == 'alarm':
            alarm_type = e.get('attributes', {}).get('alarm', 'desconocida')
            alarms.append({
                'time': format_datetime(e.get('eventTime')),
                'type': alarm_type
            })
        elif event_type in ['deviceOverspeed', 'ignitionOn', 'ignitionOff', 'deviceMoving']:
            important_events.append({
                'time': format_datetime(e.get('eventTime')),
                'type': event_labels.get(event_type, event_type)
            })
    
    # Resumen de eventos
    lines.append("Resumen:")
    for event_type, count in sorted(event_counts.items(), key=lambda x: x[1], reverse=True):
        label = event_labels.get(event_type, event_type)
        lines.append(f"  - {label}: {count}")
    
    # Mostrar alarmas (importantes)
    if alarms:
        lines.append("\n⚠️ ALARMAS DETECTADAS:")
        for alarm in alarms:
            alarm_desc = {
                'hardBraking': 'Frenado brusco',
                'hardAcceleration': 'Aceleración brusca',
                'hardCornering': 'Giro brusco',
                'overspeed': 'Exceso de velocidad'
            }.get(alarm['type'], alarm['type'])
            lines.append(f"  - {alarm['time']}: {alarm_desc}")
    
    # Mostrar eventos importantes recientes
    if important_events:
        lines.append("\nEventos importantes recientes:")
        for evt in important_events[-5:]:
            lines.append(f"  - {evt['time']}: {evt['type']}")
    
    return "\n".join(lines)


def format_trips_for_context(trips: list) -> str:
    """Formatea los viajes para incluir en el contexto"""
    if not trips:
        return "\n=== VIAJES ===\nNo hay viajes registrados."
    
    lines = [f"\n=== VIAJES ({len(trips)} registrados) ==="]
    
    total_distance = 0
    total_duration = 0
    max_speed_all = 0
    
    for i, trip in enumerate(trips, 1):
        start_time = format_datetime(trip.get('startTime'))
        end_time = format_datetime(trip.get('endTime'))
        distance_km = round(trip.get('distance', 0) / 1000, 2)
        duration = format_duration(trip.get('duration', 0))
        avg_speed = knots_to_kmh(trip.get('averageSpeed', 0))
        max_speed = knots_to_kmh(trip.get('maxSpeed', 0))
        
        total_distance += trip.get('distance', 0)
        total_duration += trip.get('duration', 0)
        if max_speed > max_speed_all:
            max_speed_all = max_speed
        
        lines.append(f"\nViaje {i}:")
        lines.append(f"  - Inicio: {start_time}")
        lines.append(f"  - Fin: {end_time}")
        lines.append(f"  - Distancia: {distance_km} km")
        lines.append(f"  - Duración: {duration}")
        lines.append(f"  - Velocidad promedio: {avg_speed} km/h")
        lines.append(f"  - Velocidad máxima: {max_speed} km/h")
        
        # Coordenadas inicio/fin
        if trip.get('startLat') and trip.get('endLat'):
            lines.append(f"  - Desde: {trip.get('startLat'):.4f}, {trip.get('startLon'):.4f}")
            lines.append(f"  - Hasta: {trip.get('endLat'):.4f}, {trip.get('endLon'):.4f}")
    
    # Totales
    if len(trips) > 1:
        lines.append(f"\nTOTALES:")
        lines.append(f"  - Distancia total: {round(total_distance/1000, 2)} km")
        lines.append(f"  - Tiempo total: {format_duration(total_duration)}")
        lines.append(f"  - Velocidad máxima alcanzada: {max_speed_all} km/h")
    
    return "\n".join(lines)


def build_vehicle_context(
    device: dict,
    positions: list,
    events: list,
    trips: list
) -> str:
    """Construye el contexto completo del vehículo para el prompt"""
    sections = [
        format_device_for_context(device),
        format_current_position(positions),
        format_positions_summary(positions),
        format_events_for_context(events),
        format_trips_for_context(trips)
    ]
    
    return "\n".join(sections)


async def chat_with_vehicle(
    user_message: str,
    device: dict,
    positions: list,
    events: list,
    trips: list,
    conversation_history: list = None
) -> str:
    """
    Envía un mensaje al chat de IA con el contexto del vehículo.
    """
    vehicle_context = build_vehicle_context(device, positions, events, trips)
    system_prompt = SYSTEM_PROMPT.format(vehicle_context=vehicle_context)
    
    # Debug: imprimir contexto
    print("=" * 50)
    print("CONTEXTO ENVIADO A LA IA:")
    print("=" * 50)
    print(vehicle_context)
    print("=" * 50)
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Agregar historial de conversación si existe
    if conversation_history:
        messages.extend(conversation_history)
    
    # Agregar mensaje actual del usuario
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error al comunicarse con OpenAI: {str(e)}")

"""
Backend API para el cliente Traccar
Actúa como proxy entre el frontend Vue y el servidor Traccar
"""
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import base64
import traceback

from traccar_service import TraccarService
from ai_service import chat_with_vehicle

app = FastAPI(
    title="Traccar Client API",
    description="API proxy para conectar con Traccar",
    version="1.0.0"
)

# Configurar CORS para permitir requests desde el frontend Vue
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================
# MODELOS
# ==============================
class LoginRequest(BaseModel):
    traccar_url: str
    username: str
    password: str


class HistoryRequest(BaseModel):
    device_id: int
    from_time: str  # ISO format
    to_time: str    # ISO format


class ChatMessage(BaseModel):
    role: str  # "user" o "assistant"
    content: str


class ChatRequest(BaseModel):
    device_id: int
    message: str
    hours_of_data: int = 24  # Horas de datos a incluir en el contexto
    conversation_history: List[ChatMessage] = []


# ==============================
# HELPERS
# ==============================
def get_traccar_service(authorization: str = Header(...)) -> TraccarService:
    """
    Extrae las credenciales del header Authorization y crea el servicio.
    El header debe tener formato: "Basic base64(url|username|password)"
    """
    try:
        if not authorization.startswith("Basic "):
            raise ValueError("Invalid auth format")
        
        encoded = authorization.split(" ")[1]
        decoded = base64.b64decode(encoded).decode("utf-8")
        parts = decoded.split("|")
        
        if len(parts) != 3:
            raise ValueError("Invalid credentials format")
        
        traccar_url, username, password = parts
        return TraccarService(traccar_url, username, password)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authorization: {str(e)}")


def encode_credentials(traccar_url: str, username: str, password: str) -> str:
    """Codifica las credenciales para el header Authorization"""
    credentials = f"{traccar_url}|{username}|{password}"
    encoded = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    return f"Basic {encoded}"


# ==============================
# ENDPOINTS - AUTH
# ==============================
@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """
    Valida las credenciales contra el servidor Traccar.
    Retorna un token (credenciales codificadas) si es exitoso.
    """
    try:
        service = TraccarService(request.traccar_url, request.username, request.password)
        # Intentar obtener la sesión para validar credenciales
        user_info = service.get_session()
        
        # Generar token con las credenciales
        token = encode_credentials(request.traccar_url, request.username, request.password)
        
        return {
            "success": True,
            "token": token,
            "user": {
                "id": user_info.get("id"),
                "name": user_info.get("name"),
                "email": user_info.get("email"),
                "administrator": user_info.get("administrator", False)
            }
        }
    except Exception as e:
        print(f"Login error: {traceback.format_exc()}")
        error_msg = str(e)
        if "401" in error_msg:
            error_msg = "Credenciales inválidas. Verifica tu email y contraseña."
        elif "404" in error_msg:
            error_msg = "URL de servidor Traccar inválida."
        elif "Connection" in error_msg or "timeout" in error_msg.lower():
            error_msg = "No se pudo conectar al servidor Traccar."
        raise HTTPException(status_code=401, detail=error_msg)


# ==============================
# ENDPOINTS - DEVICES
# ==============================
@app.get("/api/devices")
async def get_devices(authorization: str = Header(...)):
    """Obtiene todos los dispositivos del usuario"""
    service = get_traccar_service(authorization)
    try:
        devices = service.get_devices()
        return {"devices": devices}
    except Exception as e:
        print(f"Get devices error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/devices/{device_id}")
async def get_device(device_id: int, authorization: str = Header(...)):
    """Obtiene un dispositivo específico"""
    service = get_traccar_service(authorization)
    try:
        device = service.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
        return {"device": device}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get device error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================
# ENDPOINTS - POSITIONS
# ==============================
@app.get("/api/positions")
async def get_positions(
    device_id: Optional[int] = None,
    authorization: str = Header(...)
):
    """Obtiene las últimas posiciones"""
    service = get_traccar_service(authorization)
    try:
        positions = service.get_positions(device_id)
        return {"positions": positions}
    except Exception as e:
        print(f"Get positions error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/positions/history")
async def get_position_history(
    device_id: int,
    from_time: str,
    to_time: str,
    authorization: str = Header(...)
):
    """Obtiene el historial de posiciones de un dispositivo"""
    service = get_traccar_service(authorization)
    try:
        from_dt = datetime.fromisoformat(from_time.replace("Z", "+00:00"))
        to_dt = datetime.fromisoformat(to_time.replace("Z", "+00:00"))
        
        positions = service.get_position_history(device_id, from_dt, to_dt)
        return {"positions": positions}
    except Exception as e:
        print(f"Get position history error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/route")
async def get_route(
    device_id: int,
    from_time: str,
    to_time: str,
    authorization: str = Header(...)
):
    """Obtiene la ruta de un dispositivo (para dibujar en el mapa)"""
    service = get_traccar_service(authorization)
    try:
        from_dt = datetime.fromisoformat(from_time.replace("Z", "+00:00"))
        to_dt = datetime.fromisoformat(to_time.replace("Z", "+00:00"))
        
        route = service.get_route(device_id, from_dt, to_dt)
        return {"route": route}
    except Exception as e:
        print(f"Get route error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================
# ENDPOINTS - EVENTS
# ==============================
@app.get("/api/events")
async def get_events(
    device_id: Optional[int] = None,
    from_time: Optional[str] = None,
    to_time: Optional[str] = None,
    authorization: str = Header(...)
):
    """Obtiene eventos/alertas"""
    service = get_traccar_service(authorization)
    try:
        from_dt = None
        to_dt = None
        
        if from_time:
            from_dt = datetime.fromisoformat(from_time.replace("Z", "+00:00"))
        if to_time:
            to_dt = datetime.fromisoformat(to_time.replace("Z", "+00:00"))
        
        events = service.get_events(device_id, from_dt, to_dt)
        return {"events": events}
    except Exception as e:
        print(f"Get events error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trips")
async def get_trips(
    device_id: int,
    from_time: str,
    to_time: str,
    authorization: str = Header(...)
):
    """Obtiene los viajes de un dispositivo"""
    service = get_traccar_service(authorization)
    try:
        from_dt = datetime.fromisoformat(from_time.replace("Z", "+00:00"))
        to_dt = datetime.fromisoformat(to_time.replace("Z", "+00:00"))
        
        trips = service.get_trips(device_id, from_dt, to_dt)
        return {"trips": trips}
    except Exception as e:
        print(f"Get trips error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================
# ENDPOINTS - CHAT IA
# ==============================
@app.post("/api/chat")
async def chat(
    request: ChatRequest,
    authorization: str = Header(...)
):
    """
    Chat con IA para consultar sobre el vehículo.
    Recopila datos del dispositivo y los envía a OpenAI junto con el mensaje del usuario.
    """
    service = get_traccar_service(authorization)
    
    try:
        # Calcular rango de tiempo
        to_time = datetime.utcnow()
        from_time = to_time - timedelta(hours=request.hours_of_data)
        
        # Obtener datos del dispositivo
        device = service.get_device(request.device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
        
        # Recopilar datos en paralelo (posiciones, eventos, viajes)
        positions = []
        events = []
        trips = []
        
        # Intentar obtener posiciones del historial
        try:
            positions = service.get_position_history(request.device_id, from_time, to_time)
            print(f"Got {len(positions)} positions from history")
        except Exception as e:
            print(f"Error getting position history for chat: {e}")
            # Fallback: intentar con get_route
            try:
                positions = service.get_route(request.device_id, from_time, to_time)
                print(f"Got {len(positions)} positions from route")
            except Exception as e2:
                print(f"Error getting route for chat: {e2}")
                # Último intento: obtener posición actual
                try:
                    current_positions = service.get_positions(request.device_id)
                    if current_positions:
                        positions = current_positions
                        print(f"Got {len(positions)} current positions")
                except Exception as e3:
                    print(f"Error getting current positions: {e3}")
        
        try:
            events = service.get_events(request.device_id, from_time, to_time)
            print(f"Got {len(events)} events")
        except Exception as e:
            print(f"Error getting events for chat: {e}")
        
        try:
            trips = service.get_trips(request.device_id, from_time, to_time)
            if trips:
                print(f"Got {len(trips)} trips")
                for i, trip in enumerate(trips[:3]):  # Log primeros 3
                    print(f"  Trip {i+1}: {trip.get('startTime')} -> {trip.get('endTime')}, {trip.get('distance', 0)/1000:.1f}km")
            else:
                print(f"No trips returned (trips={trips})")
        except Exception as e:
            print(f"Error getting trips for chat: {e}")
            import traceback
            traceback.print_exc()
        
        # Convertir historial de conversación al formato esperado
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]
        
        # Enviar a la IA
        response = await chat_with_vehicle(
            user_message=request.message,
            device=device,
            positions=positions,
            events=events,
            trips=trips,
            conversation_history=conversation_history
        )
        
        return {
            "response": response,
            "data_summary": {
                "positions_count": len(positions),
                "events_count": len(events),
                "trips_count": len(trips),
                "hours_analyzed": request.hours_of_data
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Chat error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error en el chat: {str(e)}")


# ==============================
# DEBUG - Ver datos raw de un dispositivo
# ==============================
@app.get("/api/debug/device/{device_id}")
async def debug_device_data(
    device_id: int,
    hours: int = 24,
    authorization: str = Header(...)
):
    """
    Endpoint de debug para ver exactamente qué datos estamos obteniendo de Traccar.
    """
    service = get_traccar_service(authorization)
    
    to_time = datetime.utcnow()
    from_time = to_time - timedelta(hours=hours)
    
    result = {
        "device": None,
        "current_position": None,
        "position_history": None,
        "route": None,
        "events": None,
        "trips": None,
        "errors": []
    }
    
    # Obtener dispositivo
    try:
        result["device"] = service.get_device(device_id)
    except Exception as e:
        result["errors"].append(f"get_device: {str(e)}")
    
    # Obtener posición actual
    try:
        positions = service.get_positions(device_id)
        result["current_position"] = {
            "count": len(positions) if positions else 0,
            "data": positions[:5] if positions else []  # Solo las primeras 5
        }
    except Exception as e:
        result["errors"].append(f"get_positions: {str(e)}")
    
    # Obtener historial de posiciones
    try:
        history = service.get_position_history(device_id, from_time, to_time)
        result["position_history"] = {
            "count": len(history) if history else 0,
            "first_5": history[:5] if history else [],
            "last_5": history[-5:] if history and len(history) > 5 else []
        }
    except Exception as e:
        result["errors"].append(f"get_position_history: {str(e)}")
    
    # Obtener ruta
    try:
        route = service.get_route(device_id, from_time, to_time)
        result["route"] = {
            "count": len(route) if route else 0,
            "first_5": route[:5] if route else [],
            "last_5": route[-5:] if route and len(route) > 5 else []
        }
    except Exception as e:
        result["errors"].append(f"get_route: {str(e)}")
    
    # Obtener eventos
    try:
        events = service.get_events(device_id, from_time, to_time)
        result["events"] = {
            "count": len(events) if events else 0,
            "data": events[:10] if events else []  # Solo los primeros 10
        }
    except Exception as e:
        result["errors"].append(f"get_events: {str(e)}")
    
    # Obtener viajes
    try:
        trips = service.get_trips(device_id, from_time, to_time)
        result["trips"] = {
            "count": len(trips) if trips else 0,
            "data": trips
        }
    except Exception as e:
        result["errors"].append(f"get_trips: {str(e)}")
    
    return result


# ==============================
# HEALTH CHECK
# ==============================
@app.get("/api/health")
async def health_check():
    """Endpoint de salud para verificar que el servidor está corriendo"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

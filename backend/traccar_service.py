"""
Servicio para comunicación con la API de Traccar
"""
import requests
from typing import Optional
from datetime import datetime


class TraccarService:
    """Cliente para la API REST de Traccar"""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.timeout = 15
        self.session = requests.Session()
        self._authenticated = False
        self._cookies = None
    
    def _authenticate(self):
        """Autentica contra Traccar usando el endpoint de sesión"""
        if self._authenticated:
            return
        
        url = f"{self.base_url}/api/session"
        response = self.session.post(
            url,
            data={
                'email': self.username,
                'password': self.password
            },
            timeout=self.timeout
        )
        response.raise_for_status()
        self._authenticated = True
        self._cookies = response.cookies
        return response.json()
    
    def _request(self, method: str, endpoint: str, params: dict = None, json: dict = None):
        """Realiza una petición HTTP a la API de Traccar"""
        # Asegurar que estamos autenticados
        self._authenticate()
        
        url = f"{self.base_url}/api{endpoint}"
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=json,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        # Manejar respuestas vacías o no-JSON
        if not response.content:
            return None
        
        try:
            return response.json()
        except Exception:
            # Si la respuesta no es JSON válido, devolver lista vacía o None
            return []
    
    def verify_connection(self) -> dict:
        """Verifica la conexión obteniendo info del servidor"""
        return self._request("GET", "/server")
    
    def get_session(self) -> dict:
        """Obtiene la sesión actual del usuario (y autentica si es necesario)"""
        user_data = self._authenticate()
        if user_data:
            return user_data
        return self._request("GET", "/session")
    
    def get_devices(self) -> list:
        """Obtiene todos los dispositivos del usuario"""
        return self._request("GET", "/devices")
    
    def get_device(self, device_id: int) -> dict:
        """Obtiene un dispositivo específico"""
        devices = self._request("GET", "/devices", params={"id": device_id})
        return devices[0] if devices else None
    
    def get_positions(self, device_id: Optional[int] = None) -> list:
        """Obtiene las últimas posiciones (opcionalmente filtrado por dispositivo)"""
        params = {}
        if device_id:
            params["deviceId"] = device_id
        return self._request("GET", "/positions", params=params if params else None)
    
    def get_position_history(
        self, 
        device_id: int, 
        from_time: datetime, 
        to_time: datetime
    ) -> list:
        """Obtiene el historial de posiciones de un dispositivo en un rango de tiempo"""
        params = {
            "deviceId": device_id,
            "from": from_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "to": to_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        return self._request("GET", "/positions", params=params)
    
    def get_events(
        self, 
        device_id: Optional[int] = None,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None
    ) -> list:
        """Obtiene eventos/alertas (opcionalmente filtrado por dispositivo y tiempo)"""
        params = {}
        if device_id:
            params["deviceId"] = device_id
        if from_time:
            params["from"] = from_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        if to_time:
            params["to"] = to_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        return self._request("GET", "/reports/events", params=params if params else None)
    
    def get_trips(
        self,
        device_id: int,
        from_time: datetime,
        to_time: datetime
    ) -> list:
        """Obtiene los viajes de un dispositivo en un rango de tiempo"""
        params = {
            "deviceId": device_id,
            "from": from_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "to": to_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        return self._request("GET", "/reports/trips", params=params)
    
    def get_route(
        self,
        device_id: int,
        from_time: datetime,
        to_time: datetime
    ) -> list:
        """Obtiene la ruta (puntos) de un dispositivo en un rango de tiempo"""
        params = {
            "deviceId": device_id,
            "from": from_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "to": to_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        return self._request("GET", "/reports/route", params=params)

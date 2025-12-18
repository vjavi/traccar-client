import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para añadir el token de autenticación
api.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  if (authStore.token) {
    config.headers.Authorization = authStore.token
  }
  return config
})

// Interceptor para manejar errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: async (traccarUrl, username, password) => {
    const response = await api.post('/auth/login', {
      traccar_url: traccarUrl,
      username,
      password
    })
    return response.data
  }
}

export const devicesApi = {
  getAll: async () => {
    const response = await api.get('/devices')
    return response.data.devices
  },
  
  getById: async (deviceId) => {
    const response = await api.get(`/devices/${deviceId}`)
    return response.data.device
  }
}

export const positionsApi = {
  getLatest: async (deviceId = null) => {
    const params = deviceId ? { device_id: deviceId } : {}
    const response = await api.get('/positions', { params })
    return response.data.positions
  },
  
  getHistory: async (deviceId, fromTime, toTime) => {
    const response = await api.get('/positions/history', {
      params: {
        device_id: deviceId,
        from_time: fromTime,
        to_time: toTime
      }
    })
    return response.data.positions
  }
}

export const routeApi = {
  get: async (deviceId, fromTime, toTime) => {
    const response = await api.get('/route', {
      params: {
        device_id: deviceId,
        from_time: fromTime,
        to_time: toTime
      }
    })
    return response.data.route
  }
}

export const eventsApi = {
  getAll: async (deviceId = null, fromTime = null, toTime = null) => {
    const params = {}
    if (deviceId) params.device_id = deviceId
    if (fromTime) params.from_time = fromTime
    if (toTime) params.to_time = toTime
    
    const response = await api.get('/events', { params })
    return response.data.events
  }
}

export const tripsApi = {
  get: async (deviceId, fromTime, toTime) => {
    const response = await api.get('/trips', {
      params: {
        device_id: deviceId,
        from_time: fromTime,
        to_time: toTime
      }
    })
    return response.data.trips
  }
}

export const chatApi = {
  send: async (deviceId, message, hoursOfData = 24, conversationHistory = []) => {
    const response = await api.post('/chat', {
      device_id: deviceId,
      message,
      hours_of_data: hoursOfData,
      conversation_history: conversationHistory
    }, {
      timeout: 60000 // 60 segundos para el chat ya que OpenAI puede tardar
    })
    return response.data
  }
}

export default api


<template>
  <div class="h-full flex flex-col p-4">
    <!-- Device selector -->
    <div class="mb-4">
      <label class="block text-sm font-medium text-slate-300 mb-2">Dispositivo</label>
      <select
        v-model="selectedDeviceId"
        class="w-full bg-dark-200/50 border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:ring-2 focus:ring-traccar-500/50 focus:border-traccar-500 transition-all"
      >
        <option :value="null" disabled>Seleccionar dispositivo...</option>
        <option v-for="device in devices" :key="device.id" :value="device.id">
          {{ device.name }}
        </option>
      </select>
    </div>

    <!-- Date range -->
    <div class="mb-4 space-y-3">
      <div>
        <label class="block text-sm font-medium text-slate-300 mb-2">Desde</label>
        <input
          v-model="fromDate"
          type="datetime-local"
          class="w-full bg-dark-200/50 border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:ring-2 focus:ring-traccar-500/50 focus:border-traccar-500 transition-all"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-slate-300 mb-2">Hasta</label>
        <input
          v-model="toDate"
          type="datetime-local"
          class="w-full bg-dark-200/50 border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:ring-2 focus:ring-traccar-500/50 focus:border-traccar-500 transition-all"
        />
      </div>
    </div>

    <!-- Quick filters -->
    <div class="flex flex-wrap gap-2 mb-4">
      <button
        v-for="filter in quickFilters"
        :key="filter.label"
        @click="applyQuickFilter(filter)"
        class="px-3 py-1.5 bg-dark-200/50 hover:bg-traccar-500/20 border border-white/10 hover:border-traccar-500/30 rounded-lg text-xs text-slate-400 hover:text-traccar-400 transition-all"
      >
        {{ filter.label }}
      </button>
    </div>

    <!-- Search button -->
    <button
      @click="fetchHistory"
      :disabled="!selectedDeviceId || !fromDate || !toDate || loading"
      class="w-full bg-gradient-to-r from-traccar-500 to-traccar-600 hover:from-traccar-400 hover:to-traccar-500 disabled:from-slate-600 disabled:to-slate-700 text-white font-semibold py-3 px-4 rounded-xl shadow-lg transition-all flex items-center justify-center gap-2"
    >
      <svg v-if="loading" class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
      </svg>
      <span>{{ loading ? 'Cargando...' : 'Ver Recorrido' }}</span>
    </button>

    <!-- Results -->
    <div class="flex-1 mt-4 overflow-y-auto">
      <div v-if="error" class="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
        <p class="text-red-400 text-sm">{{ error }}</p>
      </div>

      <div v-else-if="routeData.length > 0" class="space-y-4">
        <!-- Stats -->
        <div class="bg-dark-200/30 rounded-xl p-4 border border-white/5">
          <h4 class="text-sm font-medium text-white mb-3">Resumen del recorrido</h4>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <p class="text-2xl font-display font-bold text-traccar-400">{{ routeData.length }}</p>
              <p class="text-xs text-slate-400">Puntos GPS</p>
            </div>
            <div>
              <p class="text-2xl font-display font-bold text-white">{{ calculateDistance() }}</p>
              <p class="text-xs text-slate-400">Distancia aprox.</p>
            </div>
            <div>
              <p class="text-2xl font-display font-bold text-white">{{ maxSpeed }} km/h</p>
              <p class="text-xs text-slate-400">Velocidad máx.</p>
            </div>
            <div>
              <p class="text-2xl font-display font-bold text-white">{{ avgSpeed }} km/h</p>
              <p class="text-xs text-slate-400">Velocidad prom.</p>
            </div>
          </div>
        </div>

        <!-- Trips if available -->
        <div v-if="trips.length > 0" class="space-y-2">
          <h4 class="text-sm font-medium text-white">Viajes detectados</h4>
          <div
            v-for="(trip, index) in trips"
            :key="index"
            class="bg-dark-200/30 rounded-xl p-3 border border-white/5"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-white">Viaje {{ index + 1 }}</span>
              <span class="text-xs text-slate-400">{{ formatDuration(trip.duration) }}</span>
            </div>
            <div class="text-xs text-slate-400 space-y-1">
              <p>Distancia: {{ (trip.distance / 1000).toFixed(2) }} km</p>
              <p>Vel. máx: {{ Math.round(trip.maxSpeed * 1.852) }} km/h</p>
              <p>Vel. prom: {{ Math.round(trip.averageSpeed * 1.852) }} km/h</p>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="!loading && searched" class="text-center py-8">
        <svg class="w-12 h-12 text-slate-600 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path>
        </svg>
        <p class="text-slate-500 text-sm">No se encontraron datos para el período seleccionado</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { positionsApi, tripsApi } from '../services/api'

const props = defineProps({
  selectedDevice: {
    type: Number,
    default: null
  },
  devices: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['show-route'])

const selectedDeviceId = ref(props.selectedDevice)
const fromDate = ref('')
const toDate = ref('')
const loading = ref(false)
const error = ref('')
const routeData = ref([])
const trips = ref([])
const searched = ref(false)

const quickFilters = [
  { label: 'Última hora', hours: 1 },
  { label: 'Últimas 4h', hours: 4 },
  { label: 'Hoy', hours: 24 },
  { label: 'Ayer', hours: 48, offset: 24 },
  { label: 'Última semana', hours: 168 }
]

const maxSpeed = computed(() => {
  if (routeData.value.length === 0) return 0
  const max = Math.max(...routeData.value.map(p => p.speed || 0))
  return Math.round(max * 1.852) // knots to km/h
})

const avgSpeed = computed(() => {
  if (routeData.value.length === 0) return 0
  const sum = routeData.value.reduce((acc, p) => acc + (p.speed || 0), 0)
  return Math.round((sum / routeData.value.length) * 1.852)
})

watch(() => props.selectedDevice, (newVal) => {
  if (newVal) selectedDeviceId.value = newVal
})

function applyQuickFilter(filter) {
  const now = new Date()
  const to = new Date(now)
  const from = new Date(now)
  
  if (filter.offset) {
    to.setHours(to.getHours() - filter.offset)
    from.setHours(from.getHours() - filter.hours)
  } else {
    from.setHours(from.getHours() - filter.hours)
  }
  
  fromDate.value = formatDatetimeLocal(from)
  toDate.value = formatDatetimeLocal(to)
}

function formatDatetimeLocal(date) {
  const pad = (n) => n.toString().padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

function formatDuration(ms) {
  const minutes = Math.floor(ms / 60000)
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  
  if (hours > 0) return `${hours}h ${mins}m`
  return `${mins}m`
}

function calculateDistance() {
  if (routeData.value.length < 2) return '0 km'
  
  let distance = 0
  for (let i = 1; i < routeData.value.length; i++) {
    const prev = routeData.value[i - 1]
    const curr = routeData.value[i]
    distance += haversine(prev.latitude, prev.longitude, curr.latitude, curr.longitude)
  }
  
  if (distance < 1) return `${Math.round(distance * 1000)} m`
  return `${distance.toFixed(2)} km`
}

function haversine(lat1, lon1, lat2, lon2) {
  const R = 6371 // km
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a = Math.sin(dLat / 2) ** 2 +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

async function fetchHistory() {
  if (!selectedDeviceId.value || !fromDate.value || !toDate.value) return
  
  loading.value = true
  error.value = ''
  searched.value = true
  
  try {
    const from = new Date(fromDate.value).toISOString()
    const to = new Date(toDate.value).toISOString()
    
    // Fetch positions history and trips in parallel
    const [positions, tripsData] = await Promise.all([
      positionsApi.getHistory(selectedDeviceId.value, from, to),
      tripsApi.get(selectedDeviceId.value, from, to).catch(() => [])
    ])
    
    routeData.value = positions || []
    trips.value = tripsData || []
    
    // Emit route to map
    if (positions && positions.length > 0) {
      emit('show-route', positions)
    }
  } catch (err) {
    console.error('Error fetching history:', err)
    const errorMsg = err.response?.data?.detail || err.message || 'Error al obtener el historial'
    error.value = errorMsg.includes('Expecting value') 
      ? 'No hay datos disponibles para el período seleccionado' 
      : errorMsg
    routeData.value = []
    trips.value = []
  } finally {
    loading.value = false
  }
}

// Initialize with last hour
applyQuickFilter(quickFilters[0])
</script>


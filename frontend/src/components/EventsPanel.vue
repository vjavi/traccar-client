<template>
  <div class="h-full flex flex-col p-4">
    <!-- Device selector -->
    <div class="mb-4">
      <label class="block text-sm font-medium text-slate-300 mb-2">Dispositivo</label>
      <select
        v-model="selectedDeviceId"
        class="w-full bg-dark-200/50 border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:ring-2 focus:ring-traccar-500/50 focus:border-traccar-500 transition-all"
      >
        <option :value="null">Todos los dispositivos</option>
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

    <!-- Search button -->
    <button
      @click="fetchEvents"
      :disabled="!fromDate || !toDate || loading"
      class="w-full bg-gradient-to-r from-traccar-500 to-traccar-600 hover:from-traccar-400 hover:to-traccar-500 disabled:from-slate-600 disabled:to-slate-700 text-white font-semibold py-3 px-4 rounded-xl shadow-lg transition-all flex items-center justify-center gap-2"
    >
      <svg v-if="loading" class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
      </svg>
      <span>{{ loading ? 'Cargando...' : 'Buscar Eventos' }}</span>
    </button>

    <!-- Events list -->
    <div class="flex-1 mt-4 overflow-y-auto">
      <div v-if="error" class="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
        <p class="text-red-400 text-sm">{{ error }}</p>
      </div>

      <div v-else-if="events.length > 0" class="space-y-2">
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm font-medium text-white">{{ events.length }} eventos encontrados</span>
        </div>
        
        <div
          v-for="(event, index) in events"
          :key="index"
          class="bg-dark-200/30 rounded-xl p-4 border border-white/5 animate-fade-in"
          :style="{ animationDelay: `${index * 30}ms`, opacity: 0 }"
        >
          <div class="flex items-start gap-3">
            <!-- Event icon -->
            <div :class="['w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0', getEventClass(event.type)]">
              <component :is="getEventIcon(event.type)" class="w-5 h-5" />
            </div>
            
            <!-- Event info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between gap-2 mb-1">
                <h4 class="font-medium text-white text-sm truncate">{{ getEventLabel(event.type) }}</h4>
                <span class="text-xs text-slate-500 whitespace-nowrap">{{ formatTime(event.eventTime) }}</span>
              </div>
              <p v-if="getDeviceName(event.deviceId)" class="text-xs text-slate-400 mb-1">
                {{ getDeviceName(event.deviceId) }}
              </p>
              <p v-if="event.attributes" class="text-xs text-slate-500">
                {{ formatAttributes(event.attributes) }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="!loading && searched" class="text-center py-8">
        <svg class="w-12 h-12 text-slate-600 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
        </svg>
        <p class="text-slate-500 text-sm">No se encontraron eventos para el período seleccionado</p>
      </div>

      <div v-else-if="!searched" class="text-center py-8">
        <svg class="w-12 h-12 text-slate-600 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
        </svg>
        <p class="text-slate-500 text-sm">Selecciona un rango de fechas para buscar eventos</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, h } from 'vue'
import { eventsApi } from '../services/api'

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

const selectedDeviceId = ref(props.selectedDevice)
const fromDate = ref('')
const toDate = ref('')
const loading = ref(false)
const error = ref('')
const events = ref([])
const searched = ref(false)

// Event type mappings
const eventLabels = {
  deviceOnline: 'Dispositivo en línea',
  deviceOffline: 'Dispositivo desconectado',
  deviceMoving: 'Dispositivo en movimiento',
  deviceStopped: 'Dispositivo detenido',
  deviceOverspeed: 'Exceso de velocidad',
  deviceFuelDrop: 'Caída de combustible',
  commandResult: 'Resultado de comando',
  geofenceEnter: 'Entrada a geocerca',
  geofenceExit: 'Salida de geocerca',
  alarm: 'Alarma',
  ignitionOn: 'Ignición encendida',
  ignitionOff: 'Ignición apagada',
  maintenance: 'Mantenimiento',
  textMessage: 'Mensaje de texto',
  driverChanged: 'Cambio de conductor'
}

const eventClasses = {
  deviceOnline: 'bg-traccar-500/20 text-traccar-400',
  deviceOffline: 'bg-slate-500/20 text-slate-400',
  deviceMoving: 'bg-blue-500/20 text-blue-400',
  deviceStopped: 'bg-yellow-500/20 text-yellow-400',
  deviceOverspeed: 'bg-red-500/20 text-red-400',
  alarm: 'bg-red-500/20 text-red-400',
  geofenceEnter: 'bg-purple-500/20 text-purple-400',
  geofenceExit: 'bg-orange-500/20 text-orange-400',
  ignitionOn: 'bg-traccar-500/20 text-traccar-400',
  ignitionOff: 'bg-slate-500/20 text-slate-400'
}

watch(() => props.selectedDevice, (newVal) => {
  selectedDeviceId.value = newVal
})

// Initialize with last 24 hours
const now = new Date()
const yesterday = new Date(now)
yesterday.setDate(yesterday.getDate() - 1)
fromDate.value = formatDatetimeLocal(yesterday)
toDate.value = formatDatetimeLocal(now)

function formatDatetimeLocal(date) {
  const pad = (n) => n.toString().padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

function getEventLabel(type) {
  return eventLabels[type] || type
}

function getEventClass(type) {
  return eventClasses[type] || 'bg-slate-500/20 text-slate-400'
}

function getEventIcon(type) {
  // Return SVG components based on event type
  const icons = {
    deviceOnline: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M5.636 18.364a9 9 0 010-12.728m12.728 0a9 9 0 010 12.728m-9.9-2.829a5 5 0 010-7.07m7.072 0a5 5 0 010 7.07M13 12a1 1 0 11-2 0 1 1 0 012 0z' })
    ]),
    deviceOffline: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M18.364 5.636a9 9 0 010 12.728m0 0l-12.728-12.728m12.728 12.728L5.636 5.636m12.728 12.728A9 9 0 115.636 5.636' })
    ]),
    deviceOverspeed: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M13 10V3L4 14h7v7l9-11h-7z' })
    ]),
    alarm: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' })
    ])
  }
  
  return icons[type] || icons.deviceOnline
}

function getDeviceName(deviceId) {
  const device = props.devices.find(d => d.id === deviceId)
  return device?.name || ''
}

function formatTime(isoString) {
  const date = new Date(isoString)
  return date.toLocaleString('es-ES', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatAttributes(attrs) {
  if (!attrs || Object.keys(attrs).length === 0) return ''
  return Object.entries(attrs)
    .slice(0, 3)
    .map(([key, value]) => `${key}: ${value}`)
    .join(' | ')
}

async function fetchEvents() {
  if (!fromDate.value || !toDate.value) return
  
  loading.value = true
  error.value = ''
  searched.value = true
  
  try {
    const from = new Date(fromDate.value).toISOString()
    const to = new Date(toDate.value).toISOString()
    
    events.value = await eventsApi.getAll(selectedDeviceId.value, from, to)
  } catch (err) {
    console.error('Error fetching events:', err)
    error.value = err.response?.data?.detail || 'Error al obtener los eventos'
    events.value = []
  } finally {
    loading.value = false
  }
}
</script>


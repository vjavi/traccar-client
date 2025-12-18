<template>
  <div class="h-full flex flex-col">
    <!-- Search -->
    <div class="p-4">
      <div class="relative">
        <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar dispositivo..."
          class="w-full bg-dark-200/50 border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-white text-sm placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-traccar-500/50 focus:border-traccar-500 transition-all"
        />
      </div>
    </div>

    <!-- Stats -->
    <div class="px-4 pb-4 flex gap-3">
      <div class="flex-1 bg-traccar-500/10 rounded-xl p-3 border border-traccar-500/20">
        <p class="text-2xl font-display font-bold text-traccar-400">{{ onlineCount }}</p>
        <p class="text-xs text-slate-400">En línea</p>
      </div>
      <div class="flex-1 bg-slate-500/10 rounded-xl p-3 border border-slate-500/20">
        <p class="text-2xl font-display font-bold text-slate-400">{{ offlineCount }}</p>
        <p class="text-xs text-slate-400">Desconectados</p>
      </div>
    </div>

    <!-- Device list -->
    <div class="flex-1 overflow-y-auto px-4 pb-4 space-y-2">
      <div v-if="loading" class="flex items-center justify-center py-8">
        <svg class="w-8 h-8 text-traccar-400 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
        </svg>
      </div>
      
      <div v-else-if="filteredDevices.length === 0" class="text-center py-8">
        <svg class="w-12 h-12 text-slate-600 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path>
        </svg>
        <p class="text-slate-500 text-sm">No se encontraron dispositivos</p>
      </div>

      <button
        v-for="(device, index) in filteredDevices"
        :key="device.id"
        @click="$emit('select', device.id)"
        :class="[
          'w-full text-left p-4 rounded-xl border transition-all duration-200 animate-fade-in',
          selectedDevice === device.id 
            ? 'bg-traccar-500/10 border-traccar-500/30' 
            : 'bg-dark-200/30 border-white/5 hover:bg-dark-200/50 hover:border-white/10'
        ]"
        :style="{ animationDelay: `${index * 50}ms`, opacity: 0 }"
      >
        <div class="flex items-start gap-3">
          <!-- Status indicator -->
          <div class="mt-1">
            <div :class="[
              'w-3 h-3 rounded-full',
              device.status === 'online' ? 'bg-traccar-400 shadow-lg shadow-traccar-400/50' : 'bg-slate-500'
            ]"></div>
          </div>
          
          <!-- Device info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between gap-2 mb-1">
              <h3 class="font-medium text-white truncate">{{ device.name }}</h3>
              <span v-if="getDevicePosition(device.id)" class="text-xs text-slate-400">
                {{ Math.round(getDevicePosition(device.id).speed * 1.852) }} km/h
              </span>
            </div>
            <p class="text-xs text-slate-500 mb-2">IMEI: {{ device.uniqueId }}</p>
            
            <!-- Position info -->
            <div v-if="getDevicePosition(device.id)" class="flex items-center gap-4 text-xs text-slate-400">
              <span class="flex items-center gap-1">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                </svg>
                {{ getDevicePosition(device.id).latitude.toFixed(4) }}, {{ getDevicePosition(device.id).longitude.toFixed(4) }}
              </span>
            </div>
            <p v-if="device.lastUpdate" class="text-xs text-slate-500 mt-2">
              Última act: {{ formatTime(device.lastUpdate) }}
            </p>
          </div>

          <!-- Arrow -->
          <svg class="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  devices: {
    type: Array,
    default: () => []
  },
  positions: {
    type: Array,
    default: () => []
  },
  selectedDevice: {
    type: Number,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['select'])

const searchQuery = ref('')

const filteredDevices = computed(() => {
  if (!searchQuery.value) return props.devices
  const query = searchQuery.value.toLowerCase()
  return props.devices.filter(d => 
    d.name.toLowerCase().includes(query) ||
    d.uniqueId.toLowerCase().includes(query)
  )
})

const onlineCount = computed(() => props.devices.filter(d => d.status === 'online').length)
const offlineCount = computed(() => props.devices.filter(d => d.status !== 'online').length)

function getDevicePosition(deviceId) {
  return props.positions.find(p => p.deviceId === deviceId)
}

function formatTime(isoString) {
  const date = new Date(isoString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 1) return 'Ahora'
  if (diffMins < 60) return `Hace ${diffMins} min`
  if (diffMins < 1440) return `Hace ${Math.floor(diffMins / 60)} h`
  return date.toLocaleDateString('es-ES', { day: '2-digit', month: 'short' })
}
</script>


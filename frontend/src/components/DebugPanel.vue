<template>
  <div class="h-full flex flex-col p-4 overflow-hidden">
    <div class="mb-4 space-y-3">
      <h3 class="text-white font-semibold text-sm">Debug - Datos Raw</h3>
      
      <!-- Dispositivo -->
      <select
        v-model="selectedDeviceId"
        class="w-full bg-dark-200/50 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
      >
        <option :value="null" disabled>Seleccionar dispositivo...</option>
        <option v-for="device in devices" :key="device.id" :value="device.id">
          {{ device.name }} (ID: {{ device.id }})
        </option>
      </select>
      
      <!-- Rango y botón -->
      <div class="flex gap-2">
        <select
          v-model="hours"
          class="flex-1 bg-dark-200/50 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
        >
          <option :value="1">1h</option>
          <option :value="6">6h</option>
          <option :value="24">24h</option>
          <option :value="48">48h</option>
          <option :value="168">7 días</option>
        </select>
        
        <button
          @click="fetchDebugData"
          :disabled="!selectedDeviceId || loading"
          class="px-4 py-2 bg-yellow-500 hover:bg-yellow-400 disabled:bg-slate-600 text-black font-medium rounded-lg transition-all whitespace-nowrap"
        >
          {{ loading ? '...' : 'Ejecutar' }}
        </button>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto">
      <div v-if="error" class="bg-red-500/10 border border-red-500/30 rounded-lg p-3 mb-4">
        <p class="text-red-400 text-sm">{{ error }}</p>
      </div>

      <div v-if="debugData" class="space-y-4">
        <!-- Errores -->
        <div v-if="debugData.errors?.length" class="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
          <h4 class="text-red-400 font-medium text-sm mb-2">Errores:</h4>
          <ul class="text-red-300 text-xs space-y-1">
            <li v-for="err in debugData.errors" :key="err">• {{ err }}</li>
          </ul>
        </div>

        <!-- Device -->
        <div class="bg-dark-200/50 border border-white/10 rounded-lg p-3">
          <h4 class="text-traccar-400 font-medium text-sm mb-2">📱 Device</h4>
          <pre class="text-xs text-slate-300 overflow-x-auto">{{ JSON.stringify(debugData.device, null, 2) }}</pre>
        </div>

        <!-- Current Position -->
        <div class="bg-dark-200/50 border border-white/10 rounded-lg p-3">
          <h4 class="text-traccar-400 font-medium text-sm mb-2">📍 Posición Actual ({{ debugData.current_position?.count || 0 }})</h4>
          <pre class="text-xs text-slate-300 overflow-x-auto">{{ JSON.stringify(debugData.current_position?.data, null, 2) }}</pre>
        </div>

        <!-- Position History -->
        <div class="bg-dark-200/50 border border-white/10 rounded-lg p-3">
          <h4 class="text-traccar-400 font-medium text-sm mb-2">📊 Historial Posiciones ({{ debugData.position_history?.count || 0 }})</h4>
          <div v-if="debugData.position_history?.count > 0">
            <p class="text-xs text-slate-400 mb-2">Primeras 5:</p>
            <pre class="text-xs text-slate-300 overflow-x-auto mb-2">{{ JSON.stringify(debugData.position_history?.first_5, null, 2) }}</pre>
            <p class="text-xs text-slate-400 mb-2">Últimas 5:</p>
            <pre class="text-xs text-slate-300 overflow-x-auto">{{ JSON.stringify(debugData.position_history?.last_5, null, 2) }}</pre>
          </div>
          <p v-else class="text-xs text-slate-500">Sin datos</p>
        </div>

        <!-- Route -->
        <div class="bg-dark-200/50 border border-white/10 rounded-lg p-3">
          <h4 class="text-traccar-400 font-medium text-sm mb-2">🛣️ Route ({{ debugData.route?.count || 0 }})</h4>
          <div v-if="debugData.route?.count > 0">
            <p class="text-xs text-slate-400 mb-2">Primeras 5:</p>
            <pre class="text-xs text-slate-300 overflow-x-auto">{{ JSON.stringify(debugData.route?.first_5, null, 2) }}</pre>
          </div>
          <p v-else class="text-xs text-slate-500">Sin datos</p>
        </div>

        <!-- Events -->
        <div class="bg-dark-200/50 border border-white/10 rounded-lg p-3">
          <h4 class="text-traccar-400 font-medium text-sm mb-2">⚡ Eventos ({{ debugData.events?.count || 0 }})</h4>
          <pre class="text-xs text-slate-300 overflow-x-auto">{{ JSON.stringify(debugData.events?.data, null, 2) }}</pre>
        </div>

        <!-- Trips -->
        <div class="bg-dark-200/50 border border-white/10 rounded-lg p-3">
          <h4 class="text-traccar-400 font-medium text-sm mb-2">🚗 Viajes ({{ debugData.trips?.count || 0 }})</h4>
          <pre class="text-xs text-slate-300 overflow-x-auto">{{ JSON.stringify(debugData.trips?.data, null, 2) }}</pre>
        </div>
      </div>

      <div v-else-if="!loading" class="text-center py-8">
        <p class="text-slate-500 text-sm">Selecciona un dispositivo y haz click en Debug</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import api from '../services/api'

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
const hours = ref(24)
const loading = ref(false)
const error = ref('')
const debugData = ref(null)

watch(() => props.selectedDevice, (newVal) => {
  if (newVal) selectedDeviceId.value = newVal
})

async function fetchDebugData() {
  if (!selectedDeviceId.value) return
  
  loading.value = true
  error.value = ''
  debugData.value = null
  
  try {
    const response = await api.get(`/debug/device/${selectedDeviceId.value}`, {
      params: { hours: hours.value }
    })
    debugData.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || err.message
  } finally {
    loading.value = false
  }
}
</script>


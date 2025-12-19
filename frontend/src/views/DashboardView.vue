<template>
  <div class="h-screen flex flex-col bg-dark-200">
    <!-- Header - Responsive -->
    <header class="bg-dark-100/90 backdrop-blur-lg border-b border-white/10 px-3 md:px-6 py-3 md:py-4 flex items-center justify-between z-50">
      <div class="flex items-center gap-2 md:gap-4">
        <div class="flex items-center gap-2 md:gap-3">
          <div class="w-8 h-8 md:w-10 md:h-10 bg-gradient-to-br from-traccar-400 to-traccar-600 rounded-lg md:rounded-xl flex items-center justify-center shadow-lg shadow-traccar-500/20">
            <svg class="w-4 h-4 md:w-5 md:h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
          </div>
          <div>
            <h1 class="text-sm md:text-lg font-display font-bold text-white">Traccar Client</h1>
            <p class="text-[10px] md:text-xs text-slate-400 truncate max-w-[120px] md:max-w-none">{{ authStore.traccarUrl }}</p>
          </div>
        </div>
      </div>
      
      <div class="flex items-center gap-2 md:gap-4">
        <!-- Refresh button -->
        <button 
          @click="refreshData" 
          :disabled="loading"
          class="p-2 md:p-2.5 bg-dark-200/50 hover:bg-dark-200 rounded-lg md:rounded-xl text-slate-400 hover:text-white transition-all"
          title="Actualizar datos"
        >
          <svg :class="['w-4 h-4 md:w-5 md:h-5', loading && 'animate-spin']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
        </button>
        
        <!-- User menu - Hidden on mobile, shown on md+ -->
        <div class="hidden md:flex items-center gap-3 pl-4 border-l border-white/10">
          <div class="text-right">
            <p class="text-sm font-medium text-white">{{ authStore.user?.name || authStore.user?.email }}</p>
            <p class="text-xs text-slate-400">{{ authStore.user?.administrator ? 'Administrador' : 'Usuario' }}</p>
          </div>
          <button 
            @click="handleLogout"
            class="p-2.5 bg-red-500/10 hover:bg-red-500/20 rounded-xl text-red-400 hover:text-red-300 transition-all"
            title="Cerrar sesión"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
            </svg>
          </button>
        </div>
        
        <!-- Mobile logout button -->
        <button 
          @click="handleLogout"
          class="md:hidden p-2 bg-red-500/10 hover:bg-red-500/20 rounded-lg text-red-400 hover:text-red-300 transition-all"
          title="Cerrar sesión"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
          </svg>
        </button>
      </div>
    </header>

    <!-- Main content -->
    <div class="flex-1 flex overflow-hidden relative">
      <!-- Sidebar - Desktop only -->
      <aside class="hidden md:flex w-80 bg-dark-100/50 backdrop-blur-lg border-r border-white/10 flex-col">
        <!-- Tabs -->
        <div class="flex border-b border-white/10 overflow-x-auto">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            @click="activeTab = tab.id"
            :title="tab.label"
            :class="[
              'flex-1 min-w-0 px-2 py-3 text-xs font-medium transition-all flex flex-col items-center justify-center gap-0.5',
              activeTab === tab.id 
                ? tab.id === 'chat' 
                  ? 'text-purple-400 border-b-2 border-purple-400 bg-purple-500/5'
                  : tab.id === 'debug'
                    ? 'text-yellow-400 border-b-2 border-yellow-400 bg-yellow-500/5'
                    : 'text-traccar-400 border-b-2 border-traccar-400 bg-traccar-500/5' 
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            ]"
          >
            <component :is="tab.icon" class="w-4 h-4" />
            <span class="text-[10px] truncate max-w-full">{{ tab.label }}</span>
          </button>
        </div>

        <!-- Tab content -->
        <div class="flex-1 overflow-hidden">
          <DeviceList 
            v-if="activeTab === 'devices'"
            :devices="devices"
            :positions="positions"
            :selected-device="selectedDevice"
            :loading="loading"
            @select="selectDevice"
          />
          <HistoryPanel 
            v-else-if="activeTab === 'history'"
            :selected-device="selectedDevice"
            :devices="devices"
            @show-route="showRoute"
          />
          <EventsPanel 
            v-else-if="activeTab === 'events'"
            :selected-device="selectedDevice"
            :devices="devices"
          />
          <ChatPanel
            v-else-if="activeTab === 'chat'"
            :selected-device="selectedDevice"
            :devices="devices"
          />
          <DebugPanel
            v-else-if="activeTab === 'debug'"
            :selected-device="selectedDevice"
            :devices="devices"
          />
        </div>
      </aside>

      <!-- Map -->
      <main class="flex-1 relative">
        <MapView 
          :devices="devices"
          :positions="positions"
          :selected-device="selectedDevice"
          :route-points="routePoints"
          @select-device="selectDevice"
        />
        
        <!-- Device info overlay - Responsive -->
        <div 
          v-if="selectedDeviceInfo && !mobilePanel"
          :class="[
            'absolute bg-dark-100/95 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl animate-slide-in overflow-hidden',
            'top-4 right-4 w-72 md:w-80',
            'md:block'
          ]"
        >
          <div class="p-3 md:p-4 border-b border-white/10 flex items-center justify-between">
            <h3 class="font-display font-semibold text-white text-sm md:text-base">{{ selectedDeviceInfo.device.name }}</h3>
            <button @click="selectedDevice = null" class="p-1 hover:bg-white/10 rounded-lg transition-colors">
              <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          <div class="p-3 md:p-4 space-y-2 md:space-y-3">
            <div class="flex items-center gap-3">
              <div :class="['w-3 h-3 rounded-full', selectedDeviceInfo.device.status === 'online' ? 'bg-traccar-400' : 'bg-slate-500']"></div>
              <span class="text-sm text-slate-300">{{ selectedDeviceInfo.device.status === 'online' ? 'En línea' : 'Desconectado' }}</span>
            </div>
            <div v-if="selectedDeviceInfo.position" class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-slate-400">Velocidad</span>
                <span class="text-white font-medium">{{ Math.round(selectedDeviceInfo.position.speed * 1.852) }} km/h</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-400">Coordenadas</span>
                <span class="text-white font-mono text-xs">{{ selectedDeviceInfo.position.latitude.toFixed(5) }}, {{ selectedDeviceInfo.position.longitude.toFixed(5) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-400">Última actualización</span>
                <span class="text-white">{{ formatTime(selectedDeviceInfo.position.fixTime) }}</span>
              </div>
            </div>
          </div>
        </div>
      </main>
      
      <!-- Mobile Panel Overlay -->
      <Transition name="slide-up">
        <div 
          v-if="mobilePanel"
          class="md:hidden absolute inset-x-0 bottom-0 top-0 bg-dark-100 flex flex-col pb-16"
          style="z-index: 1000;"
        >
          <div class="flex items-center justify-between px-4 py-3 border-b border-white/10 shrink-0">
            <h2 class="font-display font-semibold text-white">
              {{ mobileTabs.find(t => t.id === activeTab)?.label || tabs.find(t => t.id === activeTab)?.label }}
            </h2>
            <button 
              @click="mobilePanel = false; activeTab = 'map'"
              class="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          <div class="flex-1 overflow-hidden min-h-0">
            <DeviceList 
              v-if="activeTab === 'devices'"
              :devices="devices"
              :positions="positions"
              :selected-device="selectedDevice"
              :loading="loading"
              @select="handleMobileDeviceSelect"
            />
            <HistoryPanel 
              v-else-if="activeTab === 'history'"
              :selected-device="selectedDevice"
              :devices="devices"
              @show-route="handleMobileShowRoute"
            />
            <EventsPanel 
              v-else-if="activeTab === 'events'"
              :selected-device="selectedDevice"
              :devices="devices"
            />
            <ChatPanel
              v-else-if="activeTab === 'chat'"
              :selected-device="selectedDevice"
              :devices="devices"
            />
            <DebugPanel
              v-else-if="activeTab === 'debug'"
              :selected-device="selectedDevice"
              :devices="devices"
            />
          </div>
        </div>
      </Transition>
    </div>
    
    <!-- Mobile Bottom Navigation -->
    <nav class="md:hidden bg-dark-100 border-t border-white/10 px-2 py-1 safe-area-bottom relative" style="z-index: 1001;">
      <div class="flex justify-around">
        <button 
          v-for="tab in mobileTabs" 
          :key="tab.id"
          @click="handleMobileTabClick(tab.id)"
          :class="[
            'flex-1 flex flex-col items-center justify-center py-2 px-1 rounded-xl transition-all',
            (tab.id === 'map' && !mobilePanel) || (tab.id === activeTab && mobilePanel)
              ? tab.id === 'chat' 
                ? 'text-purple-400 bg-purple-500/10'
                : 'text-traccar-400 bg-traccar-500/10'
              : 'text-slate-400 active:bg-white/5'
          ]"
        >
          <component :is="tab.icon" class="w-5 h-5" />
          <span class="text-[10px] mt-0.5 font-medium">{{ tab.label }}</span>
        </button>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { devicesApi, positionsApi } from '../services/api'
import DeviceList from '../components/DeviceList.vue'
import MapView from '../components/MapView.vue'
import HistoryPanel from '../components/HistoryPanel.vue'
import EventsPanel from '../components/EventsPanel.vue'
import ChatPanel from '../components/ChatPanel.vue'
import DebugPanel from '../components/DebugPanel.vue'

const router = useRouter()
const authStore = useAuthStore()

// Icon components
const DevicesIcon = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z' })
])

const HistoryIcon = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' })
])

const EventsIcon = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9' })
])

const ChatIcon = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z' })
])

const DebugIcon = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4' })
])

const MapIcon = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7' })
])

const tabs = [
  { id: 'devices', label: 'Dispositivos', icon: DevicesIcon },
  { id: 'history', label: 'Historial', icon: HistoryIcon },
  { id: 'events', label: 'Eventos', icon: EventsIcon },
  { id: 'chat', label: 'Chat IA', icon: ChatIcon },
  { id: 'debug', label: 'Debug', icon: DebugIcon }
]

// Mobile tabs (simplified for bottom nav)
const mobileTabs = [
  { id: 'map', label: 'Mapa', icon: MapIcon },
  { id: 'devices', label: 'Vehículos', icon: DevicesIcon },
  { id: 'history', label: 'Historial', icon: HistoryIcon },
  { id: 'events', label: 'Alertas', icon: EventsIcon },
  { id: 'chat', label: 'Chat', icon: ChatIcon }
]

const activeTab = ref('devices')
const mobilePanel = ref(false)
const devices = ref([])
const positions = ref([])
const selectedDevice = ref(null)
const routePoints = ref([])
const loading = ref(false)
let refreshInterval = null

// Mobile handlers
function handleMobileTabClick(tabId) {
  if (tabId === 'map') {
    mobilePanel.value = false
    activeTab.value = 'map'
  } else {
    activeTab.value = tabId
    mobilePanel.value = true
  }
}

function handleMobileDeviceSelect(deviceId) {
  selectedDevice.value = deviceId
  routePoints.value = []
  // Go back to map view after selecting
  mobilePanel.value = false
  activeTab.value = 'map'
}

function handleMobileShowRoute(points) {
  routePoints.value = points
  // Go back to map view to see the route
  mobilePanel.value = false
  activeTab.value = 'map'
}

const selectedDeviceInfo = computed(() => {
  if (!selectedDevice.value) return null
  const device = devices.value.find(d => d.id === selectedDevice.value)
  const position = positions.value.find(p => p.deviceId === selectedDevice.value)
  return device ? { device, position } : null
})

function selectDevice(deviceId) {
  selectedDevice.value = deviceId
  routePoints.value = []
}

function showRoute(points) {
  routePoints.value = points
}

function formatTime(isoString) {
  const date = new Date(isoString)
  return date.toLocaleString('es-ES', { 
    hour: '2-digit', 
    minute: '2-digit',
    day: '2-digit',
    month: 'short'
  })
}

async function fetchDevices() {
  try {
    devices.value = await devicesApi.getAll()
  } catch (error) {
    console.error('Error fetching devices:', error)
  }
}

async function fetchPositions() {
  try {
    positions.value = await positionsApi.getLatest()
  } catch (error) {
    console.error('Error fetching positions:', error)
  }
}

async function refreshData() {
  loading.value = true
  try {
    await Promise.all([fetchDevices(), fetchPositions()])
  } finally {
    loading.value = false
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

onMounted(async () => {
  await refreshData()
  // Auto-refresh every 30 seconds
  refreshInterval = setInterval(refreshData, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
/* Mobile panel slide animation */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease-out;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
}

/* Safe area for iOS */
.safe-area-bottom {
  padding-bottom: max(0.25rem, env(safe-area-inset-bottom));
}

/* Device info slide animation */
.animate-slide-in {
  animation: slideIn 0.2s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>

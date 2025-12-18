<template>
  <div class="h-full w-full relative">
    <div ref="mapContainer" class="h-full w-full"></div>
    
    <!-- Map controls -->
    <div class="absolute bottom-6 right-6 flex flex-col gap-2 z-[1000]">
      <button 
        @click="fitAllMarkers"
        class="p-3 bg-dark-100/90 backdrop-blur-lg rounded-xl border border-white/10 text-slate-400 hover:text-white hover:bg-dark-100 transition-all shadow-lg"
        title="Ver todos los dispositivos"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"></path>
        </svg>
      </button>
      <button 
        v-if="routePoints.length > 0"
        @click="$emit('clear-route')"
        class="p-3 bg-red-500/20 backdrop-blur-lg rounded-xl border border-red-500/30 text-red-400 hover:text-red-300 hover:bg-red-500/30 transition-all shadow-lg"
        title="Limpiar ruta"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import L from 'leaflet'

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
  routePoints: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['select-device', 'clear-route'])

const mapContainer = ref(null)
let map = null
let markers = {}
let routeLayer = null

// Custom icon
function createIcon(isOnline, isSelected) {
  const size = isSelected ? 40 : 32
  const color = isOnline ? '#22c55e' : '#64748b'
  const borderColor = isSelected ? '#ffffff' : 'rgba(255,255,255,0.7)'
  const borderWidth = isSelected ? 4 : 3
  
  return L.divIcon({
    className: 'custom-marker-wrapper',
    html: `
      <div style="
        width: ${size}px;
        height: ${size}px;
        background: ${color};
        border: ${borderWidth}px solid ${borderColor};
        border-radius: 50%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        ${isSelected ? 'animation: pulse 2s infinite;' : ''}
      ">
        <svg width="${size * 0.5}" height="${size * 0.5}" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5">
          <path d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
          <circle cx="12" cy="11" r="3"/>
        </svg>
      </div>
    `,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2]
  })
}

function initMap() {
  map = L.map(mapContainer.value, {
    center: [-33.45, -70.65], // Santiago, Chile as default
    zoom: 10,
    zoomControl: false
  })

  // Dark tile layer
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 20
  }).addTo(map)

  // Add zoom control to bottom left
  L.control.zoom({ position: 'bottomleft' }).addTo(map)

  // Add custom CSS for pulse animation
  const style = document.createElement('style')
  style.textContent = `
    @keyframes pulse {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.1); }
    }
    .custom-marker-wrapper {
      background: transparent !important;
      border: none !important;
    }
  `
  document.head.appendChild(style)
}

function updateMarkers() {
  // Remove old markers that are no longer in positions
  const currentDeviceIds = new Set(props.positions.map(p => p.deviceId))
  Object.keys(markers).forEach(id => {
    if (!currentDeviceIds.has(parseInt(id))) {
      map.removeLayer(markers[id])
      delete markers[id]
    }
  })

  // Update or add markers
  props.positions.forEach(position => {
    const device = props.devices.find(d => d.id === position.deviceId)
    if (!device) return

    const isOnline = device.status === 'online'
    const isSelected = props.selectedDevice === device.id
    const icon = createIcon(isOnline, isSelected)

    if (markers[device.id]) {
      // Update existing marker
      markers[device.id].setLatLng([position.latitude, position.longitude])
      markers[device.id].setIcon(icon)
    } else {
      // Create new marker
      const marker = L.marker([position.latitude, position.longitude], { icon })
        .addTo(map)
        .on('click', () => emit('select-device', device.id))

      // Custom popup
      const popupContent = `
        <div style="min-width: 180px; padding: 8px;">
          <h3 style="font-weight: 600; margin-bottom: 8px; color: #f8fafc;">${device.name}</h3>
          <p style="font-size: 12px; color: #94a3b8; margin-bottom: 4px;">
            <span style="display: inline-block; width: 8px; height: 8px; background: ${isOnline ? '#22c55e' : '#64748b'}; border-radius: 50%; margin-right: 6px;"></span>
            ${isOnline ? 'En línea' : 'Desconectado'}
          </p>
          <p style="font-size: 12px; color: #94a3b8;">
            Velocidad: ${Math.round(position.speed * 1.852)} km/h
          </p>
        </div>
      `
      marker.bindPopup(popupContent, {
        className: 'custom-popup',
        closeButton: false
      })

      markers[device.id] = marker
    }
  })
}

function drawRoute() {
  // Remove existing route
  if (routeLayer) {
    map.removeLayer(routeLayer)
    routeLayer = null
  }

  if (props.routePoints.length > 1) {
    const latLngs = props.routePoints.map(p => [p.latitude, p.longitude])
    
    routeLayer = L.polyline(latLngs, {
      color: '#22c55e',
      weight: 4,
      opacity: 0.8,
      smoothFactor: 1
    }).addTo(map)

    // Add start and end markers
    const startIcon = L.divIcon({
      className: 'route-marker',
      html: `<div style="width: 24px; height: 24px; background: #22c55e; border: 3px solid white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; color: white; font-weight: bold;">A</div>`,
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    })
    
    const endIcon = L.divIcon({
      className: 'route-marker',
      html: `<div style="width: 24px; height: 24px; background: #ef4444; border: 3px solid white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; color: white; font-weight: bold;">B</div>`,
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    })

    L.marker(latLngs[0], { icon: startIcon }).addTo(map)
    L.marker(latLngs[latLngs.length - 1], { icon: endIcon }).addTo(map)

    // Fit map to route
    map.fitBounds(routeLayer.getBounds(), { padding: [50, 50] })
  }
}

function fitAllMarkers() {
  if (props.positions.length === 0) return
  
  const bounds = L.latLngBounds(
    props.positions.map(p => [p.latitude, p.longitude])
  )
  map.fitBounds(bounds, { padding: [50, 50] })
}

function centerOnDevice(deviceId) {
  const position = props.positions.find(p => p.deviceId === deviceId)
  if (position) {
    map.setView([position.latitude, position.longitude], 15)
  }
}

// Watchers
watch(() => props.positions, updateMarkers, { deep: true })
watch(() => props.selectedDevice, (newVal) => {
  updateMarkers()
  if (newVal) centerOnDevice(newVal)
})
watch(() => props.routePoints, drawRoute, { deep: true })

onMounted(() => {
  initMap()
  if (props.positions.length > 0) {
    updateMarkers()
    fitAllMarkers()
  }
})

onUnmounted(() => {
  if (map) {
    map.remove()
  }
})
</script>


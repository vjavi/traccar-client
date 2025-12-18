<template>
  <!-- Expanded overlay backdrop -->
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="isExpanded"
        class="fixed inset-0 bg-black/80 backdrop-blur-sm"
        style="z-index: 9998;"
        @click="toggleExpanded"
      ></div>
    </Transition>
  </Teleport>

  <!-- Chat container - compact or expanded -->
  <Teleport to="body" :disabled="!isExpanded">
    <div 
      :class="[
        'flex flex-col bg-dark-100',
        isExpanded 
          ? 'fixed inset-4 md:inset-8 lg:inset-16 xl:inset-24 rounded-2xl shadow-2xl border border-white/10 animate-expand' 
          : 'h-full'
      ]"
      :style="isExpanded ? 'z-index: 9999;' : ''"
      @keydown="handleKeydown"
    >
    <!-- Header -->
    <div :class="['border-b border-white/10', isExpanded ? 'px-6 py-4' : 'p-4']">
      <!-- Expanded header - horizontal layout -->
      <div v-if="isExpanded" class="max-w-3xl mx-auto">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/20">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
              </svg>
            </div>
            <div>
              <h3 class="font-display font-bold text-xl text-white">AutoAssist IA</h3>
              <p class="text-sm text-slate-400">Asistente inteligente para tu vehículo</p>
            </div>
          </div>
          
          <div class="flex items-center gap-4">
            <!-- Device indicator (expanded) -->
            <div v-if="selectedDeviceName" class="bg-dark-200/50 rounded-xl px-4 py-2 flex items-center gap-2">
              <div class="w-2 h-2 bg-traccar-400 rounded-full animate-pulse"></div>
              <span class="text-sm text-slate-300 font-medium">{{ selectedDeviceName }}</span>
            </div>
            
            <!-- Time selector (expanded) -->
            <select
              v-model="hoursOfData"
              class="bg-dark-200/50 border border-white/10 rounded-xl px-4 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50"
            >
              <option :value="1">1h</option>
              <option :value="6">6h</option>
              <option :value="12">12h</option>
              <option :value="24">24h</option>
              <option :value="48">2 días</option>
              <option :value="168">7 días</option>
            </select>
            
            <!-- Close button -->
            <button
              @click="toggleExpanded"
              class="p-2 hover:bg-white/10 rounded-xl transition-colors group"
              title="Minimizar chat"
            >
              <svg class="w-6 h-6 text-slate-400 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Compact header - vertical layout -->
      <div v-else>
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
              </svg>
            </div>
            <div>
              <h3 class="font-display font-semibold text-white">AutoAssist IA</h3>
              <p class="text-xs text-slate-400">Pregunta sobre tu vehículo</p>
            </div>
          </div>
          
          <!-- Expand button -->
          <button
            @click="toggleExpanded"
            class="p-2 hover:bg-white/10 rounded-lg transition-colors group"
            title="Expandir chat"
          >
            <svg class="w-5 h-5 text-slate-400 group-hover:text-purple-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"></path>
            </svg>
          </button>
        </div>

        <!-- Device indicator (compact) -->
        <div v-if="selectedDeviceName" class="bg-dark-200/50 rounded-xl p-3 flex items-center gap-2">
          <div class="w-2 h-2 bg-traccar-400 rounded-full"></div>
          <span class="text-sm text-slate-300">{{ selectedDeviceName }}</span>
        </div>
        <div v-else class="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-3">
          <p class="text-yellow-400 text-sm">Selecciona un dispositivo para chatear</p>
        </div>

        <!-- Time range selector (compact) -->
        <div class="mt-3">
          <label class="block text-xs text-slate-400 mb-1">Analizar datos de:</label>
          <select
            v-model="hoursOfData"
            class="w-full bg-dark-200/50 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50"
          >
            <option :value="1">Última hora</option>
            <option :value="6">Últimas 6 horas</option>
            <option :value="12">Últimas 12 horas</option>
            <option :value="24">Últimas 24 horas</option>
            <option :value="48">Últimos 2 días</option>
            <option :value="168">Última semana</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Messages -->
    <div ref="messagesContainer" :class="['flex-1 overflow-y-auto', isExpanded ? 'px-6 py-6' : 'p-4']">
      <div :class="['space-y-4', isExpanded ? 'max-w-3xl mx-auto' : '']">
      <!-- Welcome message -->
      <div v-if="messages.length === 0" :class="['text-center', isExpanded ? 'py-16' : 'py-8']">
        <div :class="[
          'bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4',
          isExpanded ? 'w-20 h-20' : 'w-16 h-16'
        ]">
          <svg :class="['text-purple-400', isExpanded ? 'w-10 h-10' : 'w-8 h-8']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
          </svg>
        </div>
        <h4 :class="['text-white font-medium mb-2', isExpanded ? 'text-2xl' : '']">¡Hola! Soy AutoAssist</h4>
        <p :class="['text-slate-400 mb-6', isExpanded ? 'text-base' : 'text-sm mb-4']">Puedo ayudarte a entender los datos de tu vehículo</p>
        
        <!-- Suggested questions -->
        <div :class="['space-y-2', isExpanded ? 'max-w-md mx-auto' : '']">
          <p class="text-xs text-slate-500 mb-3">Prueba preguntar:</p>
          <button
            v-for="suggestion in suggestions"
            :key="suggestion"
            @click="sendSuggestion(suggestion)"
            :disabled="!selectedDevice || loading"
            :class="[
              'block w-full text-left bg-dark-200/30 hover:bg-purple-500/10 border border-white/5 hover:border-purple-500/30 rounded-xl text-slate-400 hover:text-purple-300 transition-all disabled:opacity-50 disabled:cursor-not-allowed',
              isExpanded ? 'px-4 py-3 text-base' : 'px-3 py-2 text-sm'
            ]"
          >
            {{ suggestion }}
          </button>
        </div>
      </div>

      <!-- Chat messages -->
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="[
          'flex',
          message.role === 'user' ? 'justify-end' : 'justify-start'
        ]"
      >
        <div
          :class="[
            'rounded-2xl animate-fade-in',
            isExpanded ? 'max-w-[70%] px-5 py-4' : 'max-w-[85%] px-4 py-3',
            message.role === 'user'
              ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-500/20'
              : 'bg-dark-200/50 border border-white/10 text-slate-200'
          ]"
        >
          <div v-if="message.role === 'assistant'" class="flex items-center gap-2 mb-2">
            <div :class="['bg-gradient-to-br from-purple-500 to-pink-500 rounded-md flex items-center justify-center', isExpanded ? 'w-6 h-6' : 'w-5 h-5']">
              <svg :class="['text-white', isExpanded ? 'w-4 h-4' : 'w-3 h-3']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
              </svg>
            </div>
            <span :class="['text-slate-400', isExpanded ? 'text-sm' : 'text-xs']">AutoAssist</span>
          </div>
          <div :class="['whitespace-pre-wrap leading-relaxed prose prose-invert max-w-none', isExpanded ? 'text-base prose-base' : 'text-sm prose-sm']" v-html="formatMarkdown(message.content)"></div>
        </div>
      </div>

      <!-- Typing indicator -->
      <div v-if="loading" class="flex justify-start">
        <div :class="['bg-dark-200/50 border border-white/10 rounded-2xl', isExpanded ? 'px-5 py-4' : 'px-4 py-3']">
          <div class="flex items-center gap-3">
            <div class="flex gap-1">
              <span class="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
              <span class="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
              <span class="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
            </div>
            <span :class="['text-slate-400', isExpanded ? 'text-sm' : 'text-xs']">Analizando datos...</span>
          </div>
        </div>
      </div>
      </div>
    </div>

    <!-- Input -->
    <div :class="['border-t border-white/10', isExpanded ? 'px-6 py-4' : 'p-4']">
      <div :class="isExpanded ? 'max-w-3xl mx-auto' : ''">
        <div v-if="error" class="mb-3 bg-red-500/10 border border-red-500/30 rounded-lg p-3">
          <p class="text-red-400 text-xs">{{ error }}</p>
        </div>
        
        <form @submit.prevent="sendMessage" class="flex gap-3">
          <input
            v-model="inputMessage"
            type="text"
            placeholder="Escribe tu pregunta..."
            :disabled="!selectedDevice || loading"
            :class="[
              'flex-1 bg-dark-200/50 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all disabled:opacity-50',
              isExpanded ? 'px-5 py-4 text-base' : 'px-4 py-3 text-sm'
            ]"
          />
          <button
            type="submit"
            :disabled="!inputMessage.trim() || !selectedDevice || loading"
            :class="[
              'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-400 hover:to-pink-400 disabled:from-slate-600 disabled:to-slate-700 text-white rounded-xl transition-all disabled:cursor-not-allowed shadow-lg shadow-purple-500/20',
              isExpanded ? 'px-6 py-4' : 'px-4 py-3'
            ]"
          >
            <svg :class="isExpanded ? 'w-6 h-6' : 'w-5 h-5'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
            </svg>
          </button>
        </form>

        <!-- Data summary -->
        <div v-if="dataSummary" :class="['mt-3 flex items-center gap-2 text-slate-500', isExpanded ? 'justify-center text-sm' : 'text-xs']">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <span>{{ dataSummary.positions_count }} posiciones · {{ dataSummary.events_count }} eventos · {{ dataSummary.trips_count }} viajes ({{ dataSummary.hours_analyzed }}h)</span>
        </div>
      </div>
    </div>
  </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { chatApi } from '../services/api'

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

const messagesContainer = ref(null)
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const error = ref('')
const hoursOfData = ref(24)
const dataSummary = ref(null)
const isExpanded = ref(false)

function toggleExpanded() {
  isExpanded.value = !isExpanded.value
  // Scroll to bottom after expanding
  nextTick(() => scrollToBottom())
}

// Close on escape key
function handleKeydown(e) {
  if (e.key === 'Escape' && isExpanded.value) {
    isExpanded.value = false
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})

const suggestions = [
  "¿Cuál fue la velocidad máxima hoy?",
  "¿Cuántos kilómetros recorrió?",
  "¿Hubo algún exceso de velocidad?",
  "Resume la actividad del vehículo",
  "¿A qué hora se usó más el vehículo?"
]

const selectedDeviceName = computed(() => {
  const device = props.devices.find(d => d.id === props.selectedDevice)
  return device?.name || null
})

// Reset chat when device changes
watch(() => props.selectedDevice, () => {
  messages.value = []
  error.value = ''
  dataSummary.value = null
})

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

function formatMarkdown(text) {
  if (!text) return ''
  
  // Escape HTML first
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  // Bold: **text** or __text__
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong class="text-white font-semibold">$1</strong>')
  html = html.replace(/__(.+?)__/g, '<strong class="text-white font-semibold">$1</strong>')
  
  // Italic: *text* or _text_
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>')
  html = html.replace(/_([^_]+)_/g, '<em>$1</em>')
  
  // Lists: - item
  html = html.replace(/^- (.+)$/gm, '<span class="flex gap-2"><span class="text-purple-400">•</span><span>$1</span></span>')
  
  // Code: `code`
  html = html.replace(/`([^`]+)`/g, '<code class="bg-dark-200 px-1.5 py-0.5 rounded text-purple-300 text-xs">$1</code>')
  
  return html
}

function sendSuggestion(suggestion) {
  inputMessage.value = suggestion
  sendMessage()
}

async function sendMessage() {
  if (!inputMessage.value.trim() || !props.selectedDevice || loading.value) return

  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''
  error.value = ''

  // Add user message
  messages.value.push({
    role: 'user',
    content: userMessage
  })
  scrollToBottom()

  loading.value = true

  try {
    // Prepare conversation history (last 10 messages to keep context manageable)
    const conversationHistory = messages.value.slice(-10, -1).map(m => ({
      role: m.role,
      content: m.content
    }))

    const response = await chatApi.send(
      props.selectedDevice,
      userMessage,
      hoursOfData.value,
      conversationHistory
    )

    // Add assistant response
    messages.value.push({
      role: 'assistant',
      content: response.response
    })

    dataSummary.value = response.data_summary
    scrollToBottom()

  } catch (err) {
    console.error('Chat error:', err)
    error.value = err.response?.data?.detail || 'Error al enviar el mensaje'
    // Remove the user message if there was an error
    messages.value.pop()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Fade transition for backdrop */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Expand animation */
.animate-expand {
  animation: expandIn 0.25s ease-out;
}

@keyframes expandIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>


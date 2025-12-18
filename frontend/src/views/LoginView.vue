<template>
  <div class="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
    <!-- Background effects -->
    <div class="absolute inset-0 overflow-hidden">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-traccar-500/20 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-traccar-600/10 rounded-full blur-3xl"></div>
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-traccar-500/5 rounded-full blur-3xl"></div>
    </div>

    <!-- Login Card -->
    <div class="w-full max-w-md relative">
      <div class="bg-dark-100/80 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/10 p-8 animate-fade-in">
        <!-- Logo/Header -->
        <div class="text-center mb-8">
          <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-traccar-400 to-traccar-600 rounded-2xl shadow-lg shadow-traccar-500/30 mb-4 animate-pulse-glow">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
          </div>
          <h1 class="text-3xl font-display font-bold text-white mb-2">Traccar Client</h1>
          <p class="text-slate-400 text-sm">Conecta con tu servidor de rastreo GPS</p>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleLogin" class="space-y-5">
          <!-- Traccar URL -->
          <div class="animate-fade-in stagger-1" style="opacity: 0;">
            <label class="block text-sm font-medium text-slate-300 mb-2">
              URL del Servidor
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg class="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path>
                </svg>
              </div>
              <input
                v-model="form.traccarUrl"
                type="url"
                required
                placeholder="https://demo2.traccar.org"
                class="w-full bg-dark-200/50 border border-white/10 rounded-xl pl-12 pr-4 py-3.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-traccar-500/50 focus:border-traccar-500 transition-all"
              />
            </div>
          </div>

          <!-- Username -->
          <div class="animate-fade-in stagger-2" style="opacity: 0;">
            <label class="block text-sm font-medium text-slate-300 mb-2">
              Usuario
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg class="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
              </div>
              <input
                v-model="form.username"
                type="text"
                required
                placeholder="Tu usuario"
                class="w-full bg-dark-200/50 border border-white/10 rounded-xl pl-12 pr-4 py-3.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-traccar-500/50 focus:border-traccar-500 transition-all"
              />
            </div>
          </div>

          <!-- Password -->
          <div class="animate-fade-in stagger-3" style="opacity: 0;">
            <label class="block text-sm font-medium text-slate-300 mb-2">
              Contraseña
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg class="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                </svg>
              </div>
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                required
                placeholder="Tu contraseña"
                class="w-full bg-dark-200/50 border border-white/10 rounded-xl pl-12 pr-12 py-3.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-traccar-500/50 focus:border-traccar-500 transition-all"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-500 hover:text-slate-300 transition-colors"
              >
                <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path>
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                </svg>
              </button>
            </div>
          </div>

          <!-- Error message -->
          <div v-if="error" class="bg-red-500/10 border border-red-500/30 rounded-xl p-4 animate-fade-in">
            <div class="flex items-center gap-3">
              <svg class="w-5 h-5 text-red-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <p class="text-red-400 text-sm">{{ error }}</p>
            </div>
          </div>

          <!-- Submit button -->
          <div class="animate-fade-in stagger-4" style="opacity: 0;">
            <button
              type="submit"
              :disabled="loading"
              class="w-full bg-gradient-to-r from-traccar-500 to-traccar-600 hover:from-traccar-400 hover:to-traccar-500 disabled:from-slate-600 disabled:to-slate-700 text-white font-semibold py-4 px-6 rounded-xl shadow-lg shadow-traccar-500/30 hover:shadow-traccar-500/40 transition-all duration-300 flex items-center justify-center gap-2"
            >
              <svg v-if="loading" class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              <span>{{ loading ? 'Conectando...' : 'Conectar' }}</span>
            </button>
          </div>
        </form>

        <!-- Footer -->
        <p class="text-center text-slate-500 text-xs mt-6 animate-fade-in stagger-5" style="opacity: 0;">
          Cliente no oficial para Traccar GPS Tracking
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { authApi } from '../services/api'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  traccarUrl: 'https://demo2.traccar.org',
  username: '',
  password: ''
})

const loading = ref(false)
const error = ref('')
const showPassword = ref(false)

async function handleLogin() {
  loading.value = true
  error.value = ''

  try {
    const response = await authApi.login(
      form.traccarUrl,
      form.username,
      form.password
    )

    if (response.success) {
      authStore.setAuth(response.token, response.user, form.traccarUrl)
      router.push('/dashboard')
    }
  } catch (err) {
    console.error('Login error:', err)
    error.value = err.response?.data?.detail || 'Error al conectar con el servidor'
  } finally {
    loading.value = false
  }
}
</script>


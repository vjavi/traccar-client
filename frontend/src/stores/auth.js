import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('traccar_token') || null)
  const user = ref(JSON.parse(localStorage.getItem('traccar_user') || 'null'))
  const traccarUrl = ref(localStorage.getItem('traccar_url') || 'https://demo2.traccar.org')

  const isAuthenticated = computed(() => !!token.value)

  function setAuth(authToken, userData, url) {
    token.value = authToken
    user.value = userData
    traccarUrl.value = url
    
    localStorage.setItem('traccar_token', authToken)
    localStorage.setItem('traccar_user', JSON.stringify(userData))
    localStorage.setItem('traccar_url', url)
  }

  function logout() {
    token.value = null
    user.value = null
    
    localStorage.removeItem('traccar_token')
    localStorage.removeItem('traccar_user')
  }

  return {
    token,
    user,
    traccarUrl,
    isAuthenticated,
    setAuth,
    logout
  }
})


<template>
  <div id="app" class="app-container">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'

const authStore = useAuthStore()
const uiStore = useUIStore()

onMounted(async () => {
  // Initialize theme
  uiStore.initializeTheme()
  
  // Try to restore authentication state
  const token = localStorage.getItem('access_token')
  if (token && !authStore.isAuthenticated) {
    try {
      await authStore.getCurrentUser()
    } catch (error) {
      console.error('Failed to restore authentication:', error)
      authStore.logout()
    }
  }
})
</script>

<style lang="scss">
// Import global styles
@import '@/styles/index.scss';

.app-container {
  min-height: 100vh;
  background-color: var(--el-bg-color-page);
  color: var(--el-text-color-primary);
  font-family: 'Noto Sans JP', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  
  // Smooth transitions for theme changes
  transition: background-color 0.3s ease, color 0.3s ease;
}

// Global scrollbar styles
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--el-fill-color-lighter);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: var(--el-fill-color-dark);
  border-radius: 4px;
  
  &:hover {
    background: var(--el-fill-color-darker);
  }
}

// Print styles
@media print {
  .no-print {
    display: none !important;
  }
  
  .app-container {
    background: white !important;
    color: black !important;
  }
}
</style>
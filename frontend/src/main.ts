import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { createI18n } from 'vue-i18n'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'

// Import global styles
import './styles/index.scss'

// Import locales
import ja from './locales/ja.json'
import en from './locales/en.json'

// Configure NProgress
NProgress.configure({
  showSpinner: false,
  minimum: 0.2,
  speed: 500
})

// Create i18n instance
const i18n = createI18n({
  legacy: false,
  locale: 'ja',
  fallbackLocale: 'en',
  messages: {
    ja,
    en
  }
})

// Create Vue app
const app = createApp(App)

// Create Pinia store
const pinia = createPinia()

// Use plugins
app.use(pinia)
app.use(router)
app.use(ElementPlus, {
  size: 'default',
  zIndex: 3000
})
app.use(i18n)

// Register Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// Global error handler
app.config.errorHandler = (err, vm, info) => {
  console.error('Global error:', err, info)
  ElMessage.error('システムエラーが発生しました')
}

// Initialize auth store and check authentication
const authStore = useAuthStore()

// Router guards
router.beforeEach(async (to, from, next) => {
  NProgress.start()
  
  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // Try to restore session from localStorage
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          await authStore.getCurrentUser()
        } catch (error) {
          console.error('Failed to restore session:', error)
          authStore.logout()
        }
      }
      
      if (!authStore.isAuthenticated) {
        next({ name: 'Login', query: { redirect: to.fullPath } })
        return
      }
    }
    
    // Check permissions if specified
    if (to.meta.permission && !authStore.hasPermission(to.meta.permission as string)) {
      ElMessage.error('このページにアクセスする権限がありません')
      next({ name: 'Dashboard' })
      return
    }
  }
  
  // Redirect authenticated users away from auth pages
  if (to.meta.guestOnly && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
    return
  }
  
  next()
})

router.afterEach(() => {
  NProgress.done()
})

// Mount app
app.mount('#app')

// Hide loading screen
document.body.classList.add('app-ready')

// Global unhandled promise rejection handler
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason)
  ElMessage.error('予期しないエラーが発生しました')
})

// Service worker registration (for PWA support)
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration)
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError)
      })
  })
}
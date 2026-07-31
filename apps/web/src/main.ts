import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { registerSW } from 'virtual:pwa-register'
import Toast, { POSITION } from 'vue-toastification'

import App from './App.vue'
import router from './router'

// Bootstrap CSS + JS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'bootstrap'
import 'vue-toastification/dist/index.css'

// Custom theme overrides
import './styles/main.scss'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Toast, {
  position: POSITION.TOP_RIGHT,
  timeout: 5000,
  closeOnClick: false,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  hideProgressBar: false,
  closeButton: true,
})

app.mount('#app')

const updateServiceWorker = registerSW({
  immediate: true,
  onNeedRefresh() {
    window.dispatchEvent(new Event('kairo:pwa-update-available'))
  },
})

window.addEventListener('kairo:pwa-apply-update', () => {
  void updateServiceWorker(true)
})

window.setInterval(() => {
  void updateServiceWorker()
}, 60_000)

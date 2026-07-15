import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'

import AOS from 'aos'
import 'aos/dist/aos.css'

AOS.init({
  duration: 800,
  once: true
})
createApp(App).use(router).mount('#app')

import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js' // Assurez-vous d'importer le routeur

const app = createApp(App)
app.use(router) // Active Vue Router
app.mount('#app')

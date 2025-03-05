import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router/index.js' // Assurez-vous d'importer le routeur

// Import de Font Awesome localement
// Ajouter tous les styles pour assurer que toutes les icônes sont disponibles
import '@fortawesome/fontawesome-free/css/fontawesome.min.css'
import '@fortawesome/fontawesome-free/css/solid.min.css'
import '@fortawesome/fontawesome-free/css/regular.min.css'
import '@fortawesome/fontawesome-free/css/brands.min.css'
import '@fortawesome/fontawesome-free/css/all.min.css'
// Import du CSS de correction d'icônes
import './assets/icon-fixes.css'

const app = createApp(App)
const pinia = createPinia()

app.use(router) // Active Vue Router
app.use(pinia) // Active Pinia pour la gestion d'état
app.mount('#app')

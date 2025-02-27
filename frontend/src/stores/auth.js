import { ref, reactive } from 'vue'

// Créer un état réactif qui sera partagé entre les composants
const authState = reactive({
  isAuthenticated: !!localStorage.getItem('pseudo'),
  pseudo: localStorage.getItem('pseudo') || '',
  isAdmin: localStorage.getItem('is_admin') === 'true'
})

// Fonctions pour mettre à jour l'état
export function login(userData) {
  // Stocker les données dans localStorage
  localStorage.setItem('pseudo', userData.pseudo)
  localStorage.setItem('is_admin', userData.is_admin)
  
  // Mettre à jour l'état réactif
  authState.isAuthenticated = true
  authState.pseudo = userData.pseudo
  authState.isAdmin = userData.is_admin === true
}

export function logout() {
  // Supprimer les données du localStorage
  localStorage.removeItem('pseudo')
  localStorage.removeItem('is_admin')
  
  // Mettre à jour l'état réactif
  authState.isAuthenticated = false
  authState.pseudo = ''
  authState.isAdmin = false
}

// Exporter l'état pour qu'il soit accessible dans les composants
export default authState

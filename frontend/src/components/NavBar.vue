<script setup>
import { watch, ref } from 'vue'
import { useRouter } from 'vue-router'
import authState, { logout as logoutAction } from '../stores/auth'

const router = useRouter()
const isActive = ref(false)

const logout = () => {
  logoutAction()
  router.push('/')
}

const toggleMenu = () => {
  isActive.value = !isActive.value
}

// Fermer le menu quand on change de route
watch(() => router.currentRoute.value.path, () => {
  isActive.value = false
})
</script>

<template>
  <nav class="navbar is-fixed-top" role="navigation" aria-label="main navigation">
    <div class="container is-fluid">
      <div class="navbar-brand">
        <!-- Remplacer "Accueil" par un menu burger pour la page de chat -->
        <template v-if="router.currentRoute.value.path === '/chat'">
          <router-link to="/" class="navbar-item">
            <span class="icon">
              🏠
            </span>
          </router-link>
        </template>
        <template v-else>
          <router-link to="/" class="navbar-item"><span class="icon">
              🏠
            </span></router-link>
        </template>
        
        <router-link to="/about" class="navbar-item">A propos</router-link>
        
      
        
        <!-- Hamburger pour mobile -->
        <a 
          role="button" 
          class="navbar-burger" 
          :class="{ 'is-active': isActive }"
          aria-label="menu" 
          aria-expanded="false" 
          @click="toggleMenu"
        >
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
        </a>
      </div>

      <div id="navbarMenu" class="navbar-menu" :class="{ 'is-active': isActive }">
        <div class="navbar-end">
          <div class="navbar-item">
            <div v-if="authState.isAuthenticated" class="navbar-item has-dropdown is-hoverable">
              <a class="navbar-link">
                Bonjour, {{ authState.pseudo }}
              </a>
              <div class="navbar-dropdown is-right">
                <router-link to="/chat" class="navbar-item">
                  Chat
                </router-link>
                <hr class="navbar-divider">
                <a class="navbar-item" @click="logout">
                  Déconnexion
                </a>
              </div>
            </div>
            
            <div v-else class="buttons">
              <router-link to="/login" class="button is-primary">Connexion</router-link>
              <router-link to="/register" class="button is-light">Inscription</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  box-shadow: 0 2px 3px rgba(10, 10, 10, 0.1);
}
</style>

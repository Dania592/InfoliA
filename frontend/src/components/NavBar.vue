<script setup>
import { onMounted, watch, ref } from 'vue'
import { useRouter } from 'vue-router'
import authState, { logout as logoutAction } from '../stores/auth'

const router = useRouter()
const isActive = ref(false)
const isSidebarActive = ref(false)

const logout = () => {
  logoutAction()
  router.push('/') // Redirige vers l'accueil
}

const toggleMenu = () => {
  isActive.value = !isActive.value
}

const toggleSidebar = () => {
  isSidebarActive.value = !isSidebarActive.value
}

// Fermer le menu quand on change de route
watch(() => router.currentRoute.value.path, () => {
  isActive.value = false
  isSidebarActive.value = false
})
</script>

<template>
  <nav class="navbar is-fixed-top" role="navigation" aria-label="main navigation">
    <div class="container is-fluid">
      <div class="navbar-brand">
        <!-- Remplacer "Accueil" par un menu burger pour la page de chat -->
        <template v-if="router.currentRoute.value.path === '/chat'">
          <a 
            role="button" 
            class="navbar-item sidebar-toggle"
            :class="{ 'is-active': isSidebarActive }"
            @click="toggleSidebar"
          >
            <span class="icon">
              <i class="fas fa-comment"></i>
            </span>
          </a>
        </template>
        <template v-else>
          <router-link to="/" class="navbar-item">Accueil</router-link>
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
  
  <!-- Sidebar pour la page de chat -->
  <div class="sidebar" :class="{ 'is-active': isSidebarActive && router.currentRoute.value.path === '/chat' }">
    <div class="sidebar-header">
      <h3 class="title is-5">Menu</h3>
      <button class="delete" @click="toggleSidebar"></button>
    </div>
    <div class="sidebar-content">
      <aside class="menu">
        <p class="menu-label">
          Navigation
        </p>
        <ul class="menu-list">
          <li><router-link to="/" @click="toggleSidebar">Accueil</router-link></li>
          <li><router-link to="/about" @click="toggleSidebar">A propos</router-link></li>
        </ul>
        <p class="menu-label">
          Conversations
        </p>
        <ul class="menu-list">
          <li><a>Nouvelle conversation</a></li>
          <li><a>Historique</a></li>
        </ul>
      </aside>
    </div>
  </div>
  
  <!-- Overlay pour fermer le sidebar en cliquant à l'extérieur -->
  <div 
    class="sidebar-overlay" 
    :class="{ 'is-active': isSidebarActive && router.currentRoute.value.path === '/chat' }"
    @click="toggleSidebar"
  ></div>
</template>

<style scoped>
@import "../../node_modules/bulma";

/* Ajouter un peu d'espace en haut pour la navbar fixe */
.navbar {
  box-shadow: 0 2px 3px rgba(10, 10, 10, 0.1);
}

/* Styles pour la version mobile */
@media screen and (max-width: 1023px) {
  .navbar-menu.is-active {
    position: absolute;
    width: 100%;
    box-shadow: 0 8px 16px rgba(10, 10, 10, 0.1);
  }
}

/* Styles pour le sidebar */
.sidebar {
  position: fixed;
  top: 3.25rem;
  left: 0;
  width: 280px;
  height: calc(100vh - 3.25rem);
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  z-index: 29;
  transform: translateX(-100%);
  transition: transform 0.3s ease-in-out;
  overflow-y: auto;
}

.sidebar.is-active {
  transform: translateX(0);
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #f5f5f5;
}

.sidebar-content {
  padding: 1rem;
}

.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 28;
  display: none;
}

.sidebar-overlay.is-active {
  display: block;
}

.sidebar-toggle {
  cursor: pointer;
}
</style>

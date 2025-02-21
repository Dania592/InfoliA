<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isAuthenticated = ref(false)

onMounted(() => {
  // Vérifie si un utilisateur est connecté
  isAuthenticated.value = !!localStorage.getItem('user')
})

const logout = () => {
  localStorage.removeItem('user') // Supprime les données de session
  isAuthenticated.value = false // Met à jour l'état
  router.push('/') // Redirige vers l'accueil
}
</script>

<template>
  <nav class="navbar is-fixed-top" role="navigation" aria-label="main navigation">
    <div class="container is-fluid">
      <div class="navbar-brand">
        <router-link to="/" class="navbar-item">Accueil</router-link>
        <router-link to="/about" class="navbar-item">A propos</router-link>
      </div>

      <div class="navbar-menu">
        <div class="navbar-end">
          <div class="navbar-item">
            <div class="buttons">
              <!-- Si l'utilisateur est connecté, on affiche le bouton de déconnexion -->
              <button v-if="isAuthenticated" @click="logout" class="button is-danger">
                Déconnexion
              </button>
              
              <!-- Sinon, on affiche les boutons Connexion / Inscription -->
              <template v-else>
                <router-link to="/login" class="button is-primary">Connexion</router-link>
                <router-link to="/register" class="button is-light">Inscription</router-link>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
@import "../../node_modules/bulma";
</style>

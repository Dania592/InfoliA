<script setup>
import { ref, onMounted } from 'vue'
import {RouterView, RouterLink} from 'vue-router'
import NavBar from './components/NavBar.vue'

const message = ref('')

onMounted(async () => {
  try {
    const res = await fetch('http://localhost:8000/api/hello/')
    const data = await res.json()
    message.value = data.message
  } catch (error) {
    console.error("Erreur lors de la récupération des données", error)
  }
})
</script>

<template>
  <div>
    <NavBar />
    <div class="container main-content">
      <RouterView />
    </div>
  </div>
</template>

<style>
/* Ajout d'un peu d'espace pour la navbar fixe */
.main-content {
  margin-top: 4rem;
  padding: 1.5rem;
}
</style>

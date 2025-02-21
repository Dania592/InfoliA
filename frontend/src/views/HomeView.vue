<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const pseudo = ref(null)
const router = useRouter()

onMounted(() => {
  // Vérifie si un utilisateur est connecté
  const storedUser = localStorage.getItem('pseudo')
  if (storedUser) {
    pseudo.value = storedUser
  } else {
    pseudo.value = null
  }
})

const logout = () => {
  localStorage.removeItem('pseudo')
  router.push('/')
}
</script>

<template>
  <section>
    <div class="container">
      <v-if pseudo>
      <h1 class="title is-centered">Bienvenue {{ pseudo }} sur Infolia</h1>
      <p class="subtitle is-centered">Votre plateforme de partage de connaissances</p>
      </v-if>
      <v-else pseudo>
        <h1 class="title is-centered">Bienvenue sur Infolia</h1>
        <p class="subtitle is-centered">Votre plateforme de partage de connaissances</p>
      </v-else>
      <div class="field">
        <div class="control">
          <button class="button is-primary is-fullwidth" @click="logout">Se deconnecter</button>
        </div>
      </div>
    </div>
  </section>
</template>

<style>
@import "../assets/main.css";
</style>
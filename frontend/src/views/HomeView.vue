<script setup>
import authState from '../stores/auth'
</script>

<template>
  <section>
    <div class="container">
      <template v-if="authState.isAuthenticated">
        <h1 class="title is-centered">Bienvenue {{ authState.pseudo }} sur Infolia</h1>
        <p class="subtitle is-centered">Votre plateforme de partage de connaissances</p>
      </template>
      <template v-else>
        <h1 class="title is-centered">Bienvenue sur Infolia</h1>
        <p class="subtitle is-centered">Votre plateforme de partage de connaissances</p>
      </template>
    </div>
  </section>
</template>


<style>
@import "../assets/main.css";
</style>
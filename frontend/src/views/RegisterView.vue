<script setup>
import { ref } from 'vue'

const pseudo = ref('')
const password = ref('')
const confirmPassword = ref('')
const errorMessage = ref('')
const successMessage = ref('')

const register = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  if (password.value !== confirmPassword.value) {
    errorMessage.value = "Les mots de passe ne correspondent pas"
    return
  }

  try {
    const response = await fetch('http://127.0.0.1:8000/api/register/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        pseudo: pseudo.value,
        password: password.value,
        is_admin: false
      })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || "Échec de l'inscription")
    }

    successMessage.value = "Compte créé avec succès ! Vous pouvez vous connecter."
    pseudo.value = ''
    password.value = ''
    confirmPassword.value = ''
  } catch (error) {
    errorMessage.value = error.message
  }
}
</script>

<template>
  <div class="field is-align-items-center">
    <h1 class="title has-text-centered">Inscription</h1>

    <form @submit.prevent="register">
      <!-- Champ Pseudo -->
      <div class="field">
        <label class="label" for="pseudo">Pseudo</label>
        <div class="control">
                  <input id="pseudo" class="input" v-model="pseudo" placeholder="Entrez votre pseudo" required />
                </div>
              </div>

              <!-- Champ Mot de passe -->
              <div class="field">
                <label class="label" for="password">Mot de passe</label>
                <div class="control">
                  <input id="password" class="input" type="password" v-model="password" placeholder="Entrez un mot de passe" required />
                </div>
              </div>

              <!-- Champ Confirmation du mot de passe -->
              <div class="field">
                <label class="label" for="confirmPassword">Confirmez le mot de passe</label>
                <div class="control">
                  <input id="confirmPassword" class="input" type="password" v-model="confirmPassword" placeholder="Confirmez votre mot de passe" required />
                </div>
              </div>

              <!-- Message d'erreur -->
              <p v-if="errorMessage" class="notification is-danger">{{ errorMessage }}</p>

              <!-- Message de succès -->
              <p v-if="successMessage" class="notification is-success">{{ successMessage }}</p>

              <!-- Bouton S'inscrire -->
              <div class="field">
                <div class="control">
                  <button class="button is-primary is-fullwidth">S'inscrire</button>
                </div>
              </div>
            </form>
      </div>
</template>

<style scoped>
/* Assure que la section prend toute la hauteur de l'écran */
.section {
  min-height: 100vh;
}

/* Ajout d'une ombre et d'un effet moderne */
.box {
  border-radius: 10px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}
</style>

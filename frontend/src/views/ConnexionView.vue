<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login as loginAction } from '../stores/auth'

const pseudo = ref('')
const password = ref('')
const errorMessage = ref('')
const successMessage = ref('')
const router = useRouter()

const login = async () => {
    errorMessage.value = ''
    successMessage.value = ''

    try {
        const response = await fetch('http://localhost:8000/api/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pseudo: pseudo.value,
                password: password.value
            })
        })

        const data = await response.json()
        if (!response.ok) {
            throw new Error(data.detail || "Échec de la connexion")
        }

        // Utiliser la fonction login du store pour mettre à jour l'état global
        loginAction({
            pseudo: data.pseudo,
            is_admin: data.is_admin
        })

        successMessage.value = "Connexion reussie !"
        pseudo.value = ''
        password.value = ''
        
        // Redirection vers la page de chat
        router.push('/chat')
    } catch (error) {
        errorMessage.value = error.message
    }
}   
</script>  

<template>
    <div class="container">
        <div>
            <h1 class="title">Connexion</h1>
            <form @submit.prevent="login">
                <div class="field">
                    <label class="label" for="pseudo">Pseudo</label>
                    <div class="control">
                        <input id="pseudo" class="input" v-model="pseudo" placeholder="Entrez votre pseudo" required />
                    </div>
                </div>
                <div class="field">
                    <label class="label" for="password">Mot de passe</label>
                    <div class="control">
                        <input id="password" class="input" type="password" v-model="password" placeholder="Entrez votre mot de passe" required />
                    </div>
                </div>
                <div class="field">
                    <div class="control">
                        <button class="button is-primary is-fullwidth">Se connecter</button>
                    </div>
                </div>
            </form>
            <p v-if="errorMessage" class="help is-danger">{{ errorMessage }}</p>
            <p v-if="successMessage" class="help is-success">{{ successMessage }}</p>
        </div>
    </div>
</template>
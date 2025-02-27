<script setup>
import { ref } from 'vue'
import authState from '../stores/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
const messages = ref([])
const newMessage = ref('')

// Rediriger vers la page de connexion si l'utilisateur n'est pas connecté
if (!authState.isAuthenticated) {
  router.push('/login')
}

const sendMessage = () => {
  if (newMessage.value.trim() === '') return
  
  // Ajouter le message de l'utilisateur
  messages.value.push({
    id: Date.now(),
    text: newMessage.value,
    sender: 'user',
    timestamp: new Date().toLocaleTimeString()
  })
  
  // Réinitialiser le champ de saisie
  const userMessage = newMessage.value
  newMessage.value = ''
  
  // Simuler une réponse du chatbot (message générique)
  setTimeout(() => {
    messages.value.push({
      id: Date.now() + 1,
      text: `Vous avez dit: "${userMessage}". Je suis un chatbot basique et je ne peux pas encore générer de réponses intelligentes.`,
      sender: 'bot',
      timestamp: new Date().toLocaleTimeString()
    })
    
    // Faire défiler vers le bas pour voir le nouveau message
    scrollToBottom()
  }, 1000)
}

const scrollToBottom = () => {
  setTimeout(() => {
    const chatContainer = document.querySelector('.chat-messages')
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight
    }
  }, 50)
}
</script>

<template>
  <div class="chat-container">
    <div class="chat-header">
      <h1 class="title">Chat avec InfoliA</h1>
    </div>
    
    <div class="chat-messages">
      <div v-if="messages.length === 0" class="empty-chat">
        <p>Commencez à discuter avec InfoliA</p>
      </div>
      
      <div v-for="message in messages" :key="message.id" 
           :class="['message', message.sender === 'user' ? 'user-message' : 'bot-message']">
        <div class="message-content">
          <p>{{ message.text }}</p>
        </div>
        <div class="message-timestamp">{{ message.timestamp }}</div>
      </div>
    </div>
    
    <div class="chat-input">
      <div class="field has-addons">
        <div class="control is-expanded">
          <input 
            class="input" 
            type="text" 
            placeholder="Tapez votre message..." 
            v-model="newMessage"
            @keyup.enter="sendMessage"
          >
        </div>
        <div class="control">
          <button class="button is-primary" @click="sendMessage">
            <span class="icon">
              <i class="fas fa-paper-plane"></i>
            </span>
            <span>Envoyer</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 7rem);
  max-width: 900px;
  margin: 0 auto;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  background-color: #181818;
}

.chat-header {
  padding: 1rem;
  border-bottom: 1px solid #80e7c9;
  text-align: center;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.empty-chat {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #161414;
}

.message {
  max-width: 70%;
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  position: relative;
  color: #000000;
}

.user-message {
  align-self: flex-end;
  background-color: #7cff77f2;
  border-bottom-right-radius: 0.25rem;
}

.bot-message {
  align-self: flex-start;
  background-color: #80e7c9;
  color: #363636;
  border-bottom-left-radius: 0.25rem;
}

.message-content {
  margin-bottom: 0.25rem;
}

.message-timestamp {
  font-size: 0.7rem;
  opacity: 0.7;
  text-align: right;
}

.chat-input {
  padding: 1rem;
  border-top: 1px solid #80e7c9;
}

/* Responsive design */
@media screen and (max-width: 768px) {
  .message {
    max-width: 85%;
  }
  
  .chat-container {
    height: calc(100vh - 6rem);
    border-radius: 0;
  }
}
</style>

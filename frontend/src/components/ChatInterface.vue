<template>
  <div class="chat-interface">
    <!-- Header avec informations sur la conversation -->
    <div class="chat-header">
      <div class="chat-info">
        <h2 class="chat-title">{{ chatStore.currentChat?.name || 'Chat' }}</h2>
        <span v-if="chatStore.currentChat?.document" class="chat-document">
          <i class="fa-solid fa-file-alt mr-1"></i>
          {{ chatStore.currentChat.document }}
        </span>
      </div>
      <div class="chat-actions">
        <button 
          class="button is-primary is-small"
          @click="$emit('new-conversation')"
        >
          <span class="icon">
            ←
          </span>
          <span>Revenir aux conversations</span>
        </button>
      </div>
    </div>

    <!-- Zone des messages -->
    <div class="message-container" ref="messageContainer">
      <div v-if="chatStore.isLoading" class="loading-messages">
        <div class="loading-spinner"></div>
        <p>Chargement des messages...</p>
      </div>
      
      <div v-else-if="!chatStore.currentMessages.length" class="no-messages">
        <p>Aucun message dans cette conversation. Envoyez le premier message !</p>
      </div>

      <div v-else class="messages">
        <div 
          v-for="(message, index) in chatStore.currentMessages" 
          :key="index"
          class="message-item"
          :class="[
            'message-' + message.role,
            { 'is-thinking': message.thinking }
          ]"
        >
          <div class="message-header">
            <span class="message-sender">{{ getSenderLabel(message.role) }}</span>
            <span class="message-time">{{ formatDate(message.timestamp) }}</span>
          </div>
          <div class="message-content" v-html="formatContent(message.content)"></div>
        </div>
      </div>
    </div>

    <!-- Zone de saisie du message -->
    <div class="message-input-container">
      <div class="thinking-indicator" v-if="isWaitingForResponse">
        <div class="thinking-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <span class="thinking-text">Le modèle réfléchit...</span>
      </div>
      <div class="input-wrapper">
        <textarea 
          class="message-input"
          placeholder="Posez votre question..."
          v-model="newMessage"
          @keydown.enter.exact.prevent="sendMessage"
          @keydown.ctrl.enter="newMessage += '\n'"
          :disabled="isWaitingForResponse"
          ref="messageInput"
        ></textarea>
        <button 
          class="send-button"
          @click="sendMessage"
          :disabled="!newMessage.trim() || isWaitingForResponse"
        >
          <i class="fa-solid fa-paper-plane"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick, computed } from 'vue'
import { useChatStore } from '../stores/chatStore'
import authState from '../stores/auth'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

// Store Pinia
const chatStore = useChatStore()

// Émetteurs d'événements
const emit = defineEmits(['new-conversation'])

// État local
const newMessage = ref('')
const isWaitingForResponse = ref(false)
const messageContainer = ref(null)
const messageInput = ref(null)

// Configuration de marked pour les mêmes fonctionnalités que showdown
marked.setOptions({
  breaks: true,
  gfm: true,
  tables: true
})

// Fonction d'envoi de message
const sendMessage = async () => {
  if (!newMessage.value.trim() || isWaitingForResponse.value) return
  
  // Vérifier si un chat est sélectionné
  if (!chatStore.selectedChatId) {
    console.error('Aucune conversation sélectionnée pour envoyer le message')
    return
  }
  
  // Créer le message utilisateur
  const userMessage = {
    role: 'user',
    content: newMessage.value,
    timestamp: new Date().toISOString(),
  }
  
  // Ajouter le message à la conversation
  chatStore.addMessage(chatStore.selectedChatId, userMessage)
  
  // Réinitialiser la zone de saisie
  newMessage.value = ''
  
  // Faire défiler jusqu'au dernier message
  await nextTick()
  scrollToBottom()
  
  // Activer l'indicateur d'attente
  isWaitingForResponse.value = true
  
  try {
    // Appeler l'API pour obtenir une réponse
    const apiUrl = `/chat/send_message/`
    
    // Log pour déboguer l'ID du chat
    console.log('Envoi de message avec chat_id:', chatStore.selectedChatId, 'type:', typeof chatStore.selectedChatId)
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: userMessage.content,
        pseudo: authState.pseudo,
        chat_id: chatStore.selectedChatId
      }),
    })
    
    if (!response.ok) {
      throw new Error(`Erreur API: ${response.status}`)
    }
    
    const responseData = await response.json()
    
    // Ajouter la réponse à la conversation
    const modelMessage = {
      role: 'assistant',
      content: responseData.response,
      timestamp: new Date().toISOString(),
    }
    
    chatStore.addMessage(chatStore.selectedChatId, modelMessage)
    
    // Faire défiler jusqu'au dernier message
    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error('Erreur lors de l\'envoi du message:', error)
    
    // Ajouter un message d'erreur
    chatStore.addMessage(chatStore.selectedChatId, {
      role: 'system',
      content: `Erreur: Impossible de communiquer avec le modèle. ${error.message}`,
      timestamp: new Date().toISOString(),
    })
  } finally {
    // Désactiver l'indicateur d'attente
    isWaitingForResponse.value = false
    
    // Focus sur l'input
    messageInput.value?.focus()
  }
}

// Formatage du contenu avec Markdown
const formatContent = (content) => {
  if (!content) return ''
  
  try {
    // Utiliser marked au lieu de showdown
    const html = marked(content)
    return DOMPurify.sanitize(html)
  } catch (e) {
    console.error('Error formatting message:', e)
    return content
  }
}

// Défilement automatique vers le bas
const scrollToBottom = () => {
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight
  }
}

// Formatage de la date
const formatDate = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Obtenir le libellé de l'expéditeur
const getSenderLabel = (role) => {
  switch (role) {
    case 'user':
      return authState.pseudo || 'Vous'
    case 'assistant':
      return 'Assistant'
    case 'system':
      return 'Système'
    default:
      return role
  }
}

// Surveiller le changement de conversation sélectionnée
watch(() => chatStore.selectedChatId, async (newChatId, oldChatId) => {
  if (newChatId && newChatId !== oldChatId) {
    // Réinitialiser l'interface
    newMessage.value = ''
    isWaitingForResponse.value = false
    
    // S'assurer que le focus est sur la zone de saisie
    await nextTick()
    messageInput.value?.focus()
    scrollToBottom()
  }
})

// Charger les messages lorsque le composant est monté
onMounted(async () => {
  // S'assurer que les messages du chat actuel sont chargés
  if (chatStore.selectedChatId) {
    chatStore.loadChatMessages(chatStore.selectedChatId)
  }
  
  // Mettre le focus sur l'input de message
  messageInput.value?.focus()
  
  // Défiler vers le bas
  await nextTick()
  scrollToBottom()
})

// Actions à effectuer lors du démontage du composant
onBeforeUnmount(() => {
  // Sauvegarder les messages dans le localStorage
  if (chatStore.selectedChatId) {
    chatStore.saveChatMessagesToStorage()
  }
})
</script>

<style scoped>
.chat-interface {
  display: flex;
  flex-direction: column;
  height: 100%;

}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #f5f5f5;

}

.chat-info {
  display: flex;
  flex-direction: column;
}

.chat-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.chat-document {
  font-size: 0.8rem;
  color: #7a7a7a;
  margin-top: 0.25rem;
}

.chat-actions {
  display: flex;
  gap: 0.5rem;
}

.message-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;

}

.loading-messages, .no-messages {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #7a7a7a;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  margin-bottom: 1rem;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: #3273dc;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message-item {
  padding: 1rem;
  border-radius: 8px;
  max-width: 85%;
  position: relative;
}

.message-user {
  align-self: flex-end;
  background-color: #181818;
  border: 1px solid #11cfb3;
}

.message-assistant {
  align-self: flex-start;
  background-color: #11cfb3;
  border: 1px solid #EEC584 ;
  color: #181818;
}

.message-system {
  align-self: center;
  background-color: #fff3cd;
  border: 1px solid #ffeeba;
  max-width: 95%;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
}

.message-sender {
  font-weight: 600;
}

.message-time {
  color: #7a7a7a;
}

.message-content {
  white-space: pre-wrap;
  word-break: break-word;
}

.message-content :deep(p) {
  margin-bottom: 0.75rem;
}

.message-content :deep(p:last-child) {
  margin-bottom: 0;
}

.message-content :deep(pre) {
  background-color: #f5f5f5;
  padding: 0.75rem;
  border-radius: 4px;
  overflow-x: auto;
  margin: 0.75rem 0;
}

.message-content :deep(code) {
  background-color: #f5f5f5;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: monospace;
}

.message-content :deep(ul), .message-content :deep(ol) {
  margin-left: 1.5rem;
  margin-bottom: 0.75rem;
}

.message-input-container {
  padding: 1rem;
  border-top: 1px solid #f5f5f5;
}

.thinking-indicator {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  color: #7a7a7a;
  font-size: 0.9rem;
}

.thinking-dots {
  display: flex;
  gap: 0.25rem;
  margin-right: 0.5rem;
}

.thinking-dots span {
  width: 8px;
  height: 8px;
  background-color: #3273dc;
  border-radius: 50%;
  display: inline-block;
  animation: pulse 1.5s infinite ease-in-out;
}

.thinking-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.thinking-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.2);
    opacity: 1;
  }
}

.input-wrapper {
  display: flex;
  position: relative;
}

.message-input {
  flex: 1;
  padding: 0.75rem 3rem 0.75rem 0.75rem;
  border: 1px solid #11cfb3;
  border-radius: 4px;
  font-size: 1rem;
  resize: none;
  min-height: 60px;
  max-height: 200px;
  overflow-y: auto;
  line-height: 1.5;
}

.message-input:focus {
  outline: none;
  border-color: #3273dc;
  box-shadow: 0 0 0 1px rgba(50, 115, 220, 0.25);
}

.message-input:disabled {
  cursor: not-allowed;
}

.send-button {
  position: absolute;
  right: 0.5rem;
  bottom: 0.5rem;
  background-color: #11cfb3;
  color: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.send-button:hover {
  background-color: #2366d1;
}

.send-button:disabled {
  background-color: #dbdbdb;
  cursor: not-allowed;
}

.is-thinking {
  opacity: 0.7;
  border-style: dashed;
}

.mr-1 {
  margin-right: 0.25rem;
}
</style>

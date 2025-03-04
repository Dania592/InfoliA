<template>
  <div class="chat-interface" :class="{ updating: isLoading }">
    <ConversationHeader :chatId="chatId" />
    
    <div class="chat-messages">
      <div v-if="messages.length === 0" class="empty-chat">
        <p>Commencez à discuter avec InfoliA sur votre document</p>
        <button class="button is-primary mt-4" @click="openNewConversation">
          <span class="icon">
            <i class="fas fa-plus"></i>
          </span>
          <span>Nouvelle conversation</span>
        </button>
      </div>
      
      <div v-for="message in messages" :key="message.id" 
           :class="['message', message.sender === 'user' ? 'user-message' : 'bot-message']">
        <div class="message-content">
          <p>{{ message.text }}</p>
          <div v-if="message.source" class="message-source">
            Source: {{ message.source }}
          </div>
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
            placeholder="Tapez votre question..." 
            v-model="newMessage"
            @keyup.enter="sendMessage"
            :disabled="!chatId"
          >
        </div>
        <div class="control">
          <button 
            class="button is-primary" 
            @click="sendMessage"
            :disabled="!chatId || isLoading"
            :class="{'is-loading': isLoading}"
          >
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

<script setup>
import { ref, watch, onMounted } from 'vue'
import { defineProps, defineEmits } from 'vue'
import ConversationHeader from './ConversationHeader.vue'
import authState from '../stores/auth'

const props = defineProps({
  chatId: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['new-conversation'])

const messages = ref([])
const newMessage = ref('')
const isLoading = ref(false)

// Surveiller les changements de chatId
watch(() => props.chatId, (newChatId, oldChatId) => {
  console.log('ChatInterface: chatId a changé ->', newChatId, '(ancien:', oldChatId, ')')
  
  if (!newChatId) {
    console.warn('ChatInterface: chatId invalide reçu:', newChatId)
    return
  }
  
  // Convertir en chaîne si ce n'est pas déjà le cas
  const chatIdStr = String(newChatId)
  
  // Réinitialiser les messages lorsqu'on change de chat
  messages.value = []
  
  // Charger l'historique des messages pour ce chat immédiatement
  loadChatHistory(chatIdStr)
}, { immediate: true })

// Charger l'historique des messages
async function loadChatHistory(chatId) {
  try {
    isLoading.value = true
    
    // Vérifier que l'utilisateur est connecté
    if (!authState.isAuthenticated) {
      throw new Error('Vous devez être connecté pour accéder aux messages')
    }
    
    const userId = authState.pseudo
    
    console.log(`Chargement des messages pour le chat ${chatId} (type: ${typeof chatId})`)
    
    // Vérifier si des messages existent déjà dans le localStorage
    const chatMessages = JSON.parse(localStorage.getItem(`chat_messages_${userId}_${chatId}`) || '[]')
    console.log(`${chatMessages.length} messages trouvés dans le localStorage`)
    
    // Récupérer les informations du chat à partir de l'ID
    const conversations = JSON.parse(localStorage.getItem(`conversations_${userId}`) || '[]')
    console.log(`${conversations.length} conversations trouvées dans le localStorage:`, conversations)
    
    // Convertir l'ID en chaîne pour la comparaison
    const chatIdStr = String(chatId)
    const currentChat = conversations.find(chat => String(chat.id) === chatIdStr)
    
    if (!currentChat) {
      console.warn(`Conversation ${chatId} non trouvée dans la liste des conversations`)
      // Essayer de récupérer la conversation par backendId
      const chatByBackendId = conversations.find(chat => String(chat.backendId) === chatIdStr)
      if (chatByBackendId) {
        console.log(`Conversation trouvée par backendId:`, chatByBackendId)
        // Utiliser cet ID à la place
        const chatMessagesByBackendId = JSON.parse(localStorage.getItem(`chat_messages_${userId}_${chatByBackendId.id}`) || '[]')
        if (chatMessagesByBackendId.length > 0) {
          console.log(`${chatMessagesByBackendId.length} messages trouvés avec backendId`)
          messages.value = chatMessagesByBackendId
          return
        }
      }
    } else {
      console.log(`Conversation trouvée:`, currentChat)
    }
    
    if (chatMessages.length === 0) {
      // Ajouter un message de bienvenue si c'est la première fois
      const welcomeMessage = {
        id: Date.now(),
        text: "Bonjour ! Je suis InfoliA, votre assistant IA. Comment puis-je vous aider avec votre document aujourd'hui ?",
        sender: 'bot',
        timestamp: formatDate(new Date().toISOString())
      }
      
      chatMessages.push(welcomeMessage)
      localStorage.setItem(`chat_messages_${userId}_${chatId}`, JSON.stringify(chatMessages))
      console.log('Message de bienvenue ajouté')
    }
    
    messages.value = chatMessages
    console.log('Messages chargés dans le composant:', messages.value)
    
    // Faire défiler vers le bas pour voir les messages
    setTimeout(() => {
      scrollToBottom()
    }, 100)
  } catch (error) {
    console.error('Erreur lors du chargement des messages:', error)
  } finally {
    isLoading.value = false
  }
}

// Envoyer un message
async function sendMessage() {
  if (newMessage.value.trim() === '' || !props.chatId) return
  
  // Vérifier que l'utilisateur est connecté
  if (!authState.isAuthenticated) {
    alert('Vous devez être connecté pour envoyer des messages')
    return
  }
  
  const userId = authState.pseudo
  
  // Ajouter le message de l'utilisateur
  const userMessageText = newMessage.value
  const userMessage = {
    id: Date.now(),
    text: userMessageText,
    sender: 'user',
    timestamp: formatDate(new Date().toISOString())
  }
  
  messages.value.push(userMessage)
  newMessage.value = ''
  
  // Faire défiler vers le bas
  scrollToBottom()
  
  // Envoyer le message au backend
  try {
    isLoading.value = true
    
    // Récupérer les informations du chat à partir de l'ID
    const conversations = JSON.parse(localStorage.getItem(`conversations_${userId}`) || '[]')
    
    // Convertir l'ID en chaîne pour la comparaison
    const chatIdStr = String(props.chatId)
    const currentChat = conversations.find(chat => String(chat.id) === chatIdStr)
    
    if (!currentChat) {
      throw new Error(`Conversation ${props.chatId} non trouvée`)
    }
    
    console.log('Conversation trouvée:', currentChat)
    
    // Utiliser le backendId directement s'il est disponible
    // Sinon, utiliser le nom de la conversation
    const chatName = currentChat.backendId || currentChat.name
    
    console.log('Envoi du message avec:', {
      pseudo: userId,
      chat_name: chatName,
      question: userMessageText
    })
    
    // Appel à l'API backend - format simplifié pour correspondre au backend fonctionnel
    const response = await fetch('/chat/send_message/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        pseudo: userId,
        chat_name: chatName,
        question: userMessageText
      })
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('Erreur de réponse:', errorText)
      try {
        const errorData = JSON.parse(errorText)
        throw new Error(errorData.error || 'Erreur lors de l\'envoi du message')
      } catch (e) {
        throw new Error(`Erreur ${response.status}: ${errorText || response.statusText}`)
      }
    }
    
    let data
    try {
      const responseText = await response.text()
      console.log('Réponse texte:', responseText)
      data = JSON.parse(responseText)
      console.log('Réponse du serveur (parsée):', data)
    } catch (e) {
      console.error('Erreur lors du parsing de la réponse:', e)
      throw new Error('Erreur lors du traitement de la réponse du serveur')
    }
    
    // Adapter le traitement de la réponse au format du backend fonctionnel
    const botMessage = {
      id: Date.now() + 1,
      text: data.response || (data.message ? data.message : "Pas de réponse du serveur"),
      sender: 'bot',
      timestamp: formatDate(new Date().toISOString()),
      // Gestion des sources si elles existent
      source: data.source ? (Array.isArray(data.source) ? data.source.join('\n\n') : data.source) : null
    }
    
    messages.value.push(botMessage)
    
    // Sauvegarder les messages dans le localStorage avec l'ID de l'utilisateur
    localStorage.setItem(`chat_messages_${userId}_${props.chatId}`, JSON.stringify(messages.value))
    
    // Faire défiler vers le bas
    scrollToBottom()
  } catch (error) {
    console.error('Erreur lors de l\'envoi du message:', error)
    
    // Ajouter un message d'erreur
    messages.value.push({
      id: Date.now() + 1,
      text: `Désolé, une erreur s'est produite: ${error.message}`,
      sender: 'bot',
      timestamp: formatDate(new Date().toISOString())
    })
    
    scrollToBottom()
  } finally {
    isLoading.value = false
  }
}

// Ouvrir une nouvelle conversation
function openNewConversation() {
  // Émettre un événement pour informer le parent
  emit('new-conversation')
}

// Faire défiler vers le bas
function scrollToBottom() {
  // Utiliser un délai plus long pour s'assurer que le DOM est mis à jour
  setTimeout(() => {
    const chatContainer = document.querySelector('.chat-messages')
    if (chatContainer) {
      console.log('Défilement vers le bas, hauteur:', chatContainer.scrollHeight)
      chatContainer.scrollTop = chatContainer.scrollHeight
      
      // Double vérification avec un second délai
      setTimeout(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight
      }, 100)
    } else {
      console.warn('Container de chat non trouvé pour le défilement')
    }
  }, 100)
}

// Formater une date
function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.chat-interface {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #fff;
  transition: opacity 0.2s ease;
}

.chat-interface.updating {
  opacity: 0.8;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background-color: #f9f9f9;
}

.empty-chat {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #7a7a7a;
  text-align: center;
  flex-direction: column;
}

.message {
  margin-bottom: 1rem;
  max-width: 80%;
  position: relative;
}

.user-message {
  margin-left: auto;
  background-color: #3273dc;
  color: white;
  border-radius: 18px 18px 0 18px;
}

.bot-message {
  margin-right: auto;
  background-color: #f5f5f5;
  color: #4a4a4a;
  border-radius: 18px 18px 18px 0;
}

.message-content {
  padding: 0.75rem 1rem;
}

.message-content p {
  margin: 0;
  white-space: pre-wrap;
}

.message-source {
  font-size: 0.75rem;
  margin-top: 0.5rem;
  opacity: 0.8;
}

.message-timestamp {
  font-size: 0.7rem;
  text-align: right;
  margin-top: 0.25rem;
  opacity: 0.7;
}

.user-message .message-timestamp {
  color: #f5f5f5;
}

.chat-input {
  padding: 1rem;
  border-top: 1px solid #f5f5f5;
  background-color: #fff;
}
</style>

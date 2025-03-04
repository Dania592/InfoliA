<template>
  <div class="conversation-header">
    <div class="conversation-info">
      <h2 class="conversation-title">{{ conversation ? conversation.name : 'Chargement...' }}</h2>
      <div class="conversation-meta" v-if="conversation">
        <span class="conversation-date">{{ formatDate(conversation.createdAt) }}</span>
        <span class="conversation-id" v-if="conversation.backendId">
          ID: {{ formatBackendId(conversation.backendId) }}
        </span>
      </div>
    </div>
    
    <div class="conversation-document" v-if="conversation && conversation.document">
      <div class="document-info">
        <span class="icon">
          <i class="fas fa-file-alt"></i>
        </span>
        <span class="document-name">{{ conversation.document }}</span>
      </div>
      <button class="button is-small" @click="toggleDocumentInfo">
        <span class="icon">
          <i class="fas" :class="isDocumentInfoVisible ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
        </span>
      </button>
    </div>
    
    <div class="document-details" v-if="isDocumentInfoVisible && conversation && conversation.document">
      <div class="notification is-info is-light">
        <h4 class="title is-6">Document associé</h4>
        <p><strong>Nom:</strong> {{ conversation.document }}</p>
        <p><strong>Ajouté le:</strong> {{ formatDate(conversation.createdAt) }}</p>
        <p v-if="conversation.backendId"><strong>ID Backend:</strong> {{ formatBackendId(conversation.backendId) }}</p>
        <p class="document-description">
          Ce document a été associé à cette conversation et est utilisé comme contexte pour les réponses d'InfoliA.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import authState from '../stores/auth'

// Props
const props = defineProps({
  chatId: {
    type: [Number, String],
    default: null
  }
})

// État local
const conversation = ref(null)
const isDocumentInfoVisible = ref(false)

// Méthodes
const toggleDocumentInfo = () => {
  isDocumentInfoVisible.value = !isDocumentInfoVisible.value
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatBackendId = (backendId) => {
  // Si c'est un ID formaté comme "user_xxx.chat_yyy", l'extraire
  if (backendId && backendId.includes('.chat_')) {
    const parts = backendId.split('.chat_')
    if (parts.length > 1) {
      return parts[1] // Retourner juste le nom du chat
    }
  }
  return backendId
}

// Charger les détails de la conversation
watch(() => props.chatId, (newChatId) => {
  if (newChatId) {
    loadConversationDetails(newChatId)
  } else {
    conversation.value = null
  }
}, { immediate: true })

// Surveiller les changements d'authentification
watch(() => authState.isAuthenticated, () => {
  if (props.chatId) {
    loadConversationDetails(props.chatId)
  }
})

const loadConversationDetails = (chatId) => {
  // Vérifier que l'utilisateur est connecté
  if (!authState.isAuthenticated) {
    conversation.value = null
    return
  }
  
  const userId = authState.pseudo
  
  // Récupérer les conversations depuis le localStorage
  const conversations = JSON.parse(localStorage.getItem(`conversations_${userId}`) || '[]')
  
  // Convertir l'ID en chaîne pour la comparaison
  const chatIdStr = String(chatId)
  
  // Trouver la conversation correspondante
  const foundConversation = conversations.find(conv => String(conv.id) === chatIdStr)
  
  if (foundConversation) {
    conversation.value = foundConversation
  } else {
    conversation.value = null
  }
}
</script>

<style scoped>
.conversation-header {
  padding: 1rem;
  border-bottom: 1px solid #80e7c9;
  background-color: #1a1a1a;
}

.conversation-info {
  margin-bottom: 0.5rem;
}

.conversation-title {
  font-size: 1.5rem;
  margin-bottom: 0.25rem;
  color: #f5f5f5;
}

.conversation-meta {
  display: flex;
  align-items: center;
  font-size: 0.8rem;
  color: #aaa;
  margin-bottom: 0.5rem;
}

.conversation-date {
  margin-right: 1rem;
}

.conversation-id {
  font-family: monospace;
  background-color: #333;
  padding: 2px 6px;
  border-radius: 4px;
  color: #80e7c9;
  font-size: 0.75rem;
}

.conversation-document {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #2a2a2a;
  padding: 0.5rem;
  border-radius: 4px;
}

.document-info {
  display: flex;
  align-items: center;
  color: #f5f5f5;
}

.document-info .icon {
  margin-right: 0.5rem;
  color: #80e7c9;
}

.document-name {
  font-size: 0.9rem;
  max-width: 250px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.document-details {
  margin-top: 0.5rem;
}

.document-description {
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

@media screen and (max-width: 768px) {
  .conversation-header {
    padding: 0.75rem;
  }
  
  .conversation-title {
    font-size: 1.25rem;
  }
  
  .document-name {
    max-width: 150px;
  }
}
</style>

<script setup>
import { ref, watch, onMounted } from 'vue'
import authState from '../stores/auth'
import { useRouter } from 'vue-router'
import ChatInterface from '../components/ChatInterface.vue'
import ConversationList from '../components/ConversationList.vue'
import NewConversation from '../components/NewConversation.vue'

const router = useRouter()
const selectedChatId = ref(null)
const isNewConversationModalActive = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// Rediriger vers la page de connexion si l'utilisateur n'est pas connecté
if (!authState.isAuthenticated) {
  router.push('/login')
}

// Écouter les événements de sélection de chat
const handleChatSelected = (chatId) => {
  if (!chatId) {
    console.warn('ChatView: handleChatSelected appelé avec un ID invalide:', chatId)
    return
  }
  
  console.log('ChatView: handleChatSelected appelé avec ID:', chatId, '(type:', typeof chatId, ')')
  
  // Convertir en chaîne si ce n'est pas déjà le cas
  const chatIdStr = String(chatId)
  
  // Mettre à jour l'état local
  selectedChatId.value = chatIdStr
  
  console.log('ChatView: selectedChatId mis à jour:', selectedChatId.value)
  
  // Sauvegarder le chat sélectionné dans le localStorage avec l'ID de l'utilisateur
  if (authState.isAuthenticated) {
    localStorage.setItem(`selectedChatId_${authState.pseudo}`, chatIdStr)
    console.log('ChatView: ID de chat sauvegardé dans localStorage')
  }
  
  // Forcer une mise à jour du composant
  setTimeout(() => {
    const chatInterface = document.querySelector('.chat-interface')
    if (chatInterface) {
      console.log('ChatView: Interface de chat trouvée, forçage de la mise à jour')
      // Forcer un re-rendu en ajoutant et supprimant une classe
      chatInterface.classList.add('updating')
      setTimeout(() => {
        chatInterface.classList.remove('updating')
      }, 10)
    } else {
      console.warn('ChatView: Interface de chat non trouvée')
    }
  }, 100) // Augmenter le délai pour s'assurer que le DOM est mis à jour
}

// Gérer la sélection d'une conversation depuis la liste
const selectConversation = (conversationId) => {
  handleChatSelected(conversationId)
}

// Gérer la suppression d'une conversation
const handleDeleteConversation = (conversationId) => {
  // Si la conversation supprimée est celle qui est actuellement sélectionnée
  if (selectedChatId.value === conversationId) {
    selectedChatId.value = null
    
    // Supprimer également la référence dans le localStorage
    if (authState.isAuthenticated) {
      localStorage.removeItem(`selectedChatId_${authState.pseudo}`)
    }
    
    // Vérifier s'il y a d'autres conversations disponibles
    if (authState.isAuthenticated) {
      const userId = authState.pseudo
      const conversations = JSON.parse(localStorage.getItem(`conversations_${userId}`) || '[]')
      
      if (conversations.length > 0) {
        // Sélectionner la première conversation disponible
        handleChatSelected(conversations[0].id)
      }
    }
  }
}

// Ouvrir le modal de nouvelle conversation
const openNewConversationModal = () => {
  console.log('ChatView: Ouverture du modal de nouvelle conversation')
  isNewConversationModalActive.value = true
}

// Fermer le modal de nouvelle conversation
const closeNewConversationModal = () => {
  console.log('ChatView: Fermeture du modal de nouvelle conversation')
  isNewConversationModalActive.value = false
}

// Gérer la création d'une nouvelle conversation
const handleConversationCreated = (conversation) => {
  console.log('Nouvelle conversation créée et reçue dans ChatView:', conversation)
  
  // Fermer explicitement le modal
  isNewConversationModalActive.value = false
  
  // Sélectionner le nouveau chat
  handleChatSelected(conversation.id)
  
  // Afficher un message de succès
  successMessage.value = `Conversation "${conversation.name}" créée avec succès!`
  setTimeout(() => {
    successMessage.value = ''
  }, 3000)
  
  console.log('Chat sélectionné avec ID:', conversation.id)
  
  // Forcer un rafraîchissement de la page après un court délai
  // Cela peut aider à résoudre les problèmes de rendu
  setTimeout(() => {
    if (selectedChatId.value) {
      console.log('Forçage du rafraîchissement de l\'interface de chat')
      // On peut forcer un re-rendu en modifiant temporairement la valeur
      const currentId = selectedChatId.value
      selectedChatId.value = null
      setTimeout(() => {
        selectedChatId.value = currentId
      }, 50)
    }
  }, 500)
}

// Surveiller les changements d'authentification
watch(() => authState.isAuthenticated, (isAuthenticated) => {
  if (!isAuthenticated) {
    // Si l'utilisateur se déconnecte, réinitialiser la sélection
    selectedChatId.value = null
  } else {
    // Si l'utilisateur se connecte, charger sa dernière conversation sélectionnée
    const userId = authState.pseudo
    const savedChatId = localStorage.getItem(`selectedChatId_${userId}`)
    if (savedChatId) {
      selectedChatId.value = savedChatId
    }
  }
})

// Charger le chat sélectionné précédemment
onMounted(() => {
  // Écouter les événements de sélection de chat
  window.addEventListener('chat-selected', (event) => {
    console.log('ChatView: Événement chat-selected reçu avec détail:', event.detail)
    if (event.detail && event.detail.chatId) {
      handleChatSelected(event.detail.chatId)
    }
  })
  
  // Charger le chat précédemment sélectionné
  if (authState.isAuthenticated) {
    const userId = authState.pseudo
    const savedChatId = localStorage.getItem(`selectedChatId_${userId}`)
    
    if (savedChatId) {
      console.log('ChatView: Chat précédemment sélectionné trouvé:', savedChatId)
      // Utiliser un délai pour s'assurer que les conversations sont chargées
      setTimeout(() => {
        handleChatSelected(savedChatId)
      }, 300)
    }
  }
})
</script>

<template>
  <div class="chat-page">
    <!-- Messages d'erreur ou de succès -->
    <div v-if="errorMessage" class="notification is-danger is-light global-notification">
      {{ errorMessage }}
      <button class="delete" @click="errorMessage = ''"></button>
    </div>
    <div v-if="successMessage" class="notification is-success is-light global-notification">
      {{ successMessage }}
      <button class="delete" @click="successMessage = ''"></button>
    </div>
    
    <!-- Sidebar pour la liste des conversations -->
    <div class="conversation-sidebar">
      <ConversationList 
        :selectedConversationId="selectedChatId"
        @select-conversation="selectConversation"
        @new-conversation="openNewConversationModal"
        @delete-conversation="handleDeleteConversation"
      />
    </div>
    
    <!-- Interface de chat -->
    <div class="chat-content">
      <div v-if="selectedChatId" class="chat-interface-wrapper">
        <!-- Utiliser le composant ChatInterface avec une clé unique pour forcer le re-rendu -->
        <ChatInterface 
          :key="'chat-' + selectedChatId" 
          :chatId="selectedChatId" 
          @new-conversation="openNewConversationModal" 
        />
      </div>
      <div v-else class="no-chat-selected">
        <div class="message">
          <h2 class="title is-4">Bienvenue dans le chat InfoliA</h2>
          <p class="subtitle is-6">Sélectionnez une conversation dans le menu latéral ou créez-en une nouvelle.</p>
          <button class="button is-primary mt-4" @click="openNewConversationModal">
            <span class="icon">
              <i class="fas fa-plus"></i>
            </span>
            <span>Nouvelle conversation</span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Modal pour la nouvelle conversation -->
    <NewConversation 
      v-if="isNewConversationModalActive"
      :isActive="isNewConversationModalActive"
      @close="closeNewConversationModal"
      @conversation-created="handleConversationCreated"
    />
  </div>
</template>

<style scoped>
.chat-page {
  height: calc(100vh - 7rem);
  display: flex;
  position: relative;
}

.global-notification {
  position: fixed;
  top: 4rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  min-width: 300px;
  max-width: 80%;
  text-align: center;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
}

.conversation-sidebar {
  width: 300px;
  border-right: 1px solid #f5f5f5;
  height: 100%;
  overflow-y: auto;
  background-color: #fafafa;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-interface-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin: 1rem;
}

.no-chat-selected {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}

.no-chat-selected .message {
  text-align: center;
  max-width: 500px;
  padding: 2rem;
  border-radius: 8px;
  background-color: #f5f5f5;
}

@media screen and (max-width: 768px) {
  .chat-page {
    flex-direction: column;
    height: calc(100vh - 6rem);
  }
  
  .conversation-sidebar {
    width: 100%;
    height: auto;
    max-height: 40vh;
    border-right: none;
    border-bottom: 1px solid #f5f5f5;
  }
  
  .chat-content {
    height: 60vh;
  }
  
  .chat-interface-wrapper {
    margin: 0.5rem;
  }
}
</style>

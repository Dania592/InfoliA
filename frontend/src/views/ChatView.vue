<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import authState from '../stores/auth'
import { useChatStore } from '../stores/chatStore'
import { useRouter } from 'vue-router'
import ChatInterface from '../components/ChatInterface.vue'
import ConversationList from '../components/ConversationList.vue'
import NewConversation from '../components/NewConversation.vue'

const router = useRouter()
const chatStore = useChatStore()
const isNewConversationModalActive = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// Rediriger vers la page de connexion si l'utilisateur n'est pas connecté
if (!authState.isAuthenticated) {
  router.push('/login')
}

// Charger les données depuis le localStorage au montage
onMounted(() => {
  if (authState.isAuthenticated) {
    chatStore.loadFromLocalStorage(authState.pseudo)
  }
})

// Fermer le chat quand on quitte la page
onBeforeUnmount(() => {
  chatStore.resetSelectedChat()
})

// Surveiller les changements de route
watch(() => router.currentRoute.value.path, (path) => {
  if (path !== '/chat') {
    chatStore.resetSelectedChat()
  }
})

// Gérer la sélection d'une conversation depuis la liste
const selectConversation = (conversationId) => {
  chatStore.selectChat(conversationId)
}

// Désélectionner la conversation actuelle
const deselectConversation = () => {
  chatStore.selectChat(null)
}

// Gérer la suppression d'une conversation
const handleDeleteConversation = (conversationId) => {
  chatStore.removeConversation(conversationId)
}

// Ouvrir le modal de nouvelle conversation
const openNewConversationModal = () => {
  isNewConversationModalActive.value = true
}

// Fermer le modal de nouvelle conversation
const closeNewConversationModal = () => {
  isNewConversationModalActive.value = false
}

// Gérer la création d'une nouvelle conversation
const handleConversationCreated = (conversation) => {
  // Fermer explicitement le modal avant toute autre action
  isNewConversationModalActive.value = false
  
  // Ajouter la conversation au store et la sélectionner
  chatStore.addConversation(conversation)
  chatStore.selectChat(conversation.id)
  
  // Afficher un message de succès
  successMessage.value = `Conversation "${conversation.name}" créée avec succès!`
  setTimeout(() => {
    successMessage.value = ''
  }, 3000)
}

// Surveiller les changements d'authentification
watch(() => authState.isAuthenticated, (isAuthenticated) => {
  if (!isAuthenticated) {
    // Si l'utilisateur se déconnecte, réinitialiser le store
    chatStore.resetState()
  } else {
    // Si l'utilisateur se connecte, charger ses données
    chatStore.loadFromLocalStorage(authState.pseudo)
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
    <div class="conversation-sidebar" v-if="chatStore.conversations.length > 0 && !chatStore.selectedChatId">
      <ConversationList 
        @select-conversation="selectConversation"
        @new-conversation="openNewConversationModal"
        @delete-conversation="handleDeleteConversation"
      />
    </div>
    
    <!-- Interface de chat -->
    <div class="chat-content" v-else-if="chatStore.selectedChatId">
      <div class="chat-interface-wrapper">
        <ChatInterface @new-conversation="deselectConversation" />
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

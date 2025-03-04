<template>
  <div class="conversation-list">
    <div v-if="conversations.length === 0" class="no-conversations">
      <p>Vous n'avez pas encore de conversations.</p>
      <button class="button is-primary mt-3" @click="$emit('new-conversation')">
        <span class="icon">
          <i class="fas fa-plus"></i>
        </span>
        <span>Nouvelle conversation</span>
      </button>
    </div>
    
    <div v-else class="conversations">
      <div class="field has-addons mb-4">
        <div class="control is-expanded">
          <input 
            class="input" 
            type="text" 
            placeholder="Rechercher une conversation..." 
            v-model="searchQuery"
          >
        </div>
        <div class="control">
          <button class="button is-primary" @click="$emit('new-conversation')">
            <span class="icon">
              <i class="fas fa-plus"></i>
            </span>
          </button>
        </div>
      </div>
      
      <div 
        v-for="conversation in filteredConversations" 
        :key="conversation.id"
        class="conversation-item"
        :class="{ 'is-active': String(selectedConversationId) === String(conversation.id) }"
      >
        <div class="conversation-item-content" @click="selectConversation(conversation)">
          <div class="conversation-info">
            <h3 class="conversation-name">{{ conversation.name }}</h3>
            <p class="conversation-date">{{ formatDate(conversation.createdAt) }}</p>
          </div>
          <div class="conversation-document" v-if="conversation.document">
            <span class="icon">
              <i class="fas fa-file-alt"></i>
            </span>
            <span class="document-name">{{ truncateFilename(conversation.document) }}</span>
          </div>
        </div>
        <button 
          class="delete-button" 
          @click.stop="confirmDeleteConversation(conversation.id)"
          title="Supprimer cette conversation"
        >
          <span class="icon is-small">
            <i class="fas fa-times"></i>
          </span>
        </button>
      </div>
    </div>
    
    <!-- Modal de confirmation de suppression -->
    <div class="modal" :class="{'is-active': deleteModalActive}">
      <div class="modal-background" @click="cancelDelete"></div>
      <div class="modal-card">
        <header class="modal-card-head">
          <p class="modal-card-title">Confirmer la suppression</p>
          <button class="delete" aria-label="close" @click="cancelDelete"></button>
        </header>
        <section class="modal-card-body">
          <p>Êtes-vous sûr de vouloir supprimer cette conversation ? Cette action est irréversible.</p>
        </section>
        <footer class="modal-card-foot">
          <button class="button is-danger" @click="deleteConversation">Supprimer</button>
          <button class="button" @click="cancelDelete">Annuler</button>
        </footer>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import authState from '../stores/auth'
import { useRouter } from 'vue-router'

// Router
const router = useRouter()

// Props
const props = defineProps({
  selectedConversationId: {
    type: Number,
    default: null
  }
})

// Emits
const emit = defineEmits(['select-conversation', 'new-conversation', 'delete-conversation'])

// État local
const conversations = ref([])
const searchQuery = ref('')
const deleteModalActive = ref(false)
const conversationToDelete = ref(null)

// Computed properties
const filteredConversations = computed(() => {
  if (!searchQuery.value) return conversations.value
  
  const query = searchQuery.value.toLowerCase()
  return conversations.value.filter(conv => 
    conv.name.toLowerCase().includes(query) || 
    (conv.document && conv.document.toLowerCase().includes(query))
  )
})

// Méthodes
const selectConversation = (conversation) => {
  console.log('ConversationList: Sélection de la conversation:', conversation)
  // Sauvegarder l'ID de la conversation sélectionnée
  if (authState.isAuthenticated) {
    const userId = authState.pseudo
    localStorage.setItem(`selectedChatId_${userId}`, conversation.id)
  }
  
  // Émettre l'événement pour informer le parent
  emit('select-conversation', conversation.id)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

const truncateFilename = (filename) => {
  if (filename.length > 20) {
    return filename.substring(0, 17) + '...'
  }
  return filename
}

const confirmDeleteConversation = (conversationId) => {
  conversationToDelete.value = conversationId
  deleteModalActive.value = true
}

const cancelDelete = () => {
  deleteModalActive.value = false
  conversationToDelete.value = null
}

const deleteConversation = () => {
  if (!conversationToDelete.value) return
  
  // Supprimer la conversation du localStorage
  const updatedConversations = conversations.value.filter(
    conv => conv.id !== conversationToDelete.value
  )
  
  // Mettre à jour le localStorage
  const userId = authState.pseudo
  localStorage.setItem(`conversations_${userId}`, JSON.stringify(updatedConversations))
  
  // Supprimer également les messages associés
  localStorage.removeItem(`chat_messages_${conversationToDelete.value}`)
  
  // Mettre à jour l'état local
  conversations.value = updatedConversations
  
  // Émettre un événement pour informer le parent
  emit('delete-conversation', conversationToDelete.value)
  
  // Fermer le modal
  deleteModalActive.value = false
  conversationToDelete.value = null
}

// Charger les conversations depuis le localStorage
const loadConversations = () => {
  const userId = authState.pseudo
  const storedConversations = localStorage.getItem(`conversations_${userId}`)
  
  if (storedConversations) {
    conversations.value = JSON.parse(storedConversations)
  } else {
    conversations.value = []
  }
}

// Surveiller les changements d'authentification
watch(() => authState.isAuthenticated, (isAuthenticated) => {
  if (isAuthenticated) {
    loadConversations()
  } else {
    conversations.value = []
  }
}, { immediate: true })

// Charger les conversations au montage
onMounted(() => {
  if (authState.isAuthenticated) {
    loadConversations()
  }
})
</script>

<style scoped>
.conversation-list {
  height: 100%;
  overflow-y: auto;
  padding: 1rem;
}

.no-conversations {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: #7a7a7a;
}

.mt-3 {
  margin-top: 1rem;
}

.mb-4 {
  margin-bottom: 1.5rem;
}

.conversation-item {
  padding: 0.5rem;
  border-radius: 8px;
  margin-bottom: 0.75rem;
  cursor: pointer;
  border: 1px solid #f5f5f5;
  transition: all 0.2s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.conversation-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.conversation-item.is-active {
  background-color: #f0f9ff;
  border-color: #3273dc;
  box-shadow: 0 2px 5px rgba(50, 115, 220, 0.1);
}

.conversation-item-content {
  flex: 1;
  padding: 0.5rem;
}

.conversation-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.conversation-name {
  font-weight: 600;
  font-size: 1rem;
  margin: 0;
}

.conversation-date {
  font-size: 0.75rem;
  color: #7a7a7a;
  margin: 0;
}

.conversation-document {
  display: flex;
  align-items: center;
  font-size: 0.85rem;
  color: #7a7a7a;
}

.document-name {
  margin-left: 0.5rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.delete-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: none;
  background-color: transparent;
  color: #7a7a7a;
  cursor: pointer;
  opacity: 0.5;
  transition: all 0.2s ease;
}

.delete-button:hover {
  opacity: 1;
  color: #ff3860;
  background-color: rgba(255, 56, 96, 0.1);
}

.conversation-item:hover .delete-button {
  opacity: 0.8;
}
</style>

<template>
  <div class="conversation-list">
    <div v-if="chatStore.conversations.length === 0" class="no-conversations">
      <p>Vous n'avez pas encore de conversations.</p>
      <button class="button is-primary mt-3" @click="$emit('new-conversation')">
        <span class="icon">
          <i class="fa-solid fa-plus"></i>
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
              <i class="fa-solid fa-plus"></i>
            </span>
          </button>
        </div>
      </div>
      
      <div 
        v-for="conversation in filteredConversations" 
        :key="conversation.id"
        class="conversation-item"
        :class="{ 'is-active': String(chatStore.selectedChatId) === String(conversation.id) }"
      >
        <div class="conversation-item-content" @click="selectConversation(conversation)">
          <div class="conversation-info">
            <h3 class="conversation-name">{{ conversation.name }}</h3>
            <p class="conversation-date">{{ formatDate(conversation.createdAt) }}</p>
          </div>
          <div class="conversation-document" v-if="conversation.document">
            <span class="icon">
              <i class="fa-solid fa-file-alt"></i>
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
            ✕
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
import { ref, computed, watch } from 'vue'
import { useChatStore } from '../stores/chatStore'
import { useRouter } from 'vue-router'

// Router
const router = useRouter()
const chatStore = useChatStore()

// Emits
const emit = defineEmits(['select-conversation', 'new-conversation', 'delete-conversation'])

// État local
const searchQuery = ref('')
const deleteModalActive = ref(false)
const conversationToDelete = ref(null)

// Computed properties
const filteredConversations = computed(() => {
  if (!searchQuery.value) return chatStore.conversations
  
  const query = searchQuery.value.toLowerCase()
  return chatStore.conversations.filter(conv => 
    conv.name.toLowerCase().includes(query) || 
    (conv.document && conv.document.toLowerCase().includes(query))
  )
})

// Méthodes
const selectConversation = (conversation) => {
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
  
  // Émettre un événement pour informer le parent
  emit('delete-conversation', conversationToDelete.value)
  
  // Fermer le modal
  deleteModalActive.value = false
  conversationToDelete.value = null
}

// Surveiller les changements de route
watch(() => router.currentRoute.value.path, (path) => {
  if (path !== '/chat') {
    // Si nous ne sommes plus sur la route /chat, réinitialiser la sélection
    chatStore.resetSelectedChat()
  }
})
</script>

<style scoped>
.conversation-list {
  padding: 1rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #181818;
  color: #fff;
}

.no-conversations {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: #aaa;
}

.conversations {
  flex: 1;
  overflow-y: auto;
}

.conversation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  border: 1px solid #181818;
  transition: all 0.2s ease;
}

.conversation-item:hover {
  border-color: #11cfb3;
}

.conversation-item.is-active {
  border-color: #11cfb3;
  background-color: rgba(17, 207, 179, 0.1);
}

.conversation-item-content {
  flex: 1;
  cursor: pointer;
  margin-right: 0.5rem;
}

.conversation-info {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.conversation-name {
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: #fff;
}

.conversation-date {
  font-size: 0.75rem;
  color: #aaa;
}

.conversation-document {
  display: flex;
  align-items: center;
  font-size: 0.8rem;
  color: #ccc;
  margin-top: 0.25rem;
}

.conversation-document .icon {
  margin-right: 0.25rem;
  color: #11cfb3;
}

.delete-button {
  background: transparent;
  border: none;
  color: #aaa;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.delete-button:hover {
  background-color: #f14668;
  color: white;
}

.input {
  background-color: transparent;
  border-color: #11cfb3;
  color: inherit;
}

.input:focus {
  border-color: #11cfb3;
  box-shadow: 0 0 0 0.125em rgba(17, 207, 179, 0.25);
}

.input::placeholder {
  color: #888;
}

.button.is-primary {
  background-color: #11cfb3;
  border-color: transparent;
}

.button.is-primary:hover {
  background-color: #0fb9a0;
}

.modal-card-head,
.modal-card-body,
.modal-card-foot {
  background-color: #232323;
  color: #fff;
  border-color: #333;
}

.modal-card-title {
  color: #fff;
}

.button:not(.is-primary):not(.is-danger) {
  background-color: #333;
  color: #fff;
  border-color: #444;
}

.button:not(.is-primary):not(.is-danger):hover {
  background-color: #444;
  color: #fff;
}
</style>

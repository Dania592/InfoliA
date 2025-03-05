<template>
  <div class="chat-manager">
    <div class="chat-list-container" v-if="!chatViewMode">
      <h2 class="subtitle">Mes conversations</h2>
      
      <!-- Bouton pour créer une nouvelle conversation -->
      <div class="new-chat-button mb-4">
        <button class="button is-primary is-fullwidth" @click="showNewConversationModal = true">
          <span class="icon">
            <i class="fas fa-plus"></i>
          </span>
          <span>Nouvelle conversation</span>
        </button>
      </div>
      
      <!-- Liste des chats existants -->
      <div class="chat-list mt-5">
        <div v-if="isLoadingChats" class="has-text-centered py-4">
          <span class="icon is-large">
            <i class="fas fa-spinner fa-pulse"></i>
          </span>
          <p>Chargement des conversations...</p>
        </div>
        
        <div v-else-if="chats.length === 0" class="has-text-centered py-4">
          <p>Vous n'avez pas encore de conversations</p>
        </div>
        
        <div 
          v-else
          v-for="chat in chats" 
          :key="chat.id_chat" 
          class="chat-item"
          :class="{'is-active': selectedChatId === chat.id_chat}"
          @click="selectChat(chat)"
        >
          <div class="chat-item-content">
            <h4 class="is-size-5">{{ chat.nom_chat }}</h4>
            <p class="is-size-7">{{ formatDate(chat.created_at) }}</p>
            <p class="is-size-7">{{ chat.documents.length }} document(s)</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="chat-detail-container full-width" v-if="chatViewMode && selectedChat">
      <div class="chat-header">
        <div class="header-left">
          <button class="button is-primary mr-2" @click="showChatList">
            <span class="icon">
              <i class="fas fa-arrow-left"></i>
            </span>
            <span>Revenir aux conversations</span>
          </button>
          <h2 class="subtitle">{{ selectedChat ? selectedChat.nom_chat : '' }}</h2>
        </div>
        
        <div class="header-actions">
          <button class="button is-small" @click="showUploadModal = true">
            <span class="icon">
              <i class="fas fa-file-upload"></i>
            </span>
            <span>Ajouter un document</span>
          </button>
        </div>
      </div>
      
      <div class="documents-list">
        <h3 class="is-size-6 mb-2">Documents</h3>
        <div class="document-item" v-for="doc in selectedChat ? selectedChat.documents : []" :key="doc.id_document">
          <span class="icon">
            <i class="fas fa-file-pdf"></i>
          </span>
          <span>{{ doc.nom_document }}</span>
        </div>
        <p v-if="selectedChat && selectedChat.documents.length === 0" class="no-documents">Aucun document</p>
      </div>
      
      <!-- Ici, on pourrait intégrer le composant de chat existant -->
      <ChatInterface @new-conversation="showChatList" />
    </div>
    
    <!-- Modal pour ajouter un document à un chat existant -->
    <div class="modal" :class="{'is-active': showUploadModal}">
      <div class="modal-background" @click="showUploadModal = false"></div>
      <div class="modal-card">
        <header class="modal-card-head">
          <p class="modal-card-title">Ajouter un document</p>
          <button class="delete" aria-label="close" @click="showUploadModal = false"></button>
        </header>
        <section class="modal-card-body">
          <div class="field">
            <label class="label">Document PDF</label>
            <div class="file has-name is-fullwidth">
              <label class="file-label">
                <input class="file-input" type="file" accept=".pdf,.doc,.docx,.txt" @change="handleFileSelect">
                <span class="file-cta">
                  <span class="file-icon">
                    <i class="fas fa-upload"></i>
                  </span>
                  <span class="file-label">
                    Choisir un fichier
                  </span>
                </span>
                <span class="file-name" v-if="additionalFile">
                  {{ additionalFile.name }}
                </span>
                <span class="file-name" v-else>
                  Aucun fichier sélectionné
                </span>
              </label>
            </div>
          </div>
        </section>
        <footer class="modal-card-foot">
          <button 
            class="button is-success" 
            :disabled="!additionalFile"
            @click="handleUploadSubmit"
            :class="{'is-loading': isUploadingDocument}"
          >
            Ajouter
          </button>
          <button class="button" @click="showUploadModal = false">Annuler</button>
        </footer>
      </div>
    </div>
    
    <!-- Composant modal de nouvelle conversation -->
    <NewConversation 
      :is-active="showNewConversationModal" 
      @close="showNewConversationModal = false" 
      @conversation-created="createChat"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import authState from '../stores/auth'
import NewConversation from './NewConversation.vue'
import { useChatStore } from '../stores/chatStore'
import ChatInterface from './ChatInterface.vue'

export default {
  components: {
    NewConversation,
    ChatInterface
  },
  data() {
    return {
      chats: [],
      selectedChatId: null,
      selectedChat: null,
      additionalFile: null,
      isLoadingChats: true,
      isUploadingDocument: false,
      showUploadModal: false,
      showNewConversationModal: false,
      chatViewMode: false,
      chatStore: useChatStore(),
      routeWatcher: null
    }
  },
  mounted() {
    this.fetchChats()
    
    // Surveiller les changements de route
    this.routeWatcher = this.$router.afterEach((to) => {
      if (to.path !== '/chat') {
        this.showChatList()
        this.selectedChatId = null
        this.selectedChat = null
        this.chatViewMode = false
      }
    })
  },
  unmounted() {
    // Nettoyer le watcher de route lors de la destruction du composant
    if (this.routeWatcher) {
      this.routeWatcher()
    }
  },
  methods: {
    async fetchChats() {
      this.isLoadingChats = true
      
      try {
        const response = await axios.get('/api/chats/', {
          headers: {
            'Authorization': `Bearer ${authState.accessToken}`
          }
        })
        console.log('Données reçues:', response.data)
        this.chats = response.data
        this.isLoadingChats = false
      } catch (error) {
        console.error('Erreur lors de la récupération des chats:', error)
        this.isLoadingChats = false
      }
    },
    async createChat(chatName) {
      try {
        const response = await axios.post('/api/chats/', {
          nom_chat: chatName
        }, {
          headers: {
            'Authorization': `Bearer ${authState.accessToken}`
          }
        })
        
        console.log('Chat créé:', response.data)
        
        // Ajouter le nouveau chat à la liste
        this.chats.push(response.data)
        
        // Sélectionner le nouveau chat automatiquement
        this.selectChat(response.data)
        
        // Fermer le modal
        this.showNewConversationModal = false
        
        return response.data
      } catch (error) {
        console.error('Erreur lors de la création du chat:', error)
        return null
      }
    },
    async uploadDocument(chatId, file) {
      this.isUploadingDocument = true
      
      try {
        const formData = new FormData()
        formData.append('file', file)
        
        const response = await axios.post(`/api/chats/${chatId}/documents/`, formData, {
          headers: {
            'Authorization': `Bearer ${authState.accessToken}`,
            'Content-Type': 'multipart/form-data'
          }
        })
        
        console.log('Document téléversé:', response.data)
        
        // Mettre à jour la liste des documents du chat
        if (this.selectedChat && this.selectedChat.id_chat === chatId) {
          if (!this.selectedChat.documents) {
            this.selectedChat.documents = []
          }
          this.selectedChat.documents.push(response.data)
        }
        
        this.isUploadingDocument = false
        this.showUploadModal = false
        
        return response.data
      } catch (error) {
        console.error('Erreur lors du téléversement du document:', error)
        this.isUploadingDocument = false
        return null
      }
    },
    async handleUploadSubmit() {
      if (!this.additionalFile) {
        console.error('Aucun fichier sélectionné')
        return
      }
      
      if (!this.selectedChat) {
        console.error('Aucun chat sélectionné')
        return
      }
      
      await this.uploadDocument(this.selectedChat.id_chat, this.additionalFile)
      
      // Réinitialiser le fichier sélectionné
      this.additionalFile = null
    },
    handleFileSelect(event) {
      this.additionalFile = event.target.files[0]
    },
    selectChat(chat) {
      console.log('Chat sélectionné:', chat)
      console.log('ID du chat:', chat.id_chat, 'type:', typeof chat.id_chat)
      
      this.selectedChatId = chat.id_chat
      this.selectedChat = chat
      
      // Basculer en mode vue de chat
      this.chatViewMode = true
      
      // Mettre à jour le store Pinia
      this.chatStore.selectChat(chat.id_chat)
      console.log('ID stocké dans Pinia:', this.chatStore.selectedChatId)
      
      // Émettre un événement personnalisé pour informer ChatView
      const event = new CustomEvent('chat-selected', {
        detail: { chatId: chat.id_chat, chatName: chat.nom_chat }
      })
      window.dispatchEvent(event)
    },
    showChatList() {
      this.chatViewMode = false
      // On ne désélectionne pas le chat pour conserver l'état en cas de retour
    },
    formatDate(dateString) {
      if (!dateString) return 'Date inconnue'
      
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date)
    }
  }
}
</script>

<style>
.chat-manager {
  display: flex;
  height: calc(100vh - 7rem);
  max-width: 1200px;
  margin: 0 auto;
  gap: 1rem;
}

.chat-list-container {
  width: 300px;
  border-right: 1px solid #163b31;
  padding: 1rem;
  overflow-y: auto;
  transition: width 0.3s ease, opacity 0.3s ease;
}

.chat-detail-container {
  flex-grow: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.chat-detail-container.full-width {
  width: 100%;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  border-bottom: 1px solid #11cfb3;
  padding-bottom: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-left .subtitle {
  margin-bottom: 0;
  margin-left: 1rem;
}

.header-actions {
  display: flex;
  align-items: center;
}

.chat-item {
  padding: 0.75rem;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 0.5rem;
  border: 1px solid #eee;
  transition: all 0.2s ease;
}

.chat-item:hover {
  opacity: 0.8;
}

.chat-item.is-active {
  border-color: #80e7c9;
}

.mb-4 {
  margin-bottom: 1rem;
}

.mt-3 {
  margin-top: 0.75rem;
}

.mt-5 {
  margin-top: 1.25rem;
}

.ml-3 {
  margin-left: 0.75rem;
}

.mr-2 {
  margin-right: 0.5rem;
}

.documents-list {
  margin-bottom: 1rem;
}

.document-item {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  padding: 0.25rem;
}

.document-item .icon {
  margin-right: 0.5rem;
  color: #ff5722;
}

.no-documents {
  font-style: italic;
  color: #888;
  padding: 0.5rem 0;
}

.chat-content {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.chat-interface-wrapper {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

/* Responsive design */
@media screen and (max-width: 768px) {
  .chat-manager {
    flex-direction: column;
    height: auto;
  }
  
  .chat-list-container {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #80e7c9;
  }
}
</style>

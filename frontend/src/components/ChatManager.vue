<template>
  <div class="chat-manager">
    <div class="chat-list-container">
      <h2 class="subtitle">Mes conversations</h2>
      
      <!-- Formulaire pour créer un nouveau chat -->
      <div class="new-chat-form">
        <h3 class="is-size-5 mb-2">Nouvelle conversation</h3>
        <div class="field">
          <label class="label">Nom de la conversation</label>
          <div class="control">
            <input 
              class="input" 
              type="text" 
              placeholder="Entrez un nom" 
              v-model="newChatName"
            >
          </div>
        </div>
        
        <div class="field">
          <label class="label">Document PDF</label>
          <div class="file has-name is-fullwidth">
            <label class="file-label">
              <input class="file-input" type="file" accept=".pdf" @change="handleFileChange">
              <span class="file-cta">
                <span class="file-icon">
                  <i class="fas fa-upload"></i>
                </span>
                <span class="file-label">
                  Choisir un fichier
                </span>
              </span>
              <span class="file-name" v-if="selectedFile">
                {{ selectedFile.name }}
              </span>
              <span class="file-name" v-else>
                Aucun fichier sélectionné
              </span>
            </label>
          </div>
        </div>
        
        <div class="field">
          <div class="control">
            <button 
              class="button is-primary is-fullwidth" 
              :disabled="!canCreateChat"
              @click="createNewChat"
              :class="{'is-loading': isCreatingChat}"
            >
              Créer la conversation
            </button>
          </div>
        </div>
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
    
    <div class="chat-interface-container" v-if="selectedChat">
      <div class="chat-header">
        <h2 class="subtitle">{{ selectedChat.nom_chat }}</h2>
        <button class="button is-small" @click="showUploadModal = true">
          <span class="icon">
            <i class="fas fa-file-upload"></i>
          </span>
          <span>Ajouter un document</span>
        </button>
      </div>
      
      <div class="documents-list">
        <h3 class="is-size-6 mb-2">Documents</h3>
        <div class="document-item" v-for="doc in selectedChat.documents" :key="doc.id_document">
          <span class="icon">
            <i class="fas fa-file-pdf"></i>
          </span>
          <span>{{ doc.nom_document }}</span>
        </div>
      </div>
      
      <!-- Ici, on pourrait intégrer le composant de chat existant -->
    </div>
    
    <div v-else class="chat-detail-empty">
      <p>Sélectionnez une conversation ou créez-en une nouvelle</p>
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
                <input class="file-input" type="file" accept=".pdf" @change="handleAdditionalFileChange">
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
            @click="uploadAdditionalDocument"
            :class="{'is-loading': isUploadingDocument}"
          >
            Ajouter
          </button>
          <button class="button" @click="showUploadModal = false">Annuler</button>
        </footer>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import authState from '../stores/auth'

// État local
const chats = ref([])
const selectedChatId = ref(null)
const selectedChat = ref(null)
const newChatName = ref('')
const selectedFile = ref(null)
const additionalFile = ref(null)
const isLoadingChats = ref(true)
const isCreatingChat = ref(false)
const isUploadingDocument = ref(false)
const showUploadModal = ref(false)

// Vérifier si on peut créer un chat
const canCreateChat = computed(() => {
  return newChatName.value.trim() !== '' && selectedFile.value !== null
})

// Charger la liste des chats au montage du composant
onMounted(async () => {
  await fetchChats()
})

// Récupérer la liste des chats depuis l'API
async function fetchChats() {
  try {
    isLoadingChats.value = true
    
    // Utiliser l'URL complète avec le domaine
    const response = await fetch('http://localhost:8000/chat/api/list/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include'
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Erreur lors du chargement des conversations')
    }
    
    const data = await response.json()
    chats.value = data
  } catch (error) {
    console.error('Erreur:', error)
    alert('Erreur lors du chargement des conversations: ' + error.message)
  } finally {
    isLoadingChats.value = false
  }
}

// Gérer la sélection d'un fichier
function handleFileChange(event) {
  const file = event.target.files[0]
  if (file && file.type === 'application/pdf') {
    selectedFile.value = file
  } else {
    selectedFile.value = null
    alert('Veuillez sélectionner un fichier PDF')
  }
}

// Gérer la sélection d'un fichier additionnel
function handleAdditionalFileChange(event) {
  const file = event.target.files[0]
  if (file && file.type === 'application/pdf') {
    additionalFile.value = file
  } else {
    additionalFile.value = null
    alert('Veuillez sélectionner un fichier PDF')
  }
}

// Créer un nouveau chat
async function createNewChat() {
  if (!canCreateChat.value) return
  
  try {
    isCreatingChat.value = true
    
    const formData = new FormData()
    formData.append('nom_chat', newChatName.value)
    formData.append('document', selectedFile.value)
    
    // Utiliser l'URL complète avec le domaine
    const response = await fetch('http://localhost:8000/chat/api/create/', {
      method: 'POST',
      body: formData,
      credentials: 'include' // Pour envoyer les cookies de session
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Erreur lors de la création de la conversation')
    }
    
    const newChat = await response.json()
    
    // Ajouter le nouveau chat à la liste et le sélectionner
    chats.value.push(newChat)
    selectChat(newChat)
    
    // Réinitialiser le formulaire
    newChatName.value = ''
    selectedFile.value = null
    
  } catch (error) {
    console.error('Erreur:', error)
    alert('Erreur lors de la création de la conversation: ' + error.message)
  } finally {
    isCreatingChat.value = false
  }
}

// Ajouter un document à un chat existant
async function uploadAdditionalDocument() {
  if (!additionalFile.value || !selectedChat.value) return
  
  try {
    isUploadingDocument.value = true
    
    const formData = new FormData()
    formData.append('document', additionalFile.value)
    
    // Utiliser l'URL complète avec le domaine
    const response = await fetch(`http://localhost:8000/chat/api/${selectedChat.value.id_chat}/`, {
      method: 'POST',
      body: formData,
      credentials: 'include'
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Erreur lors de l\'ajout du document')
    }
    
    const newDocument = await response.json()
    
    // Ajouter le document à la liste des documents du chat sélectionné
    selectedChat.value.documents.push(newDocument)
    
    // Fermer la modal et réinitialiser
    showUploadModal.value = false
    additionalFile.value = null
    
  } catch (error) {
    console.error('Erreur:', error)
    alert('Erreur lors de l\'ajout du document: ' + error.message)
  } finally {
    isUploadingDocument.value = false
  }
}

// Sélectionner un chat
function selectChat(chat) {
  selectedChat.value = chat
  
  // Émettre un événement personnalisé pour informer ChatView
  const event = new CustomEvent('chat-selected', {
    detail: { chatId: chat.id_chat }
  })
  window.dispatchEvent(event)
  
  // Fermer la sidebar sur mobile après sélection d'un chat
  if (window.innerWidth < 768) {
    const sidebarToggle = document.querySelector('.sidebar-toggle')
    if (sidebarToggle) {
      sidebarToggle.click()
    }
  }
}

// Formater une date
function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.chat-manager {
  display: flex;
  height: calc(100vh - 7rem);
  max-width: 1200px;
  margin: 0 auto;
  gap: 1rem;
}

.chat-list-container {
  width: 300px;
  border-right: 1px solid #80e7c9;
  padding: 1rem;
  overflow-y: auto;
}

.chat-interface-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-detail-empty {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #888;
}

.chat-item {
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.chat-item:hover {
  background-color: rgba(128, 231, 201, 0.1);
}

.chat-item.is-active {
  background-color: rgba(128, 231, 201, 0.2);
  border-color: #80e7c9;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #80e7c9;
}

.documents-list {
  margin-bottom: 1rem;
}

.document-item {
  padding: 0.5rem;
  border-radius: 4px;
  background-color: rgba(128, 231, 201, 0.1);
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
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

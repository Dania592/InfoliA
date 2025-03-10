<template>
  <div class="modal" :class="{'is-active': isActive}">
    <div class="modal-background" @click="closeModal"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">Nouvelle conversation</p>
        <button class="delete" aria-label="close" @click="closeModal"></button>
      </header>
      <section class="modal-card-body">
        <!-- Étape 1: Nom de la conversation -->
        <div class="field">
          <label class="label">Nom de la conversation</label>
          <div class="control">
            <input 
              class="input" 
              type="text" 
              placeholder="Entrez un nom pour cette conversation" 
              v-model="conversationName"
              :class="{ 'is-danger': nameError }"
              ref="nameInput"
            >
          </div>
          <p v-if="nameError" class="help is-danger">{{ nameError }}</p>
        </div>

        <!-- Upload du document -->
        <div class="file-upload-container">
          <label class="label">Document (PDF uniquement, obligatoire)</label>
          <div class="file has-name is-fullwidth">
            <label class="file-label">
              <input class="file-input" type="file" @change="handleFileUpload" accept=".pdf">
              <span class="file-cta">
                <span class="file-icon">
                  ⬆️
                </span>
                <span class="file-label">
                  Choisir un fichier PDF
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
          <p v-if="fileError" class="help is-danger">{{ fileError }}</p>
          <div class="file-info mt-3" v-if="selectedFile">
            <p><strong>Type:</strong> {{ selectedFile.type || 'Non spécifié' }}</p>
            <p><strong>Taille:</strong> {{ formatFileSize(selectedFile.size) }}</p>
          </div>
          <div class="supported-formats mt-3">
            <p class="is-size-7">Formats supportés: PDF</p>
          </div>
        </div>

        <!-- Message de statut -->
        <div v-if="statusMessage" class="notification mt-3" :class="statusClass">
          <button class="delete" @click="statusMessage = ''"></button>
          {{ statusMessage }}
        </div>
      </section>
      
      <footer class="modal-card-foot">
        <button 
          class="button is-primary" 
          @click="createConversation"
          :class="{ 'is-loading': isLoading }"
          :disabled="isLoading || !isValid"
        >
          Créer la conversation
        </button>
        <button 
          class="button" 
          @click="closeModal"
          :disabled="isLoading"
        >
          Annuler
        </button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import authState from '../stores/auth'
import axios from "axios";

// Props
const props = defineProps({
  isActive: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['close', 'conversation-created'])

// État local
const conversationName = ref('')
const selectedFile = ref(null)
const nameError = ref('')
const fileError = ref('')
const isLoading = ref(false)
const statusMessage = ref('')
const statusClass = ref('is-info')
const nameInput = ref(null)
const MAX_FILENAME_LENGTH = 50

// Computed properties
const isValid = computed(() => {
  return conversationName.value.trim() !== '' && !nameError.value && !fileError.value
})

// Méthodes
const closeModal = () => {
  // Ne rien faire si en cours de chargement
  if (isLoading.value) return
  
  // Réinitialiser les états avant de fermer
  conversationName.value = ''
  selectedFile.value = null
  nameError.value = ''
  fileError.value = ''
  statusMessage.value = ''
  
  // Émettre l'événement de fermeture
  emit('close')
}

const validateForm = () => {
  let isValid = true
  
  // Valider le nom
  if (!conversationName.value.trim()) {
    nameError.value = 'Veuillez entrer un nom pour la conversation'
    isValid = false
  } else if (conversationName.value.length > 50) {
    nameError.value = 'Le nom est trop long (max 50 caractères)'
    isValid = false
  } else {
    nameError.value = ''
  }
  
  // Valider le fichier si sélectionné
  if (selectedFile.value) {
    // Vérifier la taille du fichier (max 10MB)
    if (selectedFile.value.size > 10 * 1024 * 1024) {
      fileError.value = 'Le fichier est trop volumineux (max 10MB)'
      isValid = false
    } else {
      fileError.value = ''
    }
  }
  
  return isValid
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    // Vérifier le type de fichier
    const allowedTypes = [
      'application/pdf'
    ]
    
    if (!allowedTypes.includes(file.type) && 
        !(file.name.endsWith('.pdf'))) {
      fileError.value = 'Format de fichier non supporté. Utilisez PDF.'
      selectedFile.value = null
      return
    }
    let sanitizedFileName = file.name.replace(/\s+/g, '_')
    const sanitizedFile = new File(
      [file],
      sanitizedFileName,
      { type: file.type }
    )

    // Vérifier la taille du fichier (max 10MB)
    if (sanitizedFile.size > 10 * 1024 * 1024) {
      fileError.value = 'Le fichier est trop volumineux (max 10MB)'
      selectedFile.value = null
      return
    }

    if (sanitizedFile.name.length > MAX_FILENAME_LENGTH) {
      fileError.value = `Le nom du fichier est trop long (max ${MAX_FILENAME_LENGTH} caractères).`
      selectedFile.value = null
      return
    }
    selectedFile.value = sanitizedFile
    fileError.value = ''
  } else {
    selectedFile.value = null
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const createConversation = async () => {
  // Valider le formulaire
  if (!validateForm()) {
    statusMessage.value = 'Veuillez corriger les erreurs dans le formulaire'
    statusClass.value = 'is-warning'
    return
  }
  
  try {
    isLoading.value = true
    statusMessage.value = 'Création de la conversation...'
    statusClass.value = 'is-info'
    
    // Vérifier que l'utilisateur est connecté
    if (!authState.isAuthenticated) {
      throw new Error('Vous devez être connecté pour créer une conversation')
    }
    
    // Préparation des données
    const formData = new FormData()
    formData.append("chat_name", conversationName.value)
    formData.append("user_name", authState.pseudo)
    
    if (selectedFile.value) {
      formData.append("file", selectedFile.value)
    }
    
    // Appel API pour l'upload du fichier si présent
    let chatId = null
    
    if (selectedFile.value) {
      try {
        const response = await axios.post("/chat/upload/", formData, {
          headers: { "Content-Type": "multipart/form-data" }
        })

      } catch (error) {
        console.error("Erreur lors de l'upload:", error)
        throw new Error("Erreur lors de l'upload du fichier: " + 
                        (error.response?.data?.message || error.message))
      }
    }
    
    // S'il n'y a pas d'ID de chat depuis l'upload, créer la conversation

    const createResponse = await fetch('/chat/create_chat/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        chat_name: conversationName.value,
        pseudo: authState.pseudo,
        pdf_name: selectedFile.value ? selectedFile.value.name : null
      })
    })

    if (!createResponse.ok) {
      const errorText = await createResponse.text()
      try {
        const errorData = JSON.parse(errorText)
        throw new Error(errorData.error || 'Erreur lors de la création de la conversation')
      } catch (e) {
        throw new Error(`Erreur ${createResponse.status}: ${errorText || createResponse.statusText}`)
      }
    }

    const data = await createResponse.json()
    chatId = data.chat_id || (data.vector_db ? data.vector_db.id_chat : null)
    
    if (!chatId) {
      throw new Error('Réponse invalide du serveur: ID de chat manquant')
    }
    
    // Créer un objet de conversation
    const newConversation = {
      id: Date.now(),
      name: conversationName.value,
      document: selectedFile.value ? selectedFile.value.name : null,
      createdAt: new Date().toISOString(),
      userId: authState.pseudo,
      backendId: chatId
    }
    
    // Stocker la conversation dans le localStorage avec l'ID de l'utilisateur
    const userId = authState.pseudo
    const conversations = JSON.parse(localStorage.getItem(`conversations_${userId}`) || '[]')
    conversations.push(newConversation)
    localStorage.setItem(`conversations_${userId}`, JSON.stringify(conversations))
    
    // Fermer d'abord le modal pour éviter les problèmes de transition
    emit('close')
    
    // Ensuite émettre l'événement avec un petit délai
    setTimeout(() => {
      emit('conversation-created', newConversation)
    }, 100)
    
  } catch (error) {
    console.error('Erreur lors de la création de la conversation:', error)
    statusMessage.value = `Erreur: ${error.message}`
    statusClass.value = 'is-danger'
  } finally {
    isLoading.value = false
  }
}

// Focus l'input du nom lors de l'ouverture du modal
onMounted(async () => {
  if (props.isActive) {
    await nextTick()
    nameInput.value?.focus()
  }
})
</script>

<style scoped>
.modal-card {
  width: 90%;
  max-width: 600px;
}

.file-upload-container {
  margin-top: 1.5rem;
}

.notification {
  margin-top: 1rem;
}

.file-info p {
  margin-bottom: 0.25rem;
  font-size: 0.9rem;
}

.file-info strong {
  font-weight: 600;
}

.mt-3 {
  margin-top: 1rem;
}

@media screen and (max-width: 768px) {
  .modal-card {
    width: 95%;
    margin: 0 10px;
  }
}
</style>

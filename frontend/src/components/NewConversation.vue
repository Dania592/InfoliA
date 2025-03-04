<template>
  <div class="modal" :class="{'is-active': isActive}">
    <div class="modal-background" @click="closeModal"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">Nouvelle conversation</p>
        <button class="delete" aria-label="close" @click="closeModal"></button>
      </header>
      <section class="modal-card-body">
        <div class="steps">
          <div class="step-item" :class="{ 'is-active': currentStep === 1, 'is-completed': currentStep > 1 }">
            <div class="step-marker">1</div>
            <div class="step-details">
              <p class="step-title">Nom</p>
            </div>
          </div>
          <div class="step-item" :class="{ 'is-active': currentStep === 2, 'is-completed': currentStep > 2 }">
            <div class="step-marker">2</div>
            <div class="step-details">
              <p class="step-title">Document</p>
            </div>
          </div>
          <div class="step-item" :class="{ 'is-active': currentStep === 3 }">
            <div class="step-marker">3</div>
            <div class="step-details">
              <p class="step-title">Confirmation</p>
            </div>
          </div>
        </div>

        <!-- Étape 1: Nom de la conversation -->
        <div v-if="currentStep === 1" class="step-content">
          <div class="field">
            <label class="label">Nom de la conversation</label>
            <div class="control">
              <input 
                class="input" 
                type="text" 
                placeholder="Entrez un nom pour cette conversation" 
                v-model="conversationName"
                :class="{ 'is-danger': nameError }"
              >
            </div>
            <p v-if="nameError" class="help is-danger">{{ nameError }}</p>
          </div>
        </div>

        <!-- Étape 2: Upload du document -->
        <div v-if="currentStep === 2" class="step-content">
          <div class="file-upload-container">
            <div class="file has-name is-fullwidth">
              <label class="file-label">
                <input class="file-input" type="file" @change="handleFileUpload" accept=".pdf">
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
            <p v-if="fileError" class="help is-danger">{{ fileError }}</p>
            <div class="file-info mt-3" v-if="selectedFile">
              <p><strong>Type:</strong> {{ selectedFile.type || 'Non spécifié' }}</p>
              <p><strong>Taille:</strong> {{ formatFileSize(selectedFile.size) }}</p>
            </div>
            <div class="supported-formats mt-3">
              <p class="is-size-7">Formats supportés: PDF</p>
            </div>
          </div>
        </div>

        <!-- Étape 3: Confirmation -->
        <div v-if="currentStep === 3" class="step-content">
          <div class="notification is-info is-light">
            <h4 class="title is-5">Résumé</h4>
            <p><strong>Nom de la conversation:</strong> {{ conversationName }}</p>
            <p><strong>Document:</strong> {{ selectedFile ? selectedFile.name : 'Aucun' }}</p>
          </div>
        </div>
      </section>
      
      <footer class="modal-card-foot">
        <button 
          v-if="currentStep > 1" 
          class="button" 
          @click="prevStep"
        >
          Précédent
        </button>
        <button 
          v-if="currentStep < 3" 
          class="button is-primary" 
          @click="nextStep"
          :disabled="isNextButtonDisabled"
        >
          Suivant
        </button>
        <button 
          v-if="currentStep === 3" 
          class="button is-success" 
          @click="createConversation"
          :class="{ 'is-loading': isLoading }"
        >
          Créer la conversation
        </button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import authState from '../stores/auth'
import axios from "axios";
import { defineEmits } from 'vue';

// Props
const props = defineProps({
  isActive: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['close', 'conversation-created'])

// Router
const router = useRouter()

// État local
const currentStep = ref(1)
const conversationName = ref('')
const selectedFile = ref(null)
const nameError = ref('')
const fileError = ref('')
const isLoading = ref(false)

// Computed properties
const isNextButtonDisabled = computed(() => {
  if (currentStep.value === 1) {
    return !conversationName.value.trim()
  } else if (currentStep.value === 2) {
    return !selectedFile.value
  }
  return false
})

// Méthodes
const closeModal = () => {
  // Réinitialiser les états avant de fermer
  currentStep.value = 1
  conversationName.value = ''
  selectedFile.value = null
  nameError.value = ''
  fileError.value = ''
  
  // Émettre l'événement de fermeture
  emit('close')
}

const nextStep = () => {
  if (currentStep.value === 1) {
    if (!conversationName.value.trim()) {
      nameError.value = 'Veuillez entrer un nom pour la conversation'
      return
    }
    nameError.value = ''
  } else if (currentStep.value === 2) {
    if (!selectedFile.value) {
      fileError.value = 'Veuillez sélectionner un fichier'
      return
    }
    fileError.value = ''
  }
  
  currentStep.value++
}

const prevStep = () => {
  currentStep.value--
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    // Vérifier le type de fichier
    const allowedTypes = [
      'application/pdf', 
      'application/msword', 
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain'
    ]
    
    if (!allowedTypes.includes(file.type) && 
        !(file.name.endsWith('.pdf') || 
          file.name.endsWith('.doc') || 
          file.name.endsWith('.docx') || 
          file.name.endsWith('.txt'))) {
      fileError.value = 'Format de fichier non supporté. Utilisez PDF, DOC, DOCX ou TXT.'
      selectedFile.value = null
      return
    }
    
    // Vérifier la taille du fichier (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      fileError.value = 'Le fichier est trop volumineux (max 10MB)'
      selectedFile.value = null
      return
    }
    
    selectedFile.value = file
    fileError.value = ''
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
  try {
    isLoading.value = true
    
    // Vérifier que l'utilisateur est connecté
    if (!authState.isAuthenticated) {
      throw new Error('Vous devez être connecté pour créer une conversation')
    }
    
    // Vérifier que le fichier est bien un PDF
    if (!selectedFile.value || !selectedFile.value.name.toLowerCase().endsWith('.pdf')) {
      throw new Error('Veuillez sélectionner un fichier PDF valide')
    }

    console.log('Envoi de la conversation avec:', {
      pseudo: authState.pseudo,
      chat_name: conversationName.value,
      pdf_name: selectedFile.value.name
    })

    const formData = new FormData();
    formData.append("file", selectedFile.value);
    formData.append("chat_name", conversationName.value);
    formData.append("user_name", authState.pseudo)
    try {
        const response = await axios.post("http://127.0.0.1:8000/chat/upload/", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
        console.log("Réponse du serveur:", response.data);
      } catch (error) {
        console.error("Erreur lors de l'upload:", error);
      }

    const response = await fetch('/chat/create_chat/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        chat_name: conversationName.value,
        pseudo: authState.pseudo,
        pdf_name: selectedFile.value.name,
        pdf_file : selectedFile.value
      })
    })
    
    console.log('Réponse reçue du backend, status:', response.status)
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('Erreur de réponse:', errorText)
      try {
        const errorData = JSON.parse(errorText)
        throw new Error(errorData.error || 'Erreur lors de la création de la conversation')
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
    
    // Adaptation pour le backend fonctionnel
    // Le backend fonctionnel renvoie un format différent, on s'adapte aux deux possibilités
    const chatId = data.chat_id || (data.vector_db ? data.vector_db.id_chat : null)
    
    if (!data || !chatId) {
      console.error('Réponse invalide du serveur:', data)
      throw new Error('Réponse invalide du serveur: ID de chat manquant')
    }
    
    // Créer un objet de conversation
    // Utiliser le format de chat_name attendu par le backend fonctionnel
    const newConversation = {
      id: Date.now(), // Utiliser un ID numérique pour le frontend
      name: conversationName.value,
      document: selectedFile.value.name,
      createdAt: new Date().toISOString(),
      userId: authState.pseudo,
      // Stocker l'ID du backend pour les appels API futurs
      // Pour le backend fonctionnel, on utilise simplement le nom du chat
      backendId: chatId
    }
    
    console.log('Nouvelle conversation créée:', newConversation)
    
    // Stocker la conversation dans le localStorage avec l'ID de l'utilisateur
    const userId = authState.pseudo
    const conversations = JSON.parse(localStorage.getItem(`conversations_${userId}`) || '[]')
    conversations.push(newConversation)
    localStorage.setItem(`conversations_${userId}`, JSON.stringify(conversations))
    
    console.log('Conversation ajoutée au localStorage')
    
    // Fermer le modal immédiatement
    closeModal()
    
    // Émettre un événement pour informer le parent
    emit('conversation-created', newConversation)

    // Déclencher un événement personnalisé pour sélectionner le chat
    // Utiliser setTimeout pour s'assurer que l'événement est traité après la fermeture du modal
    setTimeout(() => {
      window.dispatchEvent(new CustomEvent('chat-selected', {
        detail: { chatId: newConversation.id }
      }))

      console.log('Événement chat-selected dispatché avec ID:', newConversation.id)
    }, 300) // Augmenter le délai pour s'assurer que le composant parent a le temps de réagir

  } catch (error) {
    console.error('Erreur lors de la création de la conversation:', error)
    alert('Une erreur est survenue lors de la création de la conversation: ' + error.message)
    // Fermer le modal en cas d'erreur
    closeModal()
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* Utilisation des styles Bulma pour le modal */
.steps {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.step-item {
  position: relative;
  flex-grow: 1;
  flex-basis: 0;
  margin-top: 0;
  text-align: center;
  padding: 1rem 0;
}

.step-item:not(:first-child)::before {
  content: "";
  position: absolute;
  left: -50%;
  top: 50%;
  height: 2px;
  width: 100%;
  background-color: #dbdbdb;
  z-index: 0;
}

.step-marker {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background-color: #dbdbdb;
  color: #fff;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.step-details {
  margin-top: 0.5rem;
  text-align: center;
}

.step-title {
  font-size: 0.9rem;
  font-weight: 600;
}

.step-item.is-active .step-marker {
  background-color: #3273dc;
}

.step-item.is-completed .step-marker {
  background-color: #23d160;
}

.step-item.is-active .step-title {
  color: #3273dc;
  font-weight: 700;
}

.step-item.is-completed .step-title {
  color: #23d160;
}

.step-item.is-completed::before {
  background-color: #23d160;
}

.step-item.is-active::before {
  background-color: #3273dc;
}

.file-upload-container {
  margin-top: 1rem;
}

.selected-file {
  margin-top: 1rem;
  padding: 1rem;
  border: 1px solid #dbdbdb;
  border-radius: 4px;
  background-color: #f5f5f5;
}

.confirmation-step {
  text-align: center;
}

.confirmation-icon {
  font-size: 3rem;
  color: #23d160;
  margin-bottom: 1rem;
}

.confirmation-details {
  margin-top: 1rem;
  padding: 1rem;
  border: 1px solid #dbdbdb;
  border-radius: 4px;
  background-color: #f5f5f5;
  text-align: left;
}

.error-message {
  color: #ff3860;
  font-size: 0.8rem;
  margin-top: 0.25rem;
}
</style>

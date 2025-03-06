import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useChatStore = defineStore('chat', () => {
  // État
  const conversations = ref([])
  const selectedChatId = ref(null)
  const messages = ref({}) // Stocke les messages par ID de chat
  const isLoading = ref(false)
  
  // Getters
  const currentChat = computed(() => {
    if (!selectedChatId.value) return null
    return conversations.value.find(chat => String(chat.id_chat) === String(selectedChatId.value))
  })
  
  const currentMessages = computed(() => {
    if (!selectedChatId.value) return []
    return messages.value[selectedChatId.value] || []
  })
  
  // Actions
  function setConversations(newConversations) {
    conversations.value = newConversations
  }
  
  function addConversation(conversation) {
    conversations.value.push(conversation)
    saveConversationsToStorage()
  }
  
  function updateConversation(id, updates) {
    const index = conversations.value.findIndex(c => String(c.id_chat) === String(id))
    if (index !== -1) {
      conversations.value[index] = { ...conversations.value[index], ...updates }
      saveConversationsToStorage()
    }
  }
  
  function removeConversation(id) {
    conversations.value = conversations.value.filter(c => String(c.id_chat) !== String(id))
    // Supprimer aussi les messages associés
    delete messages.value[id]
    saveConversationsToStorage()
    saveChatMessagesToStorage()
    
    // Si c'était le chat sélectionné, on désélectionne
    if (selectedChatId.value === id) {
      selectedChatId.value = conversations.value.length > 0 ? String(conversations.value[0].id_chat) : null
    }
  }
  
  function selectChat(id) {
    if (id) {
      selectedChatId.value = String(id)
      // Charger les messages si nécessaire
      if (!messages.value[id]) {
        loadChatMessages(id)
      }
    } else {
      selectedChatId.value = null
    }
  }
  
  function addMessage(chatId, message) {
    if (!messages.value[chatId]) {
      messages.value[chatId] = []
    }
    messages.value[chatId].push(message)
    saveChatMessagesToStorage()
  }
  
  function setMessages(chatId, newMessages) {
    messages.value[chatId] = newMessages
    saveChatMessagesToStorage()
  }
  
  // Chargement depuis le localStorage
  function loadFromLocalStorage(userId) {
    try {
      // Charger les conversations
      const storedConversations = localStorage.getItem(`conversations_${userId}`)
      if (storedConversations) {
        conversations.value = JSON.parse(storedConversations)
      }
      
      // Charger le chat sélectionné
      const storedSelectedChatId = localStorage.getItem(`selectedChatId_${userId}`)
      if (storedSelectedChatId) {
        selectedChatId.value = storedSelectedChatId
        selectedChatId.value = "user_"+userId+"."+"chat_"+ localStorage.getItem('chat')
        // Charger les messages de ce chat
        loadChatMessages(storedSelectedChatId, userId)
      }
    } catch (error) {
      console.error('Erreur lors du chargement depuis le localStorage:', error)
    }
  }
  
  // Chargement des messages d'un chat spécifique
  function loadChatMessages(chatId, userId = null) {
    const user = userId || getUserId()
    if (!user) return
    
    try {
      const storedMessages = localStorage.getItem(`chat_messages_${user}_${chatId}`)
      if (storedMessages) {
        messages.value[chatId] = JSON.parse(storedMessages)
      } else {
        messages.value[chatId] = []
      }
    } catch (error) {
      console.error(`Erreur lors du chargement des messages du chat ${chatId}:`, error)
      messages.value[chatId] = []
    }
  }
  
  // Sauvegarde dans le localStorage
  function saveConversationsToStorage() {
    const userId = getUserId()
    if (!userId) return
    
    try {
      localStorage.setItem(`conversations_${userId}`, JSON.stringify(conversations.value))
      if (selectedChatId.value) {
        localStorage.setItem(`selectedChatId_${userId}`, selectedChatId.value)
      }
    } catch (error) {
      console.error('Erreur lors de la sauvegarde des conversations:', error)
    }
  }
  
  function saveChatMessagesToStorage() {
    const userId = getUserId()
    if (!userId) return
    
    try {
      Object.entries(messages.value).forEach(([chatId, chatMessages]) => {
        localStorage.setItem(`chat_messages_${userId}_${chatId}`, JSON.stringify(chatMessages))
      })
    } catch (error) {
      console.error('Erreur lors de la sauvegarde des messages:', error)
    }
  }
  
  // Utilitaire pour obtenir l'ID utilisateur
  function getUserId() {
    return localStorage.getItem('pseudo')
  }
  
  // Réinitialiser l'état (par exemple lors de la déconnexion)
  function resetState() {
    conversations.value = []
    selectedChatId.value = null
    messages.value = {}
  }
  
  // Réinitialiser uniquement le chat sélectionné
  function resetSelectedChat() {
    selectedChatId.value = null
  }
  
  return {
    // État
    conversations,
    selectedChatId,
    messages,
    isLoading,
    
    // Getters
    currentChat,
    currentMessages,
    
    // Actions
    setConversations,
    addConversation,
    updateConversation,
    removeConversation,
    selectChat,
    addMessage,
    setMessages,
    loadFromLocalStorage,
    loadChatMessages,
    resetState,
    resetSelectedChat
  }
})

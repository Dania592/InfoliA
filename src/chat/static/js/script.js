function sendMessage(event) {
      event.preventDefault();
      const input = document.getElementById('messageInput');
      const messageText = input.value.trim();
      if (!messageText) return;

      const chatHistory = document.getElementById('chatHistory');

      const userMessage = document.createElement('div');
      userMessage.className = 'message user';
      userMessage.textContent = messageText;
      chatHistory.appendChild(userMessage);

      input.value = '';
      chatHistory.scrollTop = chatHistory.scrollHeight;

      setTimeout(() => {
        const llmResponse = document.createElement('div');
        llmResponse.className = 'message llm';
        llmResponse.textContent = "(Réponse simulée de l'LLM)";
        chatHistory.appendChild(llmResponse);
        chatHistory.scrollTop = chatHistory.scrollHeight;
      }, 500);
    }

    function createNewDiscussion() {
      const discussionName = prompt("Nom de la nouvelle discussion :");
      if (discussionName) {
        const discussionList = document.getElementById('discussionList');
        const newDiscussion = document.createElement('div');
        newDiscussion.className = 'discussion-item';
        newDiscussion.textContent = discussionName;
        newDiscussion.onclick = () => selectDiscussion(discussionName);
        discussionList.appendChild(newDiscussion);
        selectDiscussion(discussionName);
      }
    }

    function selectDiscussion(name) {
      document.getElementById('chatTitle').textContent = name;
      document.getElementById('chatHistory').innerHTML = '';
      const welcomeMessage = document.createElement('div');
      welcomeMessage.className = 'message llm';
      welcomeMessage.textContent = `Bienvenue dans ${name} ! Posez votre question.`;
      document.getElementById('chatHistory').appendChild(welcomeMessage);
    }
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
        llmResponse.textContent = "reponse ici";
        chatHistory.appendChild(llmResponse);
        chatHistory.scrollTop = chatHistory.scrollHeight;
      }, 500);
    }

    function createNewDiscussion() {
      const discussionName = prompt("Nom CHAT :");
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
        console.log("iciiii")
      document.getElementById('chatTitle').textContent = name;
      document.getElementById('chatHistory').innerHTML = '';
      const welcomeMessage = document.createElement('div');
      welcomeMessage.className = 'message llm';
      welcomeMessage.textContent = `Bienve.`;
      document.getElementById('chatHistory').appendChild(welcomeMessage);

      fetch('/api/init_rag/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ chat_name: name })
        })
        .then(response => response.json())
        .then(data => {
            console.log("RAG instance initialized:", data);
        })
        .catch(error => console.error('Error initializing RAG:', error));

    }
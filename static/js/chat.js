async function userResponse() {
  let userText = document.getElementById("textInput").value;

  if (userText == "") {
    alert("Please type something!");
    return;
  }

  // Display user message
  let messageBox = document.getElementById("messageBox");
  messageBox.innerHTML += `
    <div class="first-chat">
      <p>${escapeHtml(userText)}</p>
      <div class="arrow"></div>
    </div>`;

  // Clear input and scroll to bottom
  document.getElementById("textInput").value = "";
  messageBox.scrollTop = messageBox.scrollHeight;

  // Show typing indicator
  messageBox.innerHTML += `
    <div class="second-chat typing-indicator">
      <div class="circle" id="circle-mar"></div>
      <p>Typing...</p>
      <div class="arrow"></div>
    </div>`;

  try {
    const response = await fetch('/api/llama-chat/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({
        message: userText
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // Remove typing indicator
    const typingIndicator = messageBox.querySelector('.typing-indicator');
    if (typingIndicator) {
      typingIndicator.remove();
    }

    // Verify the response has the expected structure
    if (!data.message) {
      throw new Error('Invalid response format from server');
    }

    // Display bot response
    messageBox.innerHTML += `
      <div class="second-chat">
        <div class="circle" id="circle-mar"></div>
        <p>${escapeHtml(data.message)}</p>
        <div class="arrow"></div>
      </div>`;

    // Scroll to bottom
    messageBox.scrollTop = messageBox.scrollHeight;

  } catch (error) {
    console.error('Chat Error:', error);
    
    // Remove typing indicator
    const typingIndicator = messageBox.querySelector('.typing-indicator');
    if (typingIndicator) {
      typingIndicator.remove();
    }

    // Display error message to user
    messageBox.innerHTML += `
      <div class="second-chat error">
        <div class="circle" id="circle-mar"></div>
        <p>Sorry, I encountered an error. Please try again.</p>
        <div class="arrow"></div>
      </div>`;
  }
}
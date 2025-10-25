/**
 * app.js: JS code for the adk-streaming sample app.
 */


const userId = "user1";
const sessionId = crypto.randomUUID();
const send_url =
  "http://" + window.location.host + "/send/" + userId + "/" + sessionId;


const messageForm = document.getElementById("messageForm");
const messageInput = document.getElementById("message");
const messagesDiv = document.getElementById("messages");
const sendButton = document.getElementById("sendButton");
let currentMessageId = null;


messageForm.onsubmit = function (e) {
  e.preventDefault();
  const message = messageInput.value;
  if (message) {
    const p = document.createElement("p");
    p.textContent = "> " + message;
    messagesDiv.appendChild(p);
    messageInput.value = "";
    sendMessage({
      mime_type: "text/plain",
      data: message,
    });
    console.log("[CLIENT TO AGENT] " + message);
  }
  return false;
};


async function sendMessage(message) {
  try {
    const response = await fetch(send_url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(message)
    });

    if (!response.ok) {
      console.error('Failed to send message:', response.statusText);
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        break;
      }

      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split('\n');
      buffer = lines.pop(); // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.substring(6); // Remove 'data: ' prefix
          try {
            const message_from_server = JSON.parse(data);
            console.log("[AGENT TO CLIENT] ", message_from_server);
            handleServerMessage(message_from_server);
          } catch (e) {
            console.error('Error parsing SSE data:', e);
          }
        }
      }
    }
  } catch (error) {
    console.error('Error sending message:', error);
  }
}


function handleServerMessage(message_from_server) {
  if (message_from_server.turn_complete && message_from_server.turn_complete == true) {
    currentMessageId = null;
    return;
  }

  if (message_from_server.interrupted && message_from_server.interrupted === true) {
    return;
  }

  if (message_from_server.mime_type == "text/plain") {
    if (currentMessageId == null) {
      currentMessageId = createNewMessageElement();
    }

    appendTextToMessage(currentMessageId, message_from_server.data);

    scrollToBottom();
  }
}

// Helper functions
function generateMessageId() {
  return Math.random().toString(36).substring(7);
}

function createNewMessageElement() {
  const messageId = generateMessageId();
  const messageElement = document.createElement("p");
  messageElement.id = messageId;
  messagesDiv.appendChild(messageElement);
  return messageId;
}

function appendTextToMessage(messageId, text) {
  const messageElement = document.getElementById(messageId);
  const htmlFormattedText = text.replace(/\n/g, '<br>');
  messageElement.innerHTML += htmlFormattedText;
}

function scrollToBottom() {
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}
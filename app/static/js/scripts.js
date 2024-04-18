const chatbotToggler = document.querySelector(".chatbot-toggler");
const closeBtn = document.querySelector(".close-btn");
const chatbox = document.querySelector(".chatbox");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");

let userMessage = null; // Variable to store user's message
const inputInitHeight = chatInput.scrollHeight;

const createChatLi = (message, className) => {
    // Create a chat <li> element with passed message and className
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", `${className}`);
    let chatContent = className === "outgoing" ? `<p></p>` : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
    chatLi.innerHTML = chatContent;
    chatLi.querySelector("p").textContent = message;
    return chatLi; // return chat <li> element
}

const generateResponse = (chatElement) => {

    const messageElement = chatElement.querySelector("p");

    fetch('/result', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'message': userMessage }),
    })
        .then(response => response.json())
        .then(data => {
            console.log('Received data:', data);

            messageElement.innerHTML = `${data['bot_response']}<button class="read-aloud-btn" onclick="readAloud(this, '${data['bot_response']}')"><i class="fa-solid fa-volume-low"></i></button>`;



            // Check if bot response contains buttons
            if (data['buttons']) {
                console.log('Received buttons:', data['buttons']);

                // Append buttons to chat body
                var buttonsContainer = document.createElement('div');
                buttonsContainer.classList.add('message');

                data['buttons'].forEach(button => {
                    var buttonElement = document.createElement('button');
                    buttonElement.classList.add('payload-button');
                    buttonElement.textContent = button.title;
                    buttonElement.onclick = function () {
                        payload = button.payload;
                        chatInput.value = button.title;
                        handleChat();
                    };

                    buttonsContainer.appendChild(buttonElement);
                });

                messageElement.appendChild(buttonsContainer);
            }
        
    }).catch(() => {
        messageElement.classList.add("error");
        messageElement.textContent = "Oops! Something went wrong. Please try again.";
    }).finally(() => chatbox.scrollTo(0, chatbox.scrollHeight));
}

function readAloud(button, text) {
    const speechSynthesis = window.speechSynthesis;

    if (button.classList.contains('reading')) {
        // If speech is currently being read, stop it
        speechSynthesis.cancel();
        button.innerHTML = '<i class="fa-solid fa-volume-low"></i>';
        button.classList.remove('reading');
    } else {
        // If speech is not being read, start reading
        const speechUtterance = new SpeechSynthesisUtterance(text);

        // Add an event listener for when speech synthesis finishes
        speechUtterance.addEventListener('end', () => {
            // Once reading is done, display the volume button
            button.innerHTML = '<i class="fa-solid fa-volume-low"></i>';
            button.classList.remove('reading');
        });

        speechSynthesis.speak(speechUtterance);
        button.innerHTML = '<i class="fa-solid fa-stop"></i>';
        button.classList.add('reading');
    }
}


function speechText() {
    const recognition = new webkitSpeechRecognition() || new SpeechRecognition();
    let isListening = false;
    let transcript;
    // recognition.interimResults = true;
    recognition.continuous = false;

    if (!isListening) {
        recognition.start();
        toggleButton.innerHTML = '<i class="fas fa-stop"></i>';
        isListening = true;
    } else {
        recognition.stop();
        toggleButton.innerHTML = '<i class="fas fa-microphone"></i>';
        isListening = false;
    }

    recognition.onresult = event => {
        const result = Array.from(event.results)
            .map(result => result[0].transcript)
            .join('');
        chatInput.value = result;
        handleChat();
    };

    recognition.onend = () => {
        toggleButton.innerHTML = '<i class="fas fa-microphone"></i>';
        isListening = false;
    };

    recognition.onerror = event => {
        console.error('Speech recognition error:', event.error);
    };

}

const handleChat = () => {
    userMessage = chatInput.value.trim(); // Get user entered message and remove extra whitespace
    if(!userMessage) return;

    // Clear the input textarea and set its height to default
    chatInput.value = "";
    chatInput.style.height = `${inputInitHeight}px`;

    // Append the user's message to the chatbox
    chatbox.appendChild(createChatLi(userMessage, "outgoing"));
    chatbox.scrollTo(0, chatbox.scrollHeight);
    
    setTimeout(() => {
        // Display "Thinking..." message while waiting for the response
        const incomingChatLi = createChatLi("Typing...", "incoming");
        chatbox.appendChild(incomingChatLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);
        generateResponse(incomingChatLi);
    }, 600);
}

chatInput.addEventListener("input", () => {
    // Adjust the height of the input textarea based on its content
    chatInput.style.height = `${inputInitHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
    // If Enter key is pressed without Shift key and the window 
    // width is greater than 800px, handle the chat
    if(e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleChat();
    }
});

sendChatBtn.addEventListener("click", handleChat);
closeBtn.addEventListener("click", () => document.body.classList.remove("show-chatbot"));
chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));
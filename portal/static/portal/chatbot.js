document.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("chat");
  const windowBox = document.getElementById("chat-window");
  const close = document.getElementById("chat-close");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");
  const messages = document.getElementById("chat-messages");
  const send = document.getElementById("chat-send");
  const suggestions = document.querySelector(".chat-suggestions");
  const voiceButton = document.getElementById("chat-voice-input");
  const voiceLanguage = document.getElementById("chat-voice-language");
  const speakToggle = document.getElementById("chat-speak-toggle");

  if (!button || !windowBox || !close || !form || !input || !messages || !send || !suggestions) {
    return;
  }

  let voiceRepliesEnabled = false;
  let activeRecognition = null;

  button.addEventListener("click", () => {
    windowBox.style.display = "flex";
    windowBox.setAttribute("aria-hidden", "false");
    button.setAttribute("aria-expanded", "true");
    input.focus();
  });

  close.addEventListener("click", () => {
    windowBox.style.display = "none";
    windowBox.setAttribute("aria-hidden", "true");
    button.setAttribute("aria-expanded", "false");
    window.speechSynthesis?.cancel();
    input.focus();
  });

  function addMessage(text, sender) {
    const bubble = document.createElement("div");
    bubble.className = sender === "user" ? "user-message" : "bot-message";
    bubble.textContent = text;
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
    return bubble;
  }

  function speakReply(text) {
    if (!voiceRepliesEnabled || !window.speechSynthesis || !window.SpeechSynthesisUtterance) return;
    const language = /[\u0B80-\u0BFF]/.test(text) ? "ta-IN" : "en-IN";
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language;
    const voice = window.speechSynthesis.getVoices().find((item) => item.lang.toLowerCase().startsWith(language.slice(0, 2)));
    if (voice) utterance.voice = voice;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  }

  async function sendMessage(text) {
    text = text.trim();
    if (!text || input.disabled) return;

    addMessage(text, "user");
    input.value = "";
    input.disabled = true;
    send.disabled = true;
    const loading = addMessage("Thinking…", "bot");

    try {
      const csrfInput = form.querySelector('[name="csrfmiddlewaretoken"]');
      const response = await fetch("/chatbot/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfInput.value,
        },
        body: JSON.stringify({ message: text }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.reply || data.error || "Request failed");
      const reply = data.reply || "I couldn't find an answer in the available scheme information.";
      loading.textContent = reply;
      speakReply(reply);
    } catch (error) {
      loading.textContent = error.message || "Sorry, I couldn't connect. Please try again.";
      console.error("AI Seva chatbot request failed:", error);
    } finally {
      input.disabled = false;
      send.disabled = false;
      input.focus();
    }
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    sendMessage(input.value);
  });

  suggestions.addEventListener("click", (event) => {
    const option = event.target.closest("[data-message]");
    if (option) sendMessage(option.dataset.message);
  });

  if (speakToggle) {
    speakToggle.addEventListener("click", () => {
      voiceRepliesEnabled = !voiceRepliesEnabled;
      speakToggle.setAttribute("aria-pressed", String(voiceRepliesEnabled));
      speakToggle.setAttribute("aria-label", voiceRepliesEnabled ? "Turn voice replies off" : "Turn voice replies on");
      speakToggle.title = voiceRepliesEnabled ? "Voice replies on" : "Voice replies off";
      speakToggle.textContent = voiceRepliesEnabled ? "🔊" : "🔈";
      if (!voiceRepliesEnabled) window.speechSynthesis?.cancel();
    });
  }

  if (voiceButton) {
    voiceButton.addEventListener("click", () => {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        addMessage("Voice input isn't available in this browser. You can type your question instead.", "bot");
        return;
      }
      if (activeRecognition) {
        activeRecognition.stop();
        return;
      }

      const recognition = new SpeechRecognition();
      activeRecognition = recognition;
      recognition.lang = voiceLanguage?.value || "en-IN";
      recognition.interimResults = false;
      recognition.continuous = false;
      voiceButton.setAttribute("aria-label", "Listening. Click to stop");
      voiceButton.title = "Listening — click to stop";
      recognition.onresult = (event) => {
        const transcript = event.results?.[0]?.[0]?.transcript || "";
        if (transcript) sendMessage(transcript);
      };
      recognition.onerror = (event) => {
        if (event.error !== "aborted" && event.error !== "no-speech") {
          addMessage("I couldn't hear that clearly. Please try again or type your question.", "bot");
        }
      };
      recognition.onend = () => {
        activeRecognition = null;
        voiceButton.setAttribute("aria-label", "Speak a question");
        voiceButton.title = "Speak a question";
      };
      try {
        recognition.start();
      } catch (_error) {
        activeRecognition = null;
        voiceButton.setAttribute("aria-label", "Speak a question");
        voiceButton.title = "Speak a question";
        addMessage("Voice input couldn't start. You can type your question instead.", "bot");
      }
    });
  }
});

// Attendre que le DOM soit chargé
document.addEventListener("DOMContentLoaded", function () {
  // Éléments du DOM
  const chatMessages = document.getElementById("chat-messages");
  const questionInput = document.getElementById("question-input");
  const sendButton = document.getElementById("send-button");
  const clearButton = document.getElementById("clear-button");
  const suggestionChips = document.querySelectorAll(".suggestion-chip");

  // Animation d'entrée pour les éléments de la page
  setTimeout(() => {
    document.body.classList.add("loaded");
  }, 100);

  // Fonction pour ajouter une classe active aux messages pour les animations
  function activateMessages() {
    const messages = document.querySelectorAll(".message");
    messages.forEach((message, index) => {
      setTimeout(() => {
        message.classList.add("active");
      }, index * 150);
    });
  }
  activateMessages();

  // Gestion des suggestions cliquables
  suggestionChips.forEach((chip) => {
    chip.addEventListener("click", function () {
      const question = this.getAttribute("data-question");
      questionInput.value = question;

      // Animation de sélection
      this.classList.add("selected");
      setTimeout(() => {
        sendQuestion();
      }, 300);
    });
  });

  // Fonction pour ajouter un message au chat
  function addMessage(content, isUser = false) {
    // Créer une div pour le message
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${isUser ? "user" : "bot"}`;

    // Créer le conteneur de message
    const containerDiv = document.createElement("div");
    containerDiv.className = "message-container";

    // Créer le contenu du message
    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    // Gérer le HTML dans le contenu (pour la météo formatée)
    if (content.includes("<") && content.includes(">")) {
      contentDiv.innerHTML = content;
    } else {
      contentDiv.textContent = content;
    }

    // Assembler la structure
    containerDiv.appendChild(contentDiv);
    messageDiv.appendChild(containerDiv);
    chatMessages.appendChild(messageDiv);

    // Appliquer l'animation
    setTimeout(() => {
      messageDiv.classList.add("active");
    }, 10);

    // Faire défiler vers le bas
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageDiv;
  }

  // Fonction pour afficher l'indicateur de frappe
  function showTypingIndicator() {
    const typingDiv = document.createElement("div");
    typingDiv.className = "message bot typing";

    const containerDiv = document.createElement("div");
    containerDiv.className = "message-container";

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    const dotsDiv = document.createElement("div");
    dotsDiv.className = "typing-dots";

    for (let i = 0; i < 3; i++) {
      const dot = document.createElement("span");
      dot.className = "typing-dot";
      dotsDiv.appendChild(dot);
    }

    contentDiv.appendChild(dotsDiv);
    containerDiv.appendChild(contentDiv);
    typingDiv.appendChild(containerDiv);
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return typingDiv;
  }

  // Fonction pour supprimer l'indicateur de frappe
  function removeTypingIndicator() {
    const typing = document.querySelector(".typing");
    if (typing) {
      typing.remove();
    }
  }

  // Fonction pour ajouter des suggestions de questions
  function addSuggestions(suggestions) {
    if (!suggestions || suggestions.length === 0) return;

    // Créer le conteneur de suggestions
    const suggestionsDiv = document.createElement("div");
    suggestionsDiv.className = "suggestions-container";

    // Titre des suggestions
    const titleElement = document.createElement("p");
    titleElement.className = "suggestion-title";
    titleElement.textContent = "Suggestions:";
    suggestionsDiv.appendChild(titleElement);

    // Conteneur des puces de suggestions
    const chipsContainer = document.createElement("div");
    chipsContainer.className = "suggestions";

    // Créer chaque puce de suggestion
    suggestions.forEach((suggestion) => {
      const chip = document.createElement("div");
      chip.className = "suggestion-chip";
      chip.textContent = suggestion;
      chip.setAttribute("data-question", suggestion);

      // Ajouter l'événement de clic
      chip.addEventListener("click", function () {
        questionInput.value = this.getAttribute("data-question");
        this.classList.add("selected");
        setTimeout(() => {
          sendQuestion();
        }, 300);
      });

      chipsContainer.appendChild(chip);
    });

    suggestionsDiv.appendChild(chipsContainer);
    chatMessages.appendChild(suggestionsDiv);

    // Faire défiler vers le bas
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // Envoyer une question
  async function sendQuestion() {
    const question = questionInput.value.trim();
    if (question === "") return;

    // Cacher le guide de bienvenue
    const welcomeGuide = document.querySelector(".welcome-guide");
    if (welcomeGuide) {
      welcomeGuide.style.animation = "fadeOut 0.5s forwards";
      setTimeout(() => {
        welcomeGuide.remove();
      }, 500);
    }

    // Ajouter le message utilisateur
    addMessage(question, true);

    // Afficher l'indicateur de frappe
    const typingIndicator = showTypingIndicator();

    try {
      // Envoyer au serveur
      const response = await fetch("/question", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: question }),
      });

      // Vérifier la réponse
      if (!response.ok) {
        throw new Error("Erreur serveur");
      }

      // Traiter la réponse
      const data = await response.json();

      // Supprimer l'indicateur de frappe
      removeTypingIndicator();

      // Ajouter la réponse du bot
      addMessage(data.reponse);

      // Ajouter les suggestions si disponibles
      if (data.suggestions && data.suggestions.length > 0) {
        addSuggestions(data.suggestions);
      }
    } catch (error) {
      console.error("Erreur:", error);
      removeTypingIndicator();
      addMessage(
        "Désolé, une erreur est survenue lors du traitement de votre demande."
      );
    }

    // Réinitialiser l'input
    questionInput.value = "";
    questionInput.focus();
  }

  // Gestionnaire pour le bouton d'envoi
  sendButton.addEventListener("click", sendQuestion);

  // Gestionnaire pour la touche Entrée
  questionInput.addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
      sendQuestion();
    }
  });

  // Effet de focus sur l'input
  questionInput.addEventListener("focus", function () {
    document.querySelector(".chat-input").classList.add("focused");
  });

  questionInput.addEventListener("blur", function () {
    document.querySelector(".chat-input").classList.remove("focused");
  });

  // Gestionnaire pour le bouton d'effacement
  if (clearButton) {
    clearButton.addEventListener("click", function () {
      // Animation de suppression
      const messages = document.querySelectorAll(
        ".message, .suggestions-container"
      );
      messages.forEach((message, index) => {
        setTimeout(() => {
          message.style.animation = "fadeOut 0.3s forwards";
        }, index * 50);
      });

      // Effacer après animation
      setTimeout(() => {
        // Vider la zone de chat
        chatMessages.innerHTML = "";

        // Ajouter un message de bienvenue
        addMessage(
          "👋 Bonjour! Je suis Cindy, votre assistant IA personnelle. Comment puis-je vous aider aujourd'hui?"
        );

        // Ajouter des suggestions par défaut
        addSuggestions([
          "Quelle est la météo à Paris aujourd'hui?",
          "Quelle heure est-il?",
          "Comment vas-tu?",
        ]);
      }, messages.length * 50 + 300);
    });
  }

  // Focus sur l'input au chargement
  setTimeout(() => {
    questionInput.focus();
  }, 500);
});

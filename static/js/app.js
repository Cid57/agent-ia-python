/**
 * Application principale - Interface de chat avec l'agent IA
 * Version modernisée avec architecture modulaire et pratiques ES6+
 */

// Configuration de l'application
const CONFIG = {
  animationDuration: 300,
  typingIndicatorDelay: 500,
  messageScrollDelay: 100,
  maxSuggestions: 5,
};

// Attendre que le DOM soit complètement chargé avant d'initialiser
document.addEventListener("DOMContentLoaded", () => {
  // Initialisation de l'application
  ChatApp.init();
});

/**
 * Application principale structurée avec une architecture modulaire
 */
const ChatApp = (() => {
  // État de l'application
  const state = {
    isWaitingForResponse: false,
    darkModeEnabled: localStorage.getItem("darkMode") === "true",
    messageCount: 0,
  };

  // Éléments du DOM
  let elements = {};

  /**
   * Initialise l'application
   */
  const init = () => {
    // Récupération des éléments du DOM
    elements = {
      body: document.body,
      chatMessages: document.getElementById("chat-messages"),
      questionInput: document.getElementById("question-input"),
      sendButton: document.getElementById("send-button"),
      clearButton: document.getElementById("clear-button"),
      suggestionChips: document.querySelectorAll(".suggestion-chip"),
      chatContainer: document.querySelector(".chat-container"),
    };

    // Initialisation des événements
    setupEventListeners();

    // Animation d'entrée pour les éléments de la page
    setTimeout(() => {
      elements.body.classList.add("loaded");
    }, 100);

    // Activer les messages existants
    activateMessages();

    // Initialiser le mode sombre si nécessaire
    initThemeToggle();

    // Focus sur le champ de saisie
    elements.questionInput?.focus();
  };

  /**
   * Configure les écouteurs d'événements
   */
  const setupEventListeners = () => {
    // Gérer l'envoi du message
    elements.sendButton?.addEventListener("click", handleSendMessage);

    // Envoyer le message avec la touche Entrée
    elements.questionInput?.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        handleSendMessage();
      }
    });

    // Gérer le clic sur le bouton d'effacement
    elements.clearButton?.addEventListener("click", clearChat);

    // Gérer les suggestions cliquables
    elements.suggestionChips.forEach((chip) => {
      chip.addEventListener("click", handleSuggestionClick);
    });
  };

  /**
   * Gère le clic sur une suggestion
   * @param {Event} event - L'événement de clic
   */
  const handleSuggestionClick = function () {
    const question = this.getAttribute("data-question");

    if (!question) return;

    // Mettre à jour le champ de saisie
    elements.questionInput.value = question;

    // Animation de sélection
    this.classList.add("selected");

    // Envoyer la question après un court délai
    setTimeout(() => {
      handleSendMessage();
    }, CONFIG.animationDuration);
  };

  /**
   * Gère l'envoi d'un message
   */
  const handleSendMessage = () => {
    const question = elements.questionInput.value.trim();

    // Ne rien faire si le champ est vide ou si on attend déjà une réponse
    if (!question || state.isWaitingForResponse) return;

    // Envoyer la question au serveur
    sendQuestion(question);

    // Vider le champ de saisie
    elements.questionInput.value = "";
  };

  /**
   * Active l'animation des messages existants
   */
  const activateMessages = () => {
    const messages = document.querySelectorAll(".message");

    messages.forEach((message, index) => {
      setTimeout(() => {
        message.classList.add("active");
      }, index * 150);
    });
  };

  /**
   * Ajoute un message au chat
   * @param {string} content - Le contenu du message
   * @param {boolean} isUser - Indique si le message vient de l'utilisateur
   * @returns {HTMLElement} - L'élément du message créé
   */
  const addMessage = (content, isUser = false) => {
    // Créer la structure du message
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${isUser ? "user" : "bot"}`;

    const containerDiv = document.createElement("div");
    containerDiv.className = "message-container";

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    // Gérer le HTML dans le contenu (pour le contenu formaté)
    if (content.includes("<") && content.includes(">")) {
      contentDiv.innerHTML = content;
    } else {
      // Convertir les sauts de ligne en paragraphes
      const paragraphs = content.split("\n").filter((p) => p.trim() !== "");

      if (paragraphs.length > 1) {
        paragraphs.forEach((paragraph) => {
          const p = document.createElement("p");
          p.textContent = paragraph;
          contentDiv.appendChild(p);
        });
      } else {
        contentDiv.textContent = content;
      }
    }

    // Assembler la structure
    containerDiv.appendChild(contentDiv);
    messageDiv.appendChild(containerDiv);
    elements.chatMessages.appendChild(messageDiv);

    // Appliquer l'animation
    setTimeout(() => {
      messageDiv.classList.add("active");
    }, 10);

    // Faire défiler vers le bas
    scrollToBottom();

    // Incrémenter le compteur de messages
    state.messageCount++;

    return messageDiv;
  };

  /**
   * Fait défiler la fenêtre de chat vers le bas
   */
  const scrollToBottom = () => {
    setTimeout(() => {
      elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    }, CONFIG.messageScrollDelay);
  };

  /**
   * Affiche l'indicateur de frappe
   * @returns {HTMLElement} - L'élément d'indication de frappe
   */
  const showTypingIndicator = () => {
    const typingDiv = document.createElement("div");
    typingDiv.className = "message bot typing";

    const containerDiv = document.createElement("div");
    containerDiv.className = "message-container";

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    const dotsDiv = document.createElement("div");
    dotsDiv.className = "typing-dots";

    // Créer les points d'animation
    for (let i = 0; i < 3; i++) {
      const dot = document.createElement("span");
      dot.className = "typing-dot";
      dotsDiv.appendChild(dot);
    }

    // Assembler la structure
    contentDiv.appendChild(dotsDiv);
    containerDiv.appendChild(contentDiv);
    typingDiv.appendChild(containerDiv);
    elements.chatMessages.appendChild(typingDiv);

    // Faire défiler vers le bas
    scrollToBottom();

    return typingDiv;
  };

  /**
   * Supprime l'indicateur de frappe
   */
  const removeTypingIndicator = () => {
    const typingIndicator = document.querySelector(".typing");
    if (typingIndicator) {
      typingIndicator.remove();
    }
  };

  /**
   * Ajoute des suggestions de questions
   * @param {Array} suggestions - Liste des suggestions à afficher
   */
  const addSuggestions = (suggestions) => {
    if (!suggestions || !suggestions.length) return;

    // Limiter le nombre de suggestions
    const limitedSuggestions = suggestions.slice(0, CONFIG.maxSuggestions);

    // Créer le conteneur de suggestions
    const suggestionsDiv = document.createElement("div");
    suggestionsDiv.className = "message bot suggestions-message";

    const containerDiv = document.createElement("div");
    containerDiv.className = "message-container";

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    const suggestionsContainer = document.createElement("div");
    suggestionsContainer.className = "suggestions";

    // Ajouter le titre
    const titleP = document.createElement("p");
    titleP.textContent = "Vous pourriez aussi demander :";
    contentDiv.appendChild(titleP);

    // Créer les puces de suggestions
    limitedSuggestions.forEach((suggestion) => {
      const chip = document.createElement("div");
      chip.className = "suggestion-chip";
      chip.textContent = suggestion;
      chip.setAttribute("data-question", suggestion);

      // Ajouter l'événement de clic
      chip.addEventListener("click", function () {
        elements.questionInput.value = this.getAttribute("data-question");
        this.classList.add("selected");

        setTimeout(() => {
          handleSendMessage();
        }, CONFIG.animationDuration);
      });

      suggestionsContainer.appendChild(chip);
    });

    // Assembler la structure
    contentDiv.appendChild(suggestionsContainer);
    containerDiv.appendChild(contentDiv);
    suggestionsDiv.appendChild(containerDiv);
    elements.chatMessages.appendChild(suggestionsDiv);

    // Appliquer l'animation
    setTimeout(() => {
      suggestionsDiv.classList.add("active");
    }, 10);

    // Faire défiler vers le bas
    scrollToBottom();
  };

  /**
   * Envoie une question au serveur
   * @param {string} question - La question à envoyer
   */
  const sendQuestion = async (question) => {
    if (!question || state.isWaitingForResponse) return;

    // Mettre à jour l'état
    state.isWaitingForResponse = true;

    // Ajouter le message de l'utilisateur
    addMessage(question, true);

    // Afficher l'indicateur de frappe
    const typingIndicator = showTypingIndicator();

    try {
      // Détection de différents types de messages
      const trimmedQuestion = question.trim().toLowerCase();
      const isSalutation =
        /^(bonjour|salut|coucou|hello|hey|hi|bonsoir|yo)$/i.test(
          trimmedQuestion
        );
      const isIdentityQuestion =
        /(qui es[- ]tu|tu es qui|t'es qui|quel est ton nom|comment t'appelles[- ]tu|présente[- ]toi)/.test(
          trimmedQuestion
        );
      const isCapabilityQuestion =
        /(que sais[- ]tu faire|quelles sont tes capacités|que peux[- ]tu faire|capacités|fonctionnalités|aide[- ]moi)/.test(
          trimmedQuestion
        );

      // Format de la requête
      const requestData = {
        question: question,
      };

      // Si c'est une question standard, on pourrait aussi indiquer un type
      if (isSalutation) requestData.type = "greeting";
      if (isIdentityQuestion) requestData.type = "identity";
      if (isCapabilityQuestion) requestData.type = "capability";

      const requestOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestData),
      };

      // Envoi de la requête au serveur
      const response = await fetch("/question", requestOptions);

      // Traiter selon le type de question si le serveur ne répond pas correctement
      if (!response.ok) {
        // Si le serveur renvoie une erreur, on gère localement
        if (isSalutation) {
          removeTypingIndicator();
          addMessage("Bonjour ! Comment puis-je vous aider aujourd'hui ?");
          return;
        } else if (isIdentityQuestion) {
          removeTypingIndicator();
          addMessage(
            "Je suis Cindy, votre assistant IA personnel. Je suis là pour répondre à vos questions et vous aider dans vos tâches quotidiennes."
          );
          return;
        } else if (isCapabilityQuestion) {
          removeTypingIndicator();
          addMessage(
            "Je peux répondre à vos questions, vous donner des informations sur divers sujets, vous aider à trouver des informations, et bien plus encore. N'hésitez pas à me demander ce dont vous avez besoin !"
          );
          return;
        } else {
          throw new Error(`Erreur réseau: ${response.status}`);
        }
      }

      // Traiter la réponse
      const data = await response.json();

      // Supprimer l'indicateur de frappe
      removeTypingIndicator();

      // Vérifier si la réponse contient une erreur
      if (
        !data.reponse ||
        data.reponse.includes("erreur") ||
        data.reponse.includes("Désolé")
      ) {
        // Réponses de secours selon le type de question
        if (isSalutation) {
          addMessage("Bonjour ! Comment puis-je vous aider aujourd'hui ?");
        } else if (isIdentityQuestion) {
          addMessage(
            "Je suis Cindy, votre assistant IA personnel. Je suis là pour répondre à vos questions et vous aider dans vos tâches quotidiennes."
          );
        } else if (isCapabilityQuestion) {
          addMessage(
            "Je peux répondre à vos questions, vous donner des informations sur divers sujets, vous aider à trouver des informations, et bien plus encore. N'hésitez pas à me demander ce dont vous avez besoin !"
          );
        } else {
          // Pour les autres types de questions, on montre l'erreur
          addMessage(
            data.reponse ||
              "Désolé, une erreur est survenue lors du traitement de votre demande. Veuillez réessayer."
          );
        }
      } else {
        // Ajouter la réponse au chat si tout va bien
        addMessage(data.reponse);
      }

      // Ajouter des suggestions si disponibles
      if (data.suggestions && data.suggestions.length > 0) {
        setTimeout(() => {
          addSuggestions(data.suggestions);
        }, CONFIG.typingIndicatorDelay);
      } else if (isCapabilityQuestion) {
        // Suggestions par défaut pour les questions sur les capacités
        setTimeout(() => {
          addSuggestions([
            "Quelle est la météo à Paris ?",
            "Raconte-moi une blague",
            "Quelle heure est-il ?",
            "Qui a inventé Internet ?",
          ]);
        }, CONFIG.typingIndicatorDelay);
      }
    } catch (error) {
      console.error("Erreur lors de l'envoi de la question:", error);

      // Supprimer l'indicateur de frappe
      removeTypingIndicator();

      // Réponses de secours en cas d'erreur
      const trimmedQuestion = question.trim().toLowerCase();

      if (
        /^(bonjour|salut|coucou|hello|hey|hi|bonsoir|yo)$/i.test(
          trimmedQuestion
        )
      ) {
        addMessage("Bonjour ! Comment puis-je vous aider aujourd'hui ?");
      } else if (
        /(qui es[- ]tu|tu es qui|t'es qui|quel est ton nom|comment t'appelles[- ]tu|présente[- ]toi)/.test(
          trimmedQuestion
        )
      ) {
        addMessage(
          "Je suis Cindy, votre assistant IA personnel. Je suis là pour répondre à vos questions et vous aider dans vos tâches quotidiennes."
        );
      } else if (
        /(que sais[- ]tu faire|quelles sont tes capacités|que peux[- ]tu faire|capacités|fonctionnalités|aide[- ]moi)/.test(
          trimmedQuestion
        )
      ) {
        addMessage(
          "Je peux répondre à vos questions, vous donner des informations sur divers sujets, vous aider à trouver des informations, et bien plus encore. N'hésitez pas à me demander ce dont vous avez besoin !"
        );
      } else {
        // Message d'erreur générique pour les autres questions
        addMessage(
          "Désolé, une erreur est survenue lors du traitement de votre demande. Veuillez réessayer avec une formulation différente."
        );
      }
    } finally {
      // Réinitialiser l'état
      state.isWaitingForResponse = false;
    }
  };

  /**
   * Efface l'historique du chat
   */
  const clearChat = () => {
    // Animation de sortie pour les messages
    const messages = document.querySelectorAll(".message");

    messages.forEach((message, index) => {
      setTimeout(() => {
        message.style.opacity = "0";
        message.style.transform = "translateY(10px)";
      }, index * 50);
    });

    // Supprimer les messages après l'animation
    setTimeout(() => {
      elements.chatMessages.innerHTML = "";

      // Ajouter un nouveau message de bienvenue
      const welcomeMessage =
        "Bonjour! Je suis Cindy, votre assistant IA. Comment puis-je vous aider aujourd'hui?";
      addMessage(welcomeMessage);

      // Réinitialiser le compteur de messages
      state.messageCount = 1;
    }, messages.length * 50 + 300);
  };

  /**
   * Initialise le basculement de thème (clair/sombre)
   */
  const initThemeToggle = () => {
    // Appliquer le thème sombre si nécessaire
    if (state.darkModeEnabled) {
      document.body.classList.add("dark-mode");
    }

    // Créer le bouton de basculement si nécessaire
    if (!document.getElementById("theme-toggle")) {
      const themeToggle = document.createElement("button");
      themeToggle.id = "theme-toggle";
      themeToggle.className = "secondary-button";
      themeToggle.textContent = state.darkModeEnabled
        ? "☀️ Mode clair"
        : "🌙 Mode sombre";
      themeToggle.addEventListener("click", toggleDarkMode);

      // Ajouter le bouton au conteneur d'actions
      const actionsContainer = document.querySelector(".actions");
      if (actionsContainer) {
        actionsContainer.insertBefore(themeToggle, actionsContainer.firstChild);
      }
    }
  };

  /**
   * Bascule entre les modes clair et sombre
   */
  const toggleDarkMode = () => {
    // Mettre à jour l'état
    state.darkModeEnabled = !state.darkModeEnabled;

    // Enregistrer la préférence
    localStorage.setItem("darkMode", state.darkModeEnabled);

    // Appliquer ou supprimer la classe de mode sombre
    document.body.classList.toggle("dark-mode");

    // Mettre à jour le texte du bouton
    const themeToggle = document.getElementById("theme-toggle");
    if (themeToggle) {
      themeToggle.textContent = state.darkModeEnabled
        ? "☀️ Mode clair"
        : "🌙 Mode sombre";
    }

    // Animation de transition
    elements.chatContainer.style.transition =
      "background-color 0.5s ease, box-shadow 0.5s ease";
    setTimeout(() => {
      elements.chatContainer.style.transition = "";
    }, 500);
  };

  // API publique du module
  return {
    init,
    addMessage,
    clearChat,
    toggleDarkMode,
  };
})();

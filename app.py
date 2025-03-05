"""
Application web pour notre Agent IA
Ce module contient l'application web Flask qui expose notre agent IA.
"""

from flask import Flask, render_template, request, jsonify, session
from agent import Agent
from nlp_utils import AnalyseurTexte
from memory import Memoire
import os
import time
import secrets
import logging
import sys

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('assistant_ia')

# Créer les instances de nos classes
agent = Agent(nom="Cindy")
analyseur = AnalyseurTexte()
memoire = Memoire()

# Initialiser l'application Flask
app = Flask(__name__)
# Clé secrète pour les sessions
app.secret_key = secrets.token_hex(16)

# S'assurer que les dossiers templates et static existent
try:
    for directory in ['templates', 'static', 'static/css', 'static/js', 'static/images']:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), directory)
        os.makedirs(path, exist_ok=True)
        logger.debug(f"Dossier {directory} vérifié")
except Exception as e:
    logger.error(f"Erreur lors de la création des dossiers: {e}")

# Gestionnaire d'erreurs pour les erreurs 404 (page non trouvée)
@app.errorhandler(404)
def page_not_found(e):
    logger.error(f"Page non trouvée: {request.path}")
    return render_template('error.html', 
                          error_message="Page non trouvée",
                          error_details="La page que vous recherchez n'existe pas."), 404

# Gestionnaire d'erreurs pour les erreurs 500 (erreur serveur)
@app.errorhandler(500)
def server_error(e):
    logger.error(f"Erreur serveur: {str(e)}")
    return render_template('error.html', 
                          error_message="Erreur serveur",
                          error_details="Une erreur s'est produite sur le serveur. Veuillez réessayer plus tard."), 500

@app.route('/')
def index():
    """Page d'accueil de l'application."""
    # Générer un identifiant de session unique si inexistant
    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(8)
        session['first_visit'] = True
    else:
        session['first_visit'] = False
    
    return render_template('index.html', first_visit=session.get('first_visit', True))

@app.route('/poser_question', methods=['POST'])
def poser_question():
    """Endpoint pour poser une question à l'agent."""
    try:
        # Récupérer les données de la requête
        donnees = request.get_json()
        question = donnees.get('question', '')
        
        # Vérifier si la question est vide
        if not question:
            return jsonify({
                'reponse': 'Je n\'ai pas compris votre question. Pouvez-vous reformuler?',
                'status': 'error'
            })
        
        # Ajouter un petit délai pour simuler un temps de traitement
        # et donner une impression plus naturelle
        time.sleep(0.5)
        
        # Analyser la question avec notre module NLP
        mots_cles = analyseur.extraire_mots_cles(question)
        
        # Ajouter la question à la mémoire
        memoire.ajouter_souvenir("question", question)
        
        # Générer une réponse avec notre agent
        reponse = agent.generer_reponse(question)
        
        # Ajouter la réponse à la mémoire
        memoire.ajouter_souvenir("reponse", reponse)
        
        # Si la réponse semble être une information factuelle, la sauvegarder
        if any(mot in question.lower() for mot in ["qu'est-ce", "définition", "explique", "comment"]):
            # On sauvegarde seulement les réponses qui ne sont pas des réponses par défaut
            if "Je ne comprends pas encore cette question" not in reponse:
                memoire.sauvegarder_memoire_long_terme("connaissances", f"Question: {question} | Réponse: {reponse}")
        
        # Retourner la réponse au format JSON
        return jsonify({
            'reponse': reponse,
            'mots_cles': mots_cles,
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la question: {e}")
        return jsonify({
            'reponse': 'Une erreur est survenue lors du traitement de votre question. Veuillez réessayer.',
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/historique')
def historique():
    """Page affichant l'historique des conversations."""
    try:
        # Récupérer tout l'historique récent
        historique_brut = memoire.obtenir_contexte_recent(nombre=20)
        
        # Formater l'historique pour le nouveau template
        historique_formate = []
        
        # Regrouper les questions et réponses par paires
        i = 0
        while i < len(historique_brut):
            if i + 1 < len(historique_brut) and historique_brut[i]['type'] == 'question' and historique_brut[i+1]['type'] == 'reponse':
                # Créer une paire question-réponse
                historique_formate.append({
                    'question': historique_brut[i]['contenu'],
                    'reponse': historique_brut[i+1]['contenu'],
                    'timestamp': historique_brut[i]['timestamp']
                })
                i += 2  # Avancer de deux éléments
            else:
                # Si on ne peut pas faire une paire, ajouter juste l'élément actuel
                element_type = historique_brut[i]['type']
                historique_formate.append({
                    'question': historique_brut[i]['contenu'] if element_type == 'question' else "",
                    'reponse': historique_brut[i]['contenu'] if element_type == 'reponse' else "Pas de réponse enregistrée",
                    'timestamp': historique_brut[i]['timestamp']
                })
                i += 1
        
        return render_template('historique.html', historique=historique_formate)
    except Exception as e:
        logger.error(f"Erreur lors de l'affichage de l'historique: {e}")
        return render_template('error.html', 
                              error_message="Erreur d'accès à l'historique",
                              error_details="Impossible d'accéder à l'historique des conversations."), 500

@app.route('/effacer_historique', methods=['POST'])
def effacer_historique():
    """Endpoint pour effacer l'historique des conversations."""
    try:
        # Effacer complètement la mémoire à court terme
        memoire.memoire_court_terme = []
        logger.info("Historique effacé avec succès")
        
        return jsonify({
            'status': 'success',
            'message': 'Historique effacé avec succès.'
        })
    except Exception as e:
        logger.error(f"Erreur lors de l'effacement de l'historique: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de l\'effacement de l\'historique: {str(e)}'
        }), 500

@app.route('/aide')
def aide():
    """Page d'aide expliquant les fonctionnalités de l'agent."""
    return render_template('aide.html')

# Fonction pour créer les fichiers de template s'ils n'existent pas
def creer_fichiers_template():
    """Crée les fichiers de template et statiques si nécessaire."""
    try:
        # Vérifier et créer les fichiers template
        templates = {
            'index.html': """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent IA - Assistant</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link rel="icon" href="{{ url_for('static', filename='images/favicon.ico') }}" type="image/x-icon">
</head>
<body>
    <div class="container">
        <header>
            <h1>Mon Assistant IA</h1>
            <p>Posez-moi vos questions, je suis là pour vous aider!</p>
            <nav>
                <a href="/historique">Historique</a> |
                <a href="/aide">Aide</a>
            </nav>
        </header>
        
        <main>
            <div class="chat-container">
                <div id="chat-messages">
                    {% if first_visit %}
                    <div class="message bot">
                        <div class="message-content">
                            Bonjour! Je suis votre assistant IA. Comment puis-je vous aider aujourd'hui?
                        </div>
                    </div>
                    {% endif %}
                </div>
                
                <div class="chat-input">
                    <input type="text" id="question-input" placeholder="Posez votre question ici...">
                    <button id="send-button">Envoyer</button>
                </div>
            </div>
            
            <div class="actions">
                <button id="clear-button" class="secondary-button">Effacer la conversation</button>
            </div>
        </main>
        
        <footer>
            <p>Agent IA - Version 1.1 - Développé avec Python et Flask</p>
        </footer>
    </div>
    
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
</body>
</html>""",
            'historique.html': """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent IA - Historique</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link rel="icon" href="{{ url_for('static', filename='images/favicon.ico') }}" type="image/x-icon">
</head>
<body>
    <div class="container">
        <header>
            <h1>Historique des Conversations</h1>
            <p><a href="/">Retour à l'accueil</a></p>
        </header>
        
        <main>
            <div class="historique-container">
                {% if historique %}
                    {% for item in historique %}
                        <div class="historique-item {% if item.type == 'question' %}question{% else %}reponse{% endif %}">
                            <div class="timestamp">{{ item.timestamp }}</div>
                            <div class="content">
                                <strong>{% if item.type == 'question' %}Question{% else %}Réponse{% endif %}:</strong> 
                                {{ item.contenu }}
                            </div>
                        </div>
                    {% endfor %}
                {% else %}
                    <p>Aucun historique disponible pour le moment.</p>
                {% endif %}
            </div>
        </main>
        
        <footer>
            <p>Agent IA - Version 1.1 - Développé avec Python et Flask</p>
        </footer>
    </div>
</body>
</html>""",
            'aide.html': """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent IA - Aide</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link rel="icon" href="{{ url_for('static', filename='images/favicon.ico') }}" type="image/x-icon">
</head>
<body>
    <div class="container">
        <header>
            <h1>Aide - Comment utiliser l'Agent IA</h1>
            <p><a href="/">Retour à l'accueil</a></p>
        </header>
        
        <main>
            <div class="aide-container">
                <h2>Que peut faire cet agent IA ?</h2>
                <p>Cet assistant IA est conçu pour répondre à vos questions et interagir avec vous de manière simple. Voici les différentes catégories de questions auxquelles il peut répondre :</p>
                
                {% for capacite in capacites %}
                <div class="capacite-section">
                    <h3>{{ capacite.categorie }}</h3>
                    <div class="exemples">
                        <p>Exemples :</p>
                        <ul>
                            {% for exemple in capacite.exemples %}
                            <li>{{ exemple }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
                {% endfor %}
                
                <h2>Comment ça marche ?</h2>
                <p>L'agent utilise des techniques simples de traitement du langage naturel pour comprendre vos questions et y répondre. Il identifie les mots-clés dans votre message et génère une réponse appropriée.</p>
                
                <h2>Confidentialité</h2>
                <p>Vos conversations sont stockées temporairement dans la mémoire de l'application. Vous pouvez effacer l'historique à tout moment en cliquant sur le bouton "Effacer la conversation" sur la page d'accueil.</p>
            </div>
        </main>
        
        <footer>
            <p>Agent IA - Version 1.1 - Développé avec Python et Flask</p>
        </footer>
    </div>
</body>
</html>"""
        }
        
        # Créer les fichiers template s'ils n'existent pas
        for filename, content in templates.items():
            filepath = os.path.join('templates', filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Fichier {filepath} créé")
        
        # Créer les fichiers CSS et JavaScript
        css_file = os.path.join('static', 'css', 'style.css')
        if not os.path.exists(css_file):
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write("""/* Style général */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

body {
    background-color: #f5f7fa;
    color: #333;
    line-height: 1.6;
}

.container {
    width: 90%;
    max-width: 1000px;
    margin: 0 auto;
    padding: 20px;
}

/* En-tête */
header {
    text-align: center;
    margin-bottom: 30px;
    padding: 20px 0;
    border-bottom: 1px solid #e1e4e8;
}

header h1 {
    color: #2c3e50;
    margin-bottom: 10px;
    font-size: 2.2rem;
}

header p {
    color: #7f8c8d;
    font-size: 1.1rem;
    margin-bottom: 15px;
}

header nav {
    margin-top: 10px;
}

header nav a {
    color: #3498db;
    text-decoration: none;
    margin: 0 10px;
    font-weight: 500;
    transition: color 0.3s;
}

header nav a:hover {
    color: #2980b9;
    text-decoration: underline;
}

/* Zone de chat */
.chat-container {
    background-color: #fff;
    border-radius: 12px;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    height: 70vh;
    display: flex;
    flex-direction: column;
    border: 1px solid #e1e8ed;
}

#chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    scroll-behavior: smooth;
}

.message {
    margin-bottom: 15px;
    display: flex;
    animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.message.user {
    justify-content: flex-end;
}

.message-content {
    padding: 12px 16px;
    border-radius: 18px;
    max-width: 70%;
    word-wrap: break-word;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.user .message-content {
    background-color: #4c84ff;
    color: white;
    border-bottom-right-radius: 4px;
}

.bot .message-content {
    background-color: #f1f1f1;
    color: #333;
    border-bottom-left-radius: 4px;
}

.chat-input {
    display: flex;
    padding: 15px;
    background-color: #f9f9f9;
    border-top: 1px solid #e1e4e8;
}

#question-input {
    flex: 1;
    padding: 12px 16px;
    border: 1px solid #ddd;
    border-radius: 24px;
    font-size: 16px;
    outline: none;
    transition: border-color 0.3s, box-shadow 0.3s;
}

#question-input:focus {
    border-color: #4c84ff;
    box-shadow: 0 0 0 2px rgba(76, 132, 255, 0.2);
}

#send-button {
    margin-left: 10px;
    padding: 0 20px;
    background-color: #4c84ff;
    color: white;
    border: none;
    border-radius: 24px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 500;
    transition: background-color 0.3s, transform 0.1s;
}

#send-button:hover {
    background-color: #3a6fdf;
}

#send-button:active {
    transform: scale(0.98);
}

/* Actions */
.actions {
    display: flex;
    justify-content: center;
    margin-top: 20px;
}

.secondary-button {
    background-color: #f1f1f1;
    color: #555;
    border: 1px solid #ddd;
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 14px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.secondary-button:hover {
    background-color: #e5e5e5;
}

/* Historique */
.historique-container {
    background-color: #fff;
    border-radius: 12px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    padding: 20px;
    margin-bottom: 30px;
}

.historique-item {
    margin-bottom: 15px;
    padding: 15px;
    border-radius: 8px;
    transition: transform 0.2s;
}

.historique-item:hover {
    transform: translateX(5px);
}

.historique-item.question {
    background-color: #f1f8ff;
    border-left: 4px solid #4c84ff;
}

.historique-item.reponse {
    background-color: #f8f8f8;
    border-left: 4px solid #34c759;
    margin-left: 20px;
}

.timestamp {
    color: #777;
    font-size: 14px;
    margin-bottom: 5px;
}

/* Page d'aide */
.aide-container {
    background-color: #fff;
    border-radius: 12px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    padding: 25px;
}

.aide-container h2 {
    color: #2c3e50;
    margin: 20px 0 10px 0;
    border-bottom: 1px solid #eee;
    padding-bottom: 8px;
}

.aide-container h3 {
    color: #3498db;
    margin: 15px 0 10px 0;
}

.capacite-section {
    background-color: #f9f9f9;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;
}

.exemples {
    margin-top: 10px;
}

.exemples ul {
    margin-left: 20px;
}

.exemples li {
    margin: 5px 0;
}

/* Animation de points de chargement */
.typing {
    display: flex;
    align-items: center;
    margin: 10px 0;
}

.typing-dots {
    display: flex;
}

.typing-dot {
    width: 8px;
    height: 8px;
    background-color: #aaa;
    border-radius: 50%;
    margin: 0 3px;
    animation: typingAnimation 1.5s infinite ease-in-out;
}

.typing-dot:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typingAnimation {
    0%, 60%, 100% { transform: translateY(0); }
    30% { transform: translateY(-5px); }
}

/* Pied de page */
footer {
    text-align: center;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #e1e4e8;
    color: #777;
}

footer a {
    color: #4c84ff;
    text-decoration: none;
}

footer a:hover {
    text-decoration: underline;
}

/* Responsive */
@media (max-width: 768px) {
    .message-content {
        max-width: 85%;
    }
    
    header h1 {
        font-size: 1.8rem;
    }
    
    .chat-container {
        height: 60vh;
    }
}

@media (max-width: 480px) {
    .container {
        width: 95%;
        padding: 10px;
    }
    
    .message-content {
        max-width: 90%;
    }
    
    #send-button {
        padding: 0 15px;
    }
}
""")
                logger.info("Fichier CSS créé")
        
        js_file = os.path.join('static', 'js', 'app.js')
        if not os.path.exists(js_file):
            with open(js_file, 'w', encoding='utf-8') as f:
                f.write("""// Attendre que le DOM soit chargé
document.addEventListener('DOMContentLoaded', function() {
    // Éléments du DOM
    const chatMessages = document.getElementById('chat-messages');
    const questionInput = document.getElementById('question-input');
    const sendButton = document.getElementById('send-button');
    const clearButton = document.getElementById('clear-button');
    
    // Fonction pour ajouter un message au chat
    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;
        
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        // Faire défiler vers le bas pour voir le dernier message
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Fonction pour afficher l'animation de chargement
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot typing';
        typingDiv.id = 'typing-indicator';
        
        const typingContent = document.createElement('div');
        typingContent.className = 'message-content';
        
        const typingDots = document.createElement('div');
        typingDots.className = 'typing-dots';
        
        // Créer les trois points d'animation
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'typing-dot';
            typingDots.appendChild(dot);
        }
        
        typingContent.appendChild(typingDots);
        typingDiv.appendChild(typingContent);
        chatMessages.appendChild(typingDiv);
        
        // Faire défiler vers le bas
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Fonction pour supprimer l'animation de chargement
    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    // Fonction pour envoyer une question à l'API
    async function sendQuestion(question) {
        try {
            // Désactiver le bouton pendant l'envoi
            sendButton.disabled = true;
            questionInput.disabled = true;
            
            // Afficher l'indicateur de frappe
            showTypingIndicator();
            
            // Envoyer la requête au serveur
            const response = await fetch('/poser_question', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: question })
            });
            
            // Vérifier si la requête a réussi
            if (!response.ok) {
                throw new Error('Erreur réseau');
            }
            
            // Analyser la réponse JSON
            const data = await response.json();
            
            // Supprimer l'indicateur de frappe
            removeTypingIndicator();
            
            // Ajouter la réponse de l'agent au chat
            addMessage(data.reponse);
        } catch (error) {
            console.error('Erreur:', error);
            removeTypingIndicator();
            addMessage('Désolé, une erreur est survenue lors du traitement de votre demande.');
        } finally {
            // Réactiver le bouton et l'input
            sendButton.disabled = false;
            questionInput.disabled = false;
            questionInput.focus();
        }
    }
    
    // Gérer l'envoi de question lorsque le bouton est cliqué
    sendButton.addEventListener('click', function() {
        const question = questionInput.value.trim();
        
        if (question !== '') {
            // Ajouter la question au chat
            addMessage(question, true);
            
            // Envoyer la question à l'API
            sendQuestion(question);
            
            // Effacer l'input
            questionInput.value = '';
        }
    });
    
    // Gérer l'envoi de question lorsque la touche Entrée est pressée
    questionInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendButton.click();
        }
    });
    
    // Gérer le clic sur le bouton d'effacement
    if (clearButton) {
        clearButton.addEventListener('click', async function() {
            // Demander confirmation
            if (confirm('Voulez-vous vraiment effacer toute la conversation ?')) {
                try {
                    // Envoyer la requête pour effacer l'historique
                    const response = await fetch('/effacer_historique', {
                        method: 'POST'
                    });
                    
                    if (!response.ok) {
                        throw new Error('Erreur lors de l\\'effacement de l\\'historique');
                    }
                    
                    // Vider la zone de chat sauf le message de bienvenue
                    chatMessages.innerHTML = '<div class="message bot"><div class="message-content">Conversation effacée. Comment puis-je vous aider maintenant ?</div></div>';
                    
                } catch (error) {
                    console.error('Erreur:', error);
                    alert('Erreur lors de l\\'effacement de l\\'historique');
                }
            }
        });
    }
    
    // Mettre le focus sur l'input au chargement
    questionInput.focus();
});
""")
                logger.info("Fichier JavaScript créé")
        
        logger.info("Tous les fichiers template et statiques ont été vérifiés et créés si nécessaire")
    except Exception as e:
        logger.error(f"Erreur lors de la création des fichiers template: {e}")

# Lancer l'application si ce fichier est exécuté directement
if __name__ == '__main__':
    # Créer les fichiers de template s'ils n'existent pas
    creer_fichiers_template()
    
    print("Agent AssistantIA initialisé et prêt à l'emploi!")
    
    try:
        logger.info("Démarrage du serveur Assistant IA...")
        # Lancer l'application Flask avec une configuration robuste
        # threaded=True permet de gérer plusieurs requêtes simultanément
        # use_reloader=True permet de recharger automatiquement l'application quand le code change
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True, use_reloader=True)
    except KeyboardInterrupt:
        logger.info("Arrêt du serveur par l'utilisateur.")
    except Exception as e:
        logger.error(f"Erreur lors du démarrage du serveur: {e}")
        print(f"Erreur: {e}")
        print("Pour redémarrer le serveur, exécutez à nouveau la commande: python app.py") 
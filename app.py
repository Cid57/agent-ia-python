"""
Application Flask pour l'assistant intelligent Cindy
Ce module est le point d'entrée de l'application web.
"""

import os
import logging
from flask import Flask, render_template, request, jsonify
from agent import Agent

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("assistant.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('assistant_ia.app')

# Initialisation de l'application Flask
app = Flask(__name__)

# Création de l'agent
agent = Agent(nom="Cindy")

@app.route('/')
def accueil():
    """Route principale qui affiche l'interface de chat"""
    return render_template('index.html')

@app.route('/historique')
def historique():
    """Route qui affiche l'historique des conversations"""
    historique_recents = agent.obtenir_historique(limite=20)
    stats = agent.obtenir_statistiques()
    return render_template('historique.html', historique=historique_recents, stats=stats)

@app.route('/aide')
def aide():
    """Route qui affiche la page d'aide"""
    return render_template('aide.html')

@app.route('/question', methods=['POST'])
def question():
    """
    API pour poser une question à l'agent
    Reçoit la question dans le corps de la requête et retourne la réponse
    """
    try:
        # Récupérer la question depuis la requête
        donnees = request.get_json()
        question = donnees.get('question', '')
        
        if not question:
            return jsonify({"erreur": "Aucune question fournie"}), 400
        
        logger.info(f"Question reçue: {question}")
        
        # Utiliser l'agent pour générer une réponse
        resultat = agent.generer_reponse(question)
        
        # Construire la réponse JSON avec la réponse et les suggestions
        reponse = {
            "reponse": resultat["reponse"],
            "suggestions": resultat.get("suggestions", [])
        }
        
        logger.info(f"Réponse envoyée: {resultat['reponse']}")
        return jsonify(reponse)
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la question: {str(e)}", exc_info=True)
        return jsonify({"erreur": "Une erreur est survenue lors du traitement de votre question."}), 500

# Pour la compatibilité, garder aussi l'ancienne route
@app.route('/api/question', methods=['POST'])
def poser_question():
    """Redirection vers la route principale question()"""
    return question()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)  # debug=False pour la production
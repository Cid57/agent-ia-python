"""
Application Agent Personnel avec compréhension améliorée du langage naturel
"""

import time
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from external_services import MeteoService
from nlp_engine import analyser_et_repondre

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("agent")

# Initialiser l'application Flask
app = Flask(__name__)

# Créer une instance du service météo
meteo_service = MeteoService()

# Liste des suggestions par défaut
SUGGESTIONS_DEFAUT = [
    "Quelle est la météo à Paris ?",
    "Quelle heure est-il ?",
    "Comment vas-tu ?"
]

def poser_question(question):
    """
    Fonction principale qui analyse la question de l'utilisateur et génère une réponse.
    Utilise le moteur NLP amélioré et le service météo.
    
    Args:
        question (str): La question posée par l'utilisateur
        
    Returns:
        dict: Réponse formatée avec suggestions
    """
    try:
        # Vérifier si la question est valide
        if not question or not isinstance(question, str) or question.strip() == "":
            return {
                "reponse": "Je n'ai pas bien compris votre question. Pourriez-vous reformuler ?",
                "suggestions": SUGGESTIONS_DEFAUT
            }
        
        # Nettoyer la question (supprimer les espaces en trop)
        question = question.strip()
        
        # Traitement spécial pour la question "Qui es-tu?"
        question_lower = question.lower().replace('?', '').replace('-', ' ').replace("'", ' ').strip()
        identity_patterns = ["qui es tu", "qui estu", "tu es qui", "t es qui", "es tu qui", "qui tu es", 
                            "c est qui tu", "c qui tu es", "qui est tu", "qui est toi"]
        
        is_identity_question = False
        for pattern in identity_patterns:
            if pattern in question_lower:
                is_identity_question = True
                break
                
        if is_identity_question:
            logger.info("Question spéciale d'identité détectée: " + question)
            reponse = "Je suis Cindy, votre assistant IA personnel. Je suis là pour vous aider avec diverses questions et tâches comme la météo, l'heure, des blagues et bien plus encore."
            suggestions = [
                "Quelles sont tes capacités ?",
                "Raconte-moi une blague",
                "Quelle est la météo à Paris aujourd'hui ?",
                "Comment vas-tu ?"
            ]
            return {
                "reponse": reponse,
                "suggestions": suggestions
            }
        
        # Utiliser notre moteur NLP pour analyser la question
        logger.info(f"Question reçue: {question}")
        resultat = analyser_et_repondre(question)
        
        # Enregistrer l'intention détectée pour le débogage
        logger.info(f"Intention détectée: {resultat['intention']} avec score {resultat['score']}")
        logger.info(f"Entités extraites: {resultat['entites']}")
        
        # Si l'intention est liée à la météo, utiliser l'API
        if resultat["intention"] == "meteo":
            try:
                # On passe la question complète à obtenir_meteo pour permettre l'extraction des villes
                # Le service météo s'occupera d'extraire la ville de la question
                logger.info(f"Demande météo pour la question: {question}")
                
                # Obtenir les données météo via l'API
                # La méthode retourne directement un message texte formaté
                reponse = meteo_service.obtenir_meteo(question)
                
                # Si le message est trop court, c'est probablement une erreur
                if len(reponse) < 30:
                    reponse = "Désolé, je n'ai pas pu obtenir les informations météo actuelles. Veuillez réessayer plus tard."
                
            except Exception as e:
                logger.error(f"Erreur lors de la récupération de la météo: {str(e)}")
                reponse = "Désolé, je n'ai pas pu obtenir les informations météo actuelles. Veuillez réessayer plus tard."
                
            return {
                "reponse": reponse,
                "suggestions": resultat["suggestions"]
            }
        
        # Si l'intention est liée à l'heure ou à la date, utiliser l'heure système
        elif resultat["intention"] == "heure" or resultat["intention"] == "date":
            return {
                "reponse": resultat["reponse"],
                "suggestions": resultat["suggestions"]
            }
            
        # Si l'intention est liée aux blagues
        elif resultat["intention"] == "blague":
            logger.info("Intention blague détectée, réponse avec une blague")
            return {
                "reponse": resultat["reponse"],
                "suggestions": resultat["suggestions"]
            }
        
        # Pour toutes les autres intentions, utiliser la réponse générée par le moteur NLP
        else:
            return {
                "reponse": resultat["reponse"],
                "suggestions": resultat["suggestions"]
            }
    
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la question: {str(e)}")
        return {
            "reponse": "Je suis désolé, une erreur s'est produite lors du traitement de votre question.",
            "suggestions": SUGGESTIONS_DEFAUT
        }

@app.route('/')
def index():
    """Page d'accueil de l'application"""
    return render_template('index.html')

@app.route('/aide')
def aide():
    """Page d'aide de l'application"""
    return render_template('aide.html')

@app.route('/question', methods=['POST'])
def question():
    """Endpoint pour traiter les questions de l'utilisateur"""
    try:
        # Récupérer la question depuis la requête POST
        data = request.get_json()
        question_utilisateur = data.get('question', '')
        
        # Simuler un court délai pour donner l'impression de réflexion
        time.sleep(0.5)
        
        # Traiter la question et générer une réponse
        reponse = poser_question(question_utilisateur)
        
        return jsonify(reponse)
    
    except Exception as e:
        logger.error(f"Erreur dans la route /question: {str(e)}")
        return jsonify({
            "reponse": "Une erreur s'est produite lors du traitement de votre demande.",
            "suggestions": SUGGESTIONS_DEFAUT
        })

if __name__ == '__main__':
    logger.info("Démarrage de l'application Agent Personnel")
    app.run(debug=True) 
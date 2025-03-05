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
import json

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
    """Endpoint pour poser une question à l'agent - Version avec API météo optimisée."""
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
        time.sleep(0.3)
        
        # On garde une structure simple mais on utilise l'API météo
        question_lower = question.lower()
        
        # Répondre directement aux questions les plus simples
        if "heure" in question_lower:
            from datetime import datetime
            maintenant = datetime.now()
            reponse = f"Il est actuellement {maintenant.strftime('%H:%M')}."
        
        elif any(mot in question_lower for mot in ["météo", "meteo", "temps"]):
            try:
                import requests
                from datetime import datetime
                
                # Extraire le nom de la ville de la question
                ville = None
                
                # Rechercher la ville dans la question après certains mots-clés
                mots_declencheurs = ["à", "a", "de", "pour", "sur", "dans"]
                for mot in mots_declencheurs:
                    if f" {mot} " in question_lower + " ":
                        parties = question_lower.split(f" {mot} ")
                        if len(parties) > 1:
                            # Prendre le premier mot après le déclencheur
                            ville_candidate = parties[1].split()[0].strip("?!.,;:")
                            # Si le mot candidat est plus long que 2 caractères, c'est probablement une ville
                            if len(ville_candidate) > 2:
                                ville = ville_candidate
                                break
                
                # Si aucune ville n'est trouvée, utiliser Paris comme défaut
                if not ville:
                    ville = "Paris"
                
                # ÉTAPE 1: Obtenir les coordonnées géographiques via l'API de géocodage
                geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={ville}&count=5&language=fr"
                geo_response = requests.get(geocoding_url)
                geo_data = geo_response.json()
                
                if "results" not in geo_data or not geo_data["results"]:
                    reponse = f"Je n'arrive pas à trouver les coordonnées de {ville.capitalize()}. Veuillez essayer une autre ville."
                else:
                    # Prendre le premier résultat comme le plus pertinent
                    selected_city = geo_data["results"][0]
                    
                    # Récupérer les coordonnées géographiques
                    latitude = selected_city["latitude"]
                    longitude = selected_city["longitude"]
                    city_name = selected_city["name"]
                    country_name = selected_city["country"]
                    
                    # ÉTAPE 2: Obtenir les données météo avec les coordonnées précises
                    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m&timezone=auto"
                    weather_response = requests.get(weather_url)
                    weather_data = weather_response.json()
                    
                    if "current" in weather_data:
                        current = weather_data["current"]
                        
                        # Extraire les données météo
                        temp = round(current.get("temperature_2m", 0))
                        apparent_temp = round(current.get("apparent_temperature", temp))
                        humidity = current.get("relative_humidity_2m", 0)
                        wind_speed = round(current.get("wind_speed_10m", 0) * 3.6)  # Convertir en km/h
                        weather_code = current.get("weather_code", 0)
                        
                        # Obtenir la description et l'icône en fonction du code météo
                        descriptions = {
                            0: "Ciel dégagé", 1: "Principalement dégagé", 2: "Partiellement nuageux", 3: "Nuageux",
                            45: "Brouillard", 48: "Brouillard givrant", 51: "Bruine légère", 53: "Bruine modérée",
                            55: "Bruine dense", 56: "Bruine verglaçante légère", 57: "Bruine verglaçante dense",
                            61: "Pluie légère", 63: "Pluie modérée", 65: "Pluie forte", 66: "Pluie verglaçante légère",
                            67: "Pluie verglaçante dense", 71: "Neige légère", 73: "Neige modérée", 75: "Neige forte",
                            77: "Grésil", 80: "Averses légères", 81: "Averses modérées", 82: "Averses violentes",
                            85: "Neige faible", 86: "Neige forte", 95: "Orage", 96: "Orage avec grêle légère",
                            99: "Orage avec grêle forte"
                        }
                        
                        icons = {
                            0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️", 45: "🌫️", 48: "🌫️❄️", 51: "🌦️", 53: "🌦️", 55: "🌦️",
                            56: "🌧️❄️", 57: "🌧️❄️", 61: "🌧️", 63: "🌧️", 65: "🌧️", 66: "🌧️❄️", 67: "🌧️❄️",
                            71: "❄️", 73: "❄️", 75: "❄️", 77: "🌨️", 80: "🌦️", 81: "🌦️", 82: "🌧️", 85: "🌨️",
                            86: "🌨️❄️", 95: "⛈️", 96: "⛈️❄️", 99: "⛈️❄️"
                        }
                        
                        description = descriptions.get(weather_code, "Conditions variables")
                        icon = icons.get(weather_code, "🌍")
                        
                        # Obtenir la date en français
                        today = datetime.now().strftime("%A %d %B %Y").capitalize()
                        translations = {
                            "Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi", 
                            "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi", "Sunday": "Dimanche",
                            "January": "janvier", "February": "février", "March": "mars", "April": "avril",
                            "May": "mai", "June": "juin", "July": "juillet", "August": "août",
                            "September": "septembre", "October": "octobre", "November": "novembre", "December": "décembre"
                        }
                        
                        for en, fr in translations.items():
                            today = today.replace(en, fr)
                        
                        # Formater la réponse météo avec un affichage similaire au script Wix
                        reponse = f"📆 {today} 📍 {city_name}, {country_name} {icon} {temp}°C {description} 🌡️ Ressentie: {apparent_temp}°C 💦 Humidité: {humidity}% 💨 Vent: {wind_speed} km/h ⏳ Mise à jour: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    else:
                        reponse = f"Je n'ai pas pu obtenir les données météo pour {city_name}. Le service météo semble indisponible."
            except Exception as e:
                print(f"Erreur avec le service météo: {e}")
                reponse = f"Je n'ai pas pu obtenir les informations météo en raison d'une erreur technique: {str(e)}"
        
        elif any(mot in question_lower for mot in ["bonjour", "salut", "hello", "coucou", "hey"]):
            reponse = "Bonjour ! Comment puis-je vous aider aujourd'hui ?"
        
        elif any(mot in question_lower for mot in ["comment va", "ça va", "ca va", "comment tu vas", "comment vas tu", "comment tu va", "comment vas-tu", "vas bien", "tu vas bien", "comment allez vous", "comment allez-vous", "comment tu te sens"]):
            reponse = "Je vais très bien, merci de demander ! Comment puis-je vous aider ?"
        
        elif any(mot in question_lower for mot in ["qui es-tu", "qui êtes-vous", "qui est-ce"]):
            reponse = "Je suis Cindy, votre assistant IA personnel. Je peux vous aider avec des questions simples et vous donner la météo en temps réel."
        
        elif "date" in question_lower:
            from datetime import datetime
            maintenant = datetime.now()
            reponse = f"Nous sommes le {maintenant.strftime('%d/%m/%Y')}."
        
        elif any(mot in question_lower for mot in ["merci", "thanks", "thx"]):
            reponse = "Je vous en prie ! N'hésitez pas si vous avez d'autres questions."
        
        else:
            reponse = f"Je comprends votre question : '{question}'. Je travaille en mode simplifié pour l'instant."
        
        # Essayer d'enregistrer dans la mémoire si possible
        try:
            memoire.ajouter_souvenir("question", question)
            memoire.ajouter_souvenir("reponse", reponse)
        except:
            pass  # Ignorer les erreurs de mémoire
        
        # Suggestions de villes
        suggestions = [
            "Quelle heure est-il ?",
            "Quel temps fait-il à Paris ?",
            "Quel temps fait-il à Moscou ?"
        ]
        
        # Retourner la réponse
        return jsonify({
            'reponse': reponse,
            'suggestions': suggestions,
            'status': 'success'
        })
        
    except Exception as e:
        # En cas d'erreur, on log mais on ne fait rien de complexe
        print(f"Erreur générale: {e}")
        
        # Réponse d'erreur ultra-simple
        return jsonify({
            'reponse': "Désolé, une erreur est survenue. Veuillez réessayer.",
            'status': 'error'
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
        
        # Obtenir des statistiques pour l'affichage
        stats = {}
        if hasattr(agent, 'obtenir_statistiques'):
            stats = agent.obtenir_statistiques()
        
        return render_template('historique.html', 
                              historique=historique_formate,
                              statistiques=stats)
    except Exception as e:
        logger.error(f"Erreur lors de l'affichage de l'historique: {e}")
        return render_template('error.html', 
                              error_message="Erreur d'accès à l'historique",
                              error_details="Impossible d'accéder à l'historique des conversations."), 500

@app.route('/statistiques')
def statistiques():
    # Obtenir les statistiques depuis l'agent
    essai_stats = agent.obtenir_statistiques()
    
    # Si les statistiques ne sont pas disponibles, on utilise des statistiques simulées
    if not essai_stats:
        stats = {
            "nb_interactions": 42,
            "questions_frequentes": [
                {"question": "Quelle est la météo ?", "occurrences": 15},
                {"question": "Quelle heure est-il ?", "occurrences": 10},
                {"question": "Comment vas-tu ?", "occurrences": 8}
            ],
            "sentiments": {"positif": 40, "neutre": 50, "negatif": 10},
            "distribution_categories": {
                "météo": 30,
                "heure": 25,
                "salutations": 20,
                "autres": 25
            }
        }
    else:
        stats = essai_stats
    
    # Calculer des statistiques supplémentaires si possible
    try:
        historique = memoire.recuperer_souvenirs("question")
        if historique:
            # TODO: Calculs supplémentaires
            pass
    except:
        pass
    
    return render_template('statistiques.html', stats=stats)

@app.route('/aide')
def aide():
    """Page d'aide expliquant comment utiliser l'assistant"""
    return render_template('aide.html')

@app.route('/enseigner', methods=['GET', 'POST'])
def enseigner():
    """Page permettant d'enseigner de nouvelles connaissances à l'agent."""
    if request.method == 'POST':
        try:
            categorie = request.form.get('categorie', '')
            contenu = request.form.get('contenu', '')
            
            if not categorie or not contenu:
                return render_template('enseigner.html', 
                                      message="Veuillez remplir tous les champs",
                                      succes=False)
            
            # Utiliser la méthode d'apprentissage si elle existe
            if hasattr(agent, 'apprendre_nouvelle_connaissance'):
                succes = agent.apprendre_nouvelle_connaissance(categorie, contenu)
                message = "Nouvelle connaissance ajoutée avec succès !" if succes else "Cette connaissance existe déjà ou n'a pas pu être ajoutée."
            else:
                # Fallback si la méthode n'existe pas
                if categorie in agent.connaissances:
                    agent.connaissances[categorie].append(contenu)
                else:
                    agent.connaissances[categorie] = [contenu]
                message = "Nouvelle connaissance ajoutée avec succès !"
                succes = True
            
            return render_template('enseigner.html', 
                                  message=message,
                                  succes=succes)
        except Exception as e:
            logger.error(f"Erreur lors de l'apprentissage: {e}")
            return render_template('enseigner.html', 
                                  message=f"Une erreur est survenue: {str(e)}",
                                  succes=False)
    else:
        # Afficher le formulaire
        categories = list(agent.connaissances.keys())
        return render_template('enseigner.html', categories=categories)

@app.route('/api/categories')
def api_categories():
    """API endpoint pour récupérer les catégories existantes."""
    try:
        categories = list(agent.connaissances.keys())
        return jsonify({
            'categories': categories,
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des catégories: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/statistiques')
def api_statistiques():
    """API endpoint pour récupérer les statistiques de l'agent."""
    try:
        if hasattr(agent, 'obtenir_statistiques'):
            stats = agent.obtenir_statistiques()
            return jsonify({
                'statistiques': stats,
                'status': 'success'
            })
        else:
            return jsonify({
                'status': 'error',
                'error': 'Les statistiques ne sont pas disponibles dans cette version de l\'agent.'
            }), 404
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

# Point d'entrée principal
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
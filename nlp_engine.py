"""
Module de traitement du langage naturel pour l'agent Cindy.
Ce module permet d'analyser les questions des utilisateurs et de générer des réponses appropriées.
"""

import re
import random
import json
import logging
from datetime import datetime

# Importer notre nouveau module d'apprentissage
from apprentissage import sauvegarder_interaction, charger_modele_ameliore, predire_intention

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("nlp_engine.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("nlp_engine")

# Dictionnaire des intentions possibles avec leurs mots-clés et poids
INTENTIONS = {
    "salutation": {
        "mots_cles": {
            "bonjour": 3, "salut": 3, "hello": 3, "coucou": 3, "hey": 2,
            "bonsoir": 3, "jour": 1, "soir": 1, "yo": 2, "hi": 2,
            "bon matin": 3, "buenos dias": 2, "hola": 2, "good morning": 2,
            "bjr": 3, "bsr": 3, "re": 2
        }
    },
    "meteo": {
        "mots_cles": {
            "meteo": 5, "temps": 4, "température": 4, "climat": 3, "chaud": 2,
            "froid": 2, "pluie": 3, "soleil": 3, "nuage": 2, "météo": 5,
            "neige": 3, "ensoleillé": 3, "pluvieux": 3, "degrés": 3, "météorologique": 4,
            "pleuvoir": 5, "pleut": 5, "pleuvra": 5, "va-t-il pleuvoir": 6, "va t il pleuvoir": 6,
            "va-t-il": 2, "va t il": 2, "fera-t-il": 2, "fera t il": 2, "prévoir": 3,
            "prévisions": 4, "nuageux": 3, "orageux": 3, "humidité": 3, "venteux": 3,
            "chaleur": 3, "gelée": 3, "degrés celsius": 4, "celsius": 3, "tempête": 4,
            "averse": 4, "beau temps": 4, "mauvais temps": 4, "ciel": 2, "éclair": 3,
            "tonnerre": 3, "brouillard": 3
        }
    },
    "heure": {
        "mots_cles": {
            "heure": 5, "temps": 2, "horloge": 3, "montre": 2, "actuel": 1,
            "maintenant": 1, "précisément": 1, "moment": 1, "horaire": 3
        }
    },
    "date": {
        "mots_cles": {
            "date": 5, "jour": 3, "mois": 3, "année": 3, "aujourd'hui": 4,
            "semaine": 2, "calendrier": 3, "actuel": 1
        }
    },
    "remerciement": {
        "mots_cles": {
            "merci": 5, "remercie": 4, "remercier": 4, "thanks": 3, "gracier": 3,
            "reconnaissance": 2, "gentil": 2, "sympa": 2
        }
    },
    "bien_etre": {
        "mots_cles": {
            "ca va": 4, "vas-tu": 4, "comment vas": 4, "comment tu vas": 4, "ça va": 4, 
            "comment ça va": 5, "tu vas bien": 4, "forme": 2, "santé": 2, "humeur": 2,
            "bien": 1, "état": 1
        }
    },
    "aide": {
        "mots_cles": {
            "aide": 5, "aider": 4, "help": 4, "comment": 2, "besoin": 2,
            "pouvez-vous": 1, "peux-tu": 1, "assister": 3, "assistance": 3,
            "guide": 3, "montrer": 2, "expliquer": 2, "instructions": 3
        }
    },
    "capacites": {
        "mots_cles": {
            "faire": 3, "capable": 4, "capacités": 5, "fonctionnalités": 4, "options": 3,
            "possibilités": 4, "quoi faire": 4, "que sais-tu": 5, "que peux-tu": 5,
            "commandes": 3, "fonctions": 3, "services": 2
        }
    },
    "identite": {
        "mots_cles": {
            "qui es-tu": 6, "qui es tu": 6, "t'appelles": 5, "t'appelle": 5, "appelles-tu": 5,
            "ton nom": 5, "ton prénom": 5, "es-tu qui": 4, "es tu qui": 4, "es-tu": 4, "es tu": 4,
            "identité": 4, "présente-toi": 5, "présente toi": 5, "tu es qui": 6, "toi": 2,
            "prénom": 3, "nom": 3, "connaitre": 1, "connaître": 1, "à propos de toi": 4,
            "tu t'appelles": 5, "tu t appelles": 5, "c'est quoi ton nom": 5, "c est quoi ton nom": 5,
            "qui tu es": 6, "ton identité": 5, "parle-moi de toi": 5, "parle moi de toi": 5,
            "dis-moi qui tu es": 6, "dis moi qui tu es": 6, "cindy": 3
        }
    },
    "blague": {
        "mots_cles": {
            "blague": 5, "joke": 5, "drôle": 4, "amusant": 4, "rire": 4,
            "humour": 4, "raconter": 3, "raconte": 3, "histoire": 2, "rigoler": 4,
            "marrant": 4, "hilarant": 4, "comique": 4, "gag": 4, "farce": 3
        }
    }
}

# Charger modèle amélioré s'il existe
modele_ameliore = charger_modele_ameliore()
if modele_ameliore:
    logger.info("Modèle amélioré chargé avec succès")
    # Fusionner le modèle amélioré avec notre dictionnaire de base
    for intention, donnees in modele_ameliore.items():
        if intention in INTENTIONS:
            # Mettre à jour les mots-clés existants
            for mot, poids in donnees.get("mots_cles", {}).items():
                INTENTIONS[intention]["mots_cles"][mot] = poids
        else:
            # Ajouter la nouvelle intention
            INTENTIONS[intention] = donnees
else:
    logger.info("Aucun modèle amélioré trouvé, utilisation du modèle de base")

# Regex pour détecter les villes (mots commençant par une majuscule)
REGEX_VILLE = r'\b([A-Z][a-z]+|[A-Z]+)\b'

# Regex pour détecter les nombres
REGEX_NOMBRE = r'\b\d+\b'

# Liste de villes courantes en France pour améliorer la détection
VILLES_COURANTES = [
    "paris", "marseille", "lyon", "toulouse", "nice", "nantes", 
    "strasbourg", "montpellier", "bordeaux", "lille", "rennes", 
    "reims", "toulon", "saint-étienne", "angers", "grenoble", 
    "dijon", "nîmes", "aix-en-provence", "nancy", "metz"
]

def extraire_entites(question):
    """
    Extrait des entités comme des villes, dates, nombres, etc. de la question.
    """
    entites = {}
    question_original = question
    question_lower = question.lower()
    
    # Recherche de motifs spécifiques pour les villes dans des questions de météo et pluie
    motifs_meteo_ville = [
        r'(?:météo|meteo|temps|température|temperature|climat)\s+(?:à|a|au|en|de|pour)\s+([a-zÀ-ÿ\s-]+?)(?:\s|$|\?|\.)',
        r'(?:va-t-il|va t il|pleut-il|pleut t il|va-t-il pleuvoir|va t il pleuvoir)\s+(?:à|a|au|en|de|pour)?\s+([a-zÀ-ÿ\s-]+?)(?:\s|$|\?|\.)',
        r'(?:à|a|au|en|de|pour)\s+([a-zÀ-ÿ\s-]+?)(?:\s|$|\?|\.)(?:météo|meteo|temps|pluie|pleuvoir)',
        r'(?:pluie|pleuvoir|pleut|neige|neiger)\s+(?:à|a|au|en|de|pour)\s+([a-zÀ-ÿ\s-]+?)(?:\s|$|\?|\.)'
    ]
    
    for motif in motifs_meteo_ville:
        matches = re.findall(motif, question_lower)
        if matches and matches[0].strip():
            # Vérifier que ce n'est pas un mot commun
            for match in matches:
                match_clean = match.strip()
                mots_communs = ["demain", "aujourd'hui", "matin", "soir", "temps", "pluie"]
                if match_clean and match_clean not in mots_communs:
                    # Récupérer la version originale avec casse
                    index = question_lower.find(match_clean)
                    if index != -1:
                        original_match = question_original[index:index+len(match_clean)]
                        entites["ville"] = original_match.capitalize()
                        break
            if "ville" in entites:
                break
    
    # Extraction des villes potentielles (mots commençant par une majuscule)
    if "ville" not in entites:
        villes = re.findall(REGEX_VILLE, question_original)
        if villes:
            # Filtrer les faux positifs au début de phrase
            if villes[0] == question_original.split()[0] and len(villes) > 1:
                villes = villes[1:]
            if villes:
                entites["ville"] = villes[0]
    
    # Si pas de ville trouvée avec le regex, chercher dans les villes courantes
    if "ville" not in entites:
        for ville in VILLES_COURANTES:
            # Chercher la ville avec des délimiteurs de mots pour éviter les faux positifs
            pattern = r'\b' + re.escape(ville) + r'\b'
            if re.search(pattern, question_lower):
                # Récupérer la vraie casse depuis la question originale
                match = re.search(pattern, question_lower)
                start, end = match.span()
                entites["ville"] = question_original[start:end].capitalize()
                break
    
    # Recherche de motifs spécifiques pour les villes
    if "ville" not in entites:
        # Motifs comme "à Paris", "pour Lyon", etc.
        motifs_ville = [
            r'à\s+([a-zA-Z\-]+)',
            r'de\s+([a-zA-Z\-]+)',
            r'pour\s+([a-zA-Z\-]+)',
            r'sur\s+([a-zA-Z\-]+)',
        ]
        
        for motif in motifs_ville:
            matches = re.findall(motif, question_lower)
            if matches:
                for match in matches:
                    # Vérifier si ce n'est pas un mot commun non-ville
                    mots_communs = ["demain", "aujourd'hui", "matin", "soir", "temps", "pluie"]
                    if match not in mots_communs:
                        entites["ville"] = match.capitalize()
                        break
                if "ville" in entites:
                    break
    
    # Extraction des nombres
    nombres = re.findall(REGEX_NOMBRE, question_original)
    if nombres:
        entites["nombre"] = nombres[0]
    
    return entites

def calculer_score_intention(question, mots_cles):
    """
    Calcule un score pour une intention en fonction des mots-clés présents.
    """
    question = question.lower()
    # Normaliser la question pour gérer les variations d'apostrophes
    question_normalisee = question.replace("'", " ").replace("-", " ")
    score = 0
    
    for mot, poids in mots_cles.items():
        # Vérifier si le mot-clé exact est présent dans la question originale
        if re.search(r'\b' + re.escape(mot) + r'\b', question):
            score += poids
        # Vérifier également dans la version normalisée pour les mots avec apostrophes
        elif '-' in mot or "'" in mot:
            mot_normalise = mot.replace("'", " ").replace("-", " ")
            if re.search(r'\b' + re.escape(mot_normalise) + r'\b', question_normalisee):
                score += poids
    
    return score

def determiner_intention(question):
    """
    Détermine l'intention principale de la question.
    Utilise à la fois notre système de mots-clés et notre modèle amélioré.
    
    Args:
        question (str): La question posée par l'utilisateur
        
    Returns:
        tuple: (intention, score, entites)
    """
    # Extraire les entités (ville, nombre, etc.)
    entites = extraire_entites(question)
    
    # Convertir la question en minuscules pour les comparaisons
    question_lower = question.lower()
    
    # Vérifier si la question contient des mots-clés liés à la météo
    mots_meteo = ["météo", "meteo", "temps", "température", "temperature", "climat", "pleuvoir", "pluie", "neige", "soleil"]
    est_meteo = any(mot in question_lower for mot in mots_meteo)
    
    # Vérifier d'abord si la question contient explicitement des mots-clés pour l'heure
    mots_heure = ["heure", "quelle heure", "horloge", "quelle heure est-il", "il est quelle heure"]
    est_heure = any(mot in question_lower for mot in mots_heure)
    
    # Vérifier les mots-clés bien_etre en priorité
    mots_bien_etre = ["comment vas", "comment va", "comment tu vas", "comment ça va", "ça va"]
    est_bien_etre = any(mot in question_lower for mot in mots_bien_etre)
    
    # Vérifier si la question contient des mots-clés pour la date
    mots_date = ["date", "jour", "aujourd'hui", "quel jour", "quelle date"]
    est_date = any(mot in question_lower for mot in mots_date)
    
    # Vérification prioritaire pour le bien-être
    if est_bien_etre:
        logger.info("Question concernant le bien-être détectée")
        return "bien_etre", 1.0, entites
    
    # Priorité à la météo si les deux sont présents
    if est_meteo and est_date:
        # Si la météo et la date sont mentionnées ensemble, on privilégie la météo
        logger.info(f"Question contient à la fois des mots de météo et de date, priorité à la météo")
        return "meteo", 1.0, entites
    
    # Si c'est une demande d'heure explicite
    if est_heure:
        return "heure", 1.0, entites
        
    # Si c'est une demande de date explicite (et pas de météo)
    if est_date:
        return "date", 1.0, entites

    # Si ce n'est pas l'heure ou la date, continuer avec l'analyse normale
    # Utiliser notre modèle amélioré pour prédire l'intention
    modele_ameliore = charger_modele_ameliore()
    
    # Obtenir la prédiction du modèle
    intention_predite, score_predit = predire_intention(question, modele_ameliore)
    
    # Si le score est assez élevé, utiliser la prédiction du modèle
    if score_predit >= 0.7:
        logger.info(f"Intention prédite par le modèle amélioré: {intention_predite} avec score {score_predit}")
        return intention_predite, score_predit, entites
    
    # Sinon, utiliser notre système de score basé sur les mots-clés
    # Dictionnaire des catégories avec leurs mots-clés
    mots_cles = {
        "salutation": ["bonjour", "salut", "hello", "coucou", "hey", "bjr", "bonsoir"],
        "meteo": ["météo", "meteo", "température", "temperature", "climat", "pleuvoir", "neige", "soleil", "pluie"],
        "heure": ["heure", "horloge", "montre", "minute", "seconde", "quelle heure"],
        "date": ["date", "jour", "mois", "année", "quel jour", "calendrier"],
        "remerciement": ["merci", "remercie", "remercier", "thanks", "thx", "grateful"],
        "bien_etre": ["comment vas", "comment ça va", "ça va", "ca va", "bien", "santé", "humeur"],
        "aide": ["aide", "aider", "help", "assister", "assistance", "secourir", "secours"],
        "capacites": ["peux-tu", "es-tu capable", "capacité", "compétence", "fonctionnalité", "fonction"],
        "blague": ["blague", "histoire drôle", "faire rire", "raconter une blague", "connais-tu une blague"],
        "identite": ["qui es-tu", "qui es tu", "qui tu es", "comment t'appelles-tu", "comment t appelles tu", "ton nom", "tu es qui", "tu t'appelles comment", "tu t appelles comment", "prénom", "présente-toi", "présente toi", "identité"]
    }
    
    # Calculer le score pour chaque intention
    scores = {}
    for categorie, keywords in mots_cles.items():
        score = calculer_score_intention(question, keywords)
        scores[categorie] = score
        
    # Vérification explicite pour l'intention identité
    if "qui es-tu" in question_lower or "qui es tu" in question_lower or "qui es tu?" in question_lower or "qui es-tu?" in question_lower:
        scores["identite"] = max(scores.get("identite", 0) + 1.0, 1.0)
        
    # Traitement spécial pour le mot "temps" qui peut être ambigu
    if "temps" in question.lower():
        # Vérifier si c'est probablement une question sur l'heure
        if any(mot in question.lower() for mot in ["quel temps", "combien de temps"]):
            scores["heure"] += 0.5
        # Sinon, c'est probablement une question sur la météo
        else:
            scores["meteo"] += 0.5
            
    # Trouver l'intention avec le score le plus élevé
    intention_max = max(scores, key=scores.get)
    score_max = scores[intention_max]
    
    # Si le score est trop faible, considérer comme intention inconnue
    if score_max < 0.2:
        intention_max = "inconnu"
        score_max = 0
        
    return intention_max, score_max, entites

def generer_reponse_simple(intention, entites=None):
    """
    Génère une réponse simple en fonction de l'intention détectée.
    """
    entites = entites or {}
    
    reponses = {
        "salutation": [
            "Bonjour ! Comment puis-je vous aider aujourd'hui ?",
            "Salut ! Je suis Cindy, votre assistant. Que puis-je faire pour vous ?",
            "Bonjour ! Que puis-je faire pour vous ?"
        ],
        "meteo": [
            f"Je vais consulter la météo pour vous{' à ' + entites.get('ville') if entites.get('ville') else ''}.",
            f"Laissez-moi vérifier la météo{' à ' + entites.get('ville') if entites.get('ville') else ''}.",
            f"Je recherche les informations météo{' pour ' + entites.get('ville') if entites.get('ville') else ''}."
        ],
        "heure": [
            f"Il est actuellement {datetime.now().strftime('%H:%M')}.",
            f"L'heure actuelle est {datetime.now().strftime('%H:%M')}.",
            f"Il est {datetime.now().strftime('%H:%M')}."
        ],
        "date": [
            f"Nous sommes le {datetime.now().strftime('%d/%m/%Y')}.",
            f"La date d'aujourd'hui est le {datetime.now().strftime('%d %B %Y')}.",
            f"Aujourd'hui, nous sommes le {datetime.now().strftime('%A %d %B %Y')}."
        ],
        "remerciement": [
            "De rien ! C'est un plaisir de vous aider.",
            "Je vous en prie. Y a-t-il autre chose que je puisse faire pour vous ?",
            "Avec plaisir ! N'hésitez pas si vous avez d'autres questions."
        ],
        "bien_etre": [
            "Je vais très bien, merci ! Et vous, comment allez-vous ?",
            "Tout va bien de mon côté. Comment puis-je vous aider aujourd'hui ?",
            "Je suis opérationnelle et prête à vous aider. Comment allez-vous ?"
        ],
        "aide": [
            "Je peux vous aider avec la météo, l'heure, la date et répondre à diverses questions. Que souhaitez-vous savoir ?",
            "Vous pouvez me demander la météo, l'heure, ou simplement discuter. Comment puis-je vous aider ?",
            "Je suis là pour vous assister. Posez-moi une question sur la météo, l'heure ou autre chose."
        ],
        "capacites": [
            "Je peux vous donner la météo, l'heure, la date, et répondre à vos questions générales.",
            "Mes capacités incluent : informations météo, heure et date, assistance générale et conversation simple.",
            "Je suis capable de vous informer sur la météo, vous donner l'heure et la date, et répondre à diverses questions."
        ],
        "identite": [
            "Je suis Cindy, votre assistant IA personnel. Je suis là pour vous aider avec diverses questions et tâches.",
            "Je m'appelle Cindy, une intelligence artificielle conçue pour répondre à vos questions et vous assister au quotidien.",
            "Je suis Cindy, un assistant virtuel développé pour vous aider. Je peux répondre à vos questions sur la météo, l'heure et bien plus encore."
        ],
        "blague": [
            "Pourquoi les plongeurs plongent-ils toujours en arrière et jamais en avant ? Parce que sinon ils tombent dans le bateau !",
            "Qu'est-ce qu'un crocodile qui surveille la pharmacie ? Un Lacoste garde.",
            "Que fait une fraise sur un cheval ? Elle galope !",
            "Qu'est-ce qui est jaune et qui attend ? Jonathan.",
            "Pourquoi les canards sont-ils toujours à l'heure ? Parce qu'ils sont dans l'étang !",
            "Comment appelle-t-on un chat tombé dans un pot de peinture le jour de Noël ? Un chat-peint de Noël.",
            "Quel est le comble pour un électricien ? De ne pas être au courant.",
            "Que dit un escargot qui rencontre une limace ? 'Tiens, tu as oublié ta carapace !'",
            "C'est l'histoire d'un papier qui tombe à l'eau. Il crie : 'Au secours ! Je ne sais pas nager !' Heureusement, une feuille morte passait par là.",
            "Pourquoi les abeilles ont-elles du miel ? Parce qu'elles se sucrent les doigts."
        ],
        "inconnu": [
            "Je ne suis pas sûre de comprendre votre demande. Pouvez-vous reformuler ?",
            "Désolée, je n'ai pas bien saisi. Pouvez-vous préciser votre question ?",
            "Je ne comprends pas complètement. Essayez de poser votre question différemment."
        ]
    }
    
    # Si l'intention existe dans notre dictionnaire de réponses
    if intention in reponses:
        return random.choice(reponses[intention])
    else:
        return random.choice(reponses["inconnu"])

def analyser_et_repondre(question, contexte=None):
    """
    Analyse la question de l'utilisateur et génère une réponse appropriée.
    
    Args:
        question (str): La question posée par l'utilisateur
        contexte (dict, optional): Contexte de la conversation

    Returns:
        dict: Résultat contenant la réponse, l'intention détectée et d'autres métadonnées
    """
    if not question or not isinstance(question, str):
        return {
            "reponse": "Je n'ai pas reçu de question valide.",
            "intention": "erreur",
            "score": 0,
            "entites": {},
            "suggestions": ["Essayez de me poser une question sur la météo à Paris", "Demandez-moi l'heure", "Demandez-moi comment je vais"]
        }
    
    try:
        logger.info(f"Début d'analyse de la question: '{question}'")
        
        # Déterminer l'intention de la question
        intention, score, entites = determiner_intention(question)
        logger.info(f"Question: '{question}' → Intention: {intention} (score: {score}), Entités: {entites}")
        
        # Générer une réponse simple en fonction de l'intention
        logger.info(f"Génération de réponse pour l'intention: {intention}")
        reponse = generer_reponse_simple(intention, entites)
        logger.info(f"Réponse générée: {reponse}")
        
        # Générer des suggestions basées sur l'intention
        logger.info(f"Génération de suggestions pour l'intention: {intention}")
        suggestions = generer_suggestions(intention)
        
        # Enregistrer l'interaction pour l'apprentissage
        try:
            sauvegarder_interaction(question, reponse, intention, score, entites)
        except Exception as e_save:
            logger.error(f"Erreur lors de l'enregistrement de l'interaction: {str(e_save)}")
        
        # Retourner le résultat
        return {
            "reponse": reponse,
            "intention": intention,
            "score": score,
            "entites": entites,
            "suggestions": suggestions
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Erreur lors de l'analyse de la question: {str(e)}")
        logger.error(f"Détail de l'erreur: {error_trace}")
        return {
            "reponse": "Désolée, une erreur s'est produite lors du traitement de votre question.",
            "intention": "erreur",
            "score": 0,
            "entites": {},
            "suggestions": ["Essayez de poser une question simple", "Demandez-moi la météo à Paris", "Demandez-moi l'heure"]
        }

def generer_suggestions(intention):
    """
    Génère des suggestions de questions basées sur l'intention détectée.
    """
    suggestions = {
        "salutation": [
            "Quelle est la météo à Paris aujourd'hui ?",
            "Quelle heure est-il ?",
            "Qui es-tu ?",
            "Raconte-moi une blague",
            "Comment vas-tu ?"
        ],
        "meteo": [
            "Quel temps fait-il à Paris ?",
            "Quelle est la météo à Lyon ?",
            "Va-t-il pleuvoir à Bordeaux demain ?",
            "Fait-il chaud à Nice ?",
            "Quel temps fait-il à Marseille ?",
            "Météo à Strasbourg aujourd'hui",
            "Quelle est la température à Toulouse ?"
        ],
        "heure": [
            "Quelle est la date aujourd'hui ?",
            "Quel jour sommes-nous ?",
            "Qui es-tu ?",
            "Raconte-moi une blague"
        ],
        "date": [
            "Quelle heure est-il ?",
            "Quel temps fait-il à Paris aujourd'hui ?",
            "Raconte-moi une blague",
            "Qui es-tu ?"
        ],
        "remerciement": [
            "Quelle est la météo à Paris aujourd'hui ?",
            "Raconte-moi une blague",
            "Qui es-tu ?",
            "Quelles sont tes capacités ?"
        ],
        "bien_etre": [
            "Quelle est la météo à Lyon aujourd'hui ?",
            "Raconte-moi une blague",
            "Qui es-tu ?",
            "Quelles sont tes capacités ?"
        ],
        "aide": [
            "Quelle est la météo à Paris ?",
            "Quelle heure est-il ?",
            "Qui es-tu ?",
            "Quelles sont tes capacités ?",
            "Raconte-moi une blague"
        ],
        "capacites": [
            "Donne-moi la météo pour Paris",
            "Quelle heure est-il ?",
            "Raconte-moi une blague",
            "Qui es-tu ?"
        ],
        "identite": [
            "Quelles sont tes capacités ?",
            "Raconte-moi une blague",
            "Quelle est la météo à Paris aujourd'hui ?",
            "Comment vas-tu ?"
        ],
        "blague": [
            "Raconte-moi une autre blague",
            "Quelle est la météo à Marseille aujourd'hui ?",
            "Comment vas-tu ?",
            "Qui es-tu ?"
        ],
        "inconnu": [
            "Quelle est la météo à Paris aujourd'hui ?",
            "Qui es-tu ?",
            "Raconte-moi une blague",
            "Quelle heure est-il ?",
            "Comment vas-tu ?"
        ]
    }
    
    # Si l'intention existe dans notre dictionnaire de suggestions
    if intention in suggestions:
        # Pour la météo, sélectionner 3 suggestions aléatoires parmi les options disponibles
        if intention == "meteo":
            import random
            return random.sample(suggestions[intention], 3)
        # Pour les autres intentions, sélectionner 3 ou 4 suggestions aléatoires
        else:
            import random
            max_suggestions = min(4, len(suggestions[intention]))
            return random.sample(suggestions[intention], max_suggestions)
    else:
        return random.sample(suggestions["inconnu"], 3)

# Tests unitaires simples si le script est exécuté directement
if __name__ == "__main__":
    # Tests de différentes questions
    questions_test = [
        "Bonjour, comment ça va ?",
        "Quelle est la météo à Paris ?",
        "Quelle heure est-il ?",
        "Quel jour sommes-nous ?",
        "Merci pour ton aide",
        "Comment vas-tu ?",
        "Pouvez-vous m'aider ?",
        "Que peux-tu faire ?",
        "J'aime les chats" # Devrait être une intention inconnue
    ]
    
    print("=== Tests du moteur NLP ===")
    for question in questions_test:
        resultat = analyser_et_repondre(question)
        print(f"\nQuestion: '{question}'")
        print(f"Intention: {resultat['intention']} (score: {resultat['score']})")
        print(f"Entités: {resultat['entites']}")
        print(f"Réponse: '{resultat['reponse']}'")
        print(f"Suggestions: {resultat['suggestions']}")
    
    print("\n=== Tests terminés ===") 
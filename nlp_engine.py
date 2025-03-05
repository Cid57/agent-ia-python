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
from apprentissage import sauvegarder_interaction, charger_modele_ameliore

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
            "bonsoir": 3, "jour": 1, "soir": 1
        }
    },
    "meteo": {
        "mots_cles": {
            "meteo": 5, "temps": 4, "température": 4, "climat": 3, "chaud": 2,
            "froid": 2, "pluie": 3, "soleil": 3, "nuage": 2, "météo": 5,
            "neige": 3, "ensoleillé": 3, "pluvieux": 3, "degrés": 3, "météorologique": 4,
            "pleuvoir": 5, "pleut": 5, "pleuvra": 5, "va-t-il pleuvoir": 6, "va t il pleuvoir": 6,
            "va-t-il": 2, "va t il": 2, "fera-t-il": 2, "fera t il": 2
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
    score = 0
    
    for mot, poids in mots_cles.items():
        # Vérifie si le mot-clé est présent dans la question
        if re.search(r'\b' + re.escape(mot) + r'\b', question):
            score += poids
    
    return score

def determiner_intention(question):
    """
    Détermine l'intention de l'utilisateur en fonction de sa question.
    Retourne un tuple (intention, score, entites).
    """
    scores = {}
    for intention, data in INTENTIONS.items():
        scores[intention] = calculer_score_intention(question, data["mots_cles"])
    
    # Trouver l'intention avec le score le plus élevé
    intention_max = max(scores.items(), key=lambda x: x[1])
    
    # Extraire des entités potentielles
    entites = extraire_entites(question)
    
    # Si le score maximum est trop faible, l'intention est inconnue
    if intention_max[1] < 2:
        return ("inconnu", 0, entites)
    
    return (intention_max[0], intention_max[1], entites)

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
            f"Il est {datetime.now().strftime('%H:%M')} à ma montre."
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
            "suggestions": ["Essayez de me poser une question sur la météo", "Demandez-moi l'heure", "Demandez-moi comment je vais"]
        }
    
    try:
        # Déterminer l'intention de la question
        intention, score, entites = determiner_intention(question)
        logger.info(f"Question: '{question}' → Intention: {intention} (score: {score}), Entités: {entites}")
        
        # Générer une réponse simple en fonction de l'intention
        reponse = generer_reponse_simple(intention, entites)
        
        # Générer des suggestions basées sur l'intention
        suggestions = generer_suggestions(intention)
        
        # Enregistrer l'interaction pour l'apprentissage
        sauvegarder_interaction(question, reponse, intention, score, entites)
        
        # Retourner le résultat
        return {
            "reponse": reponse,
            "intention": intention,
            "score": score,
            "entites": entites,
            "suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de la question: {str(e)}")
        return {
            "reponse": "Désolée, une erreur s'est produite lors du traitement de votre question.",
            "intention": "erreur",
            "score": 0,
            "entites": {},
            "suggestions": ["Essayez de poser une question simple", "Demandez-moi la météo", "Demandez-moi l'heure"]
        }

def generer_suggestions(intention):
    """
    Génère des suggestions de questions basées sur l'intention détectée.
    """
    suggestions = {
        "salutation": [
            "Quelle est la météo aujourd'hui ?",
            "Quelle heure est-il ?",
            "Raconte-moi une blague"
        ],
        "meteo": [
            "Quel temps fait-il à Paris ?",
            "Quelle est la météo à Lyon ?",  # Formulation différente
            "Donne-moi la météo pour Marseille",  # Autre formulation
            "Va-t-il pleuvoir à Bordeaux demain ?",  # Question sur la pluie
            "Fait-il chaud à Nice ?",  # Question sur la température
            "Météo à Strasbourg"  # Format court
        ],
        "heure": [
            "Quelle est la date aujourd'hui ?",
            "Quel jour sommes-nous ?",
            "Raconte-moi une blague"
        ],
        "date": [
            "Quelle heure est-il ?",
            "Quel temps fait-il aujourd'hui ?",
            "Raconte-moi une blague"
        ],
        "remerciement": [
            "Quelle est la météo aujourd'hui ?",
            "Raconte-moi une blague",
            "Quelles sont tes capacités ?"
        ],
        "bien_etre": [
            "Quelle est la météo aujourd'hui ?",
            "Raconte-moi une blague",
            "Que peux-tu faire ?"
        ],
        "aide": [
            "Quelle est la météo à Paris ?",
            "Quelle heure est-il ?",
            "Raconte-moi une blague"
        ],
        "capacites": [
            "Donne-moi la météo pour Paris",
            "Quelle heure est-il ?",
            "Raconte-moi une blague"
        ],
        "blague": [
            "Raconte-moi une autre blague",
            "Quelle est la météo aujourd'hui ?",
            "Comment vas-tu ?"
        ],
        "inconnu": [
            "Quelle est la météo aujourd'hui ?",
            "Quelle heure est-il ?",
            "Raconte-moi une blague"
        ]
    }
    
    # Si l'intention existe dans notre dictionnaire de suggestions
    if intention in suggestions:
        # Pour la météo, sélectionner 3 suggestions aléatoires parmi les options disponibles
        if intention == "meteo":
            import random
            return random.sample(suggestions[intention], 3)
        return suggestions[intention]
    else:
        return suggestions["inconnu"]

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
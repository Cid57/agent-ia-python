"""
Agent IA - Module principal
Ce module contient la classe principale Agent qui gère la logique de notre assistant IA.
"""

import random
import datetime
import locale
import logging
import platform
from nlp_utils import AnalyseurTexte
from external_services import MeteoService

# Configurer le logger
logger = logging.getLogger('assistant_ia.agent')

# Configurer la localisation pour avoir les noms des jours en français
def configurer_locale():
    """Configure la locale pour le français selon le système d'exploitation."""
    system = platform.system()
    locales_to_try = []
    
    # Différentes locales à essayer selon le système d'exploitation
    if system == 'Windows':
        locales_to_try = ['fr_FR', 'fra', 'fra_fra', 'French_France']
    else:  # Linux, MacOS, etc.
        locales_to_try = ['fr_FR.UTF-8', 'fr_FR.utf8', 'fr_FR', 'fr']
    
    # Essayer chaque locale
    for loc in locales_to_try:
        try:
            locale.setlocale(locale.LC_TIME, loc)
            logger.info(f"Locale configurée avec succès: {loc}")
            return True
        except locale.Error:
            continue
    
    # Si aucune locale française n'est disponible
    logger.warning("Aucune locale française n'a pu être configurée. Utilisation de la locale par défaut.")
    try:
        # Utiliser la locale par défaut du système
        locale.setlocale(locale.LC_TIME, '')
        logger.info(f"Utilisation de la locale par défaut: {locale.getlocale(locale.LC_TIME)}")
    except:
        logger.error("Impossible de configurer une locale.")
    
    return False

# Appeler la fonction de configuration
configurer_locale()

class Agent:
    """
    Classe Agent: représente notre assistant IA avec ses capacités de base.
    """
    
    def __init__(self, nom="AssistantIA"):
        """
        Initialise un nouvel agent.
        
        Args:
            nom (str): Le nom de l'agent
        """
        self.nom = nom
        logger.info(f"Agent {self.nom} initialisé")
        
        # Initialiser les services externes
        self.meteo_service = MeteoService()
        
        # Dictionnaire étendu avec plus de catégories et de mots-clés
        self.connaissances = {
            "salutations": [
                "bonjour", "salut", "hello", "coucou", "bonsoir", "hey", "yo", "hola", 
                "bjr", "slt", "rebonjour", "re", "bon matin", "bonne journée", "good morning",
                "bien le bonjour", "hi", "kikou", "cc", "wesh"
            ],
            "au revoir": [
                "au revoir", "bye", "à bientôt", "adieu", "à plus tard", "ciao", "à+", 
                "tchao", "à la prochaine", "salut", "bonne journée", "bonne soirée", "à demain",
                "aurevoir", "a+", "a plus", "goodbye", "see you", "a bientot"
            ],
            "météo": [
                "météo", "temps", "pluie", "neige", "soleil", "température", "climat", "orage", 
                "tempête", "prévisions", "vent", "nuage", "ensoleillé", "pluvieux", "chaud", "froid",
                "il fait beau", "il pleut", "météorologie", "weather", "meteo", "temperature",
                "ville", "quel temps", "degrés", "celsius", "fahrenheit", "humidité", "précipitations"
            ],
            "heure": [
                "heure", "temps", "horloge", "montre", "minutes", "secondes", "midi", "minuit", 
                "matin", "soir", "après-midi", "date", "jour", "aujourd'hui", "l'heure", "quelle heure",
                "chronologie", "clock", "time", "maintenant", "horaire", "la date"
            ],
            "humeur": [
                "comment vas", "comment ça va", "ça va", "la forme", "humeur", "comment tu te sens", 
                "sentiment", "état", "comment tu vas", "tu vas bien", "en forme", "ca va", "ça roule",
                "tu te portes bien", "moral", "feeling", "vas-tu", "how are you", "comment allez vous"
            ],
            "présentation": [
                "qui es-tu", "présente-toi", "c'est quoi ton nom", "quel est ton nom", "comment t'appelles-tu", 
                "tu es qui", "ton nom", "ton créateur", "ta fonction", "tu sers à quoi", "ton but",
                "qu'est-ce que tu es", "qui t'a créé", "what are you", "identity", "identité", "présentation",
                "qui es tu", "tu t'appelles comment", "te présenter", "appelles tu"
            ],
            "remerciements": [
                "merci", "thanks", "thx", "je te remercie", "cool", "super", "génial", "bravo", 
                "bien joué", "parfait", "excellent", "c'est gentil", "bien vu", "je t'en remercie",
                "thanks a lot", "thank you", "je te suis reconnaissant", "c'est cool", "sympa", "ty"
            ],
            "aide": [
                "aide", "help", "besoin d'aide", "sos", "comment faire", "peux-tu m'aider", "j'ai besoin", 
                "aide-moi", "instructions", "guide", "comment utiliser", "que peux-tu faire", "capabilities",
                "capacités", "fonctionnalités", "commands", "commandes", "ton aide", "assistance", "support",
                "guidemoi", "comment ca marche", "fonctionnement", "quelles commandes", "possible"
            ],
            "blague": [
                "blague", "histoire drôle", "fais-moi rire", "raconte une blague", "humour", 
                "quelque chose de drôle", "joke", "amusant", "rigolo", "drole", "rigolant", 
                "marrant", "funny", "humor", "humoristique", "rire", "farce", "plaisanterie",
                "raconte quelque chose de drole", "raconter une blague", "fais moi sourire"
            ],
            "capacités": [
                "capable", "fonction", "options", "fonctionnalité", "capacité", "possibilité", 
                "savoir-faire", "connaissance", "que sais-tu", "tu peux quoi", "tu sais faire quoi",
                "quoi faire", "que peux-tu", "tu sais quoi", "sais-tu", "peux-tu", "peut tu", "quelles fonctions"
            ]
        }
        
        # Réponses variées pour chaque catégorie
        self.reponses = {
            "salutations": [
                f"Bonjour ! Je suis {self.nom}, votre assistante IA. Comment puis-je vous aider aujourd'hui ?",
                f"Salut ! C'est {self.nom}. Je suis là pour vous aider !",
                f"Coucou ! Ravie de vous parler. Que puis-je faire pour vous ?",
                f"Bonjour ! Comment puis-je vous assister aujourd'hui ?"
            ],
            "au revoir": [
                "Au revoir ! N'hésitez pas à revenir si vous avez d'autres questions.",
                "À bientôt ! J'espère avoir pu vous aider.",
                "À la prochaine ! Passez une excellente journée.",
                "Au revoir et à très vite !"
            ],
            "météo": [
                "Voici la météo actuelle : {meteo}",
                "D'après mes informations, voici la météo : {meteo}",
                "Les conditions météorologiques actuelles sont : {meteo}"
            ],
            "humeur": [
                "Je vais très bien, merci de demander ! Et vous ?",
                "En tant qu'IA, je n'ai pas d'émotions, mais je suis toujours prête à vous aider !",
                "Je suis au top de ma forme numérique et prête à vous assister !"
            ],
            "présentation": [
                f"Je suis {self.nom}, une assistante IA créée pour répondre à vos questions et vous aider dans vos tâches quotidiennes.",
                f"Je m'appelle {self.nom}, une agente IA conçue pour interagir avec vous et vous assister.",
                f"Je suis {self.nom}, votre assistante virtuelle personnelle. Je suis là pour vous aider et répondre à vos questions."
            ],
            "remerciements": [
                "De rien ! C'est un plaisir de vous aider.",
                "Tout le plaisir est pour moi !",
                "Je vous en prie. N'hésitez pas si vous avez d'autres questions."
            ],
            "aide": [
                f"Je suis {self.nom}, votre assistante IA. Je peux répondre à des questions, vous donner l'heure, la météo, raconter des blagues et discuter avec vous. Essayez de me demander 'Quelle heure est-il ?', 'Quel temps fait-il à Paris ?' ou 'Raconte-moi une blague'.",
                "Je peux vous aider sur plusieurs sujets : l'heure actuelle, la météo dans différentes villes, des blagues, des informations sur moi-même. Essayez de me poser ces questions !",
                "Comment puis-je vous aider aujourd'hui ? Je peux vous donner l'heure, la météo, vous raconter une blague, ou simplement discuter avec vous. N'hésitez pas à demander !"
            ],
            "blague": [
                "Pourquoi les plongeurs plongent-ils toujours en arrière et jamais en avant ? Parce que sinon ils tombent dans le bateau !",
                "Un électron frappe à la porte d'un hôtel. Le réceptionniste lui demande : 'Vous désirez une chambre ?' Et l'électron répond : 'Non merci, je suis déjà excité.'",
                "Qu'est-ce qu'un crocodile qui surveille la pharmacie ? Un Lacoste Garde.",
                "Pourquoi les informaticiens confondent-ils Halloween et Noël ? Parce qu'Oct 31 = Dec 25.",
                "Que dit un informaticien quand il s'ennuie ? Je bit ma vie !"
            ],
            "capacités": [
                f"En tant qu'assistante IA, je peux : vous donner l'heure actuelle, vous informer sur la météo dans différentes villes, raconter des blagues, discuter simplement et répondre à des questions basiques. Essayez par exemple 'Quelle heure est-il ?', 'Quel temps fait-il à Paris ?' ou 'Raconte-moi une blague'.",
                f"Mes capacités incluent : vous saluer, vous dire au revoir, vous donner l'heure, vous informer sur la météo, répondre à des questions sur moi-même et raconter des blagues. Que souhaitez-vous essayer ?",
                f"Je peux répondre à des questions simples, vous donner l'heure et la météo, raconter des blagues et avoir une conversation basique. N'hésitez pas à me tester !"
            ],
            "inconnu": [
                "Je ne comprends pas encore cette question. Je suis une agente en apprentissage ! Essayez de me demander l'heure, la météo ou de me demander une blague.",
                "Hmm, je ne suis pas sûre de comprendre. Pourriez-vous reformuler votre question ? Je peux par exemple vous donner l'heure actuelle, la météo ou vous raconter une blague.",
                "Désolée, cette question dépasse mes capacités actuelles. Essayez plutôt de me demander 'Quelle heure est-il ?', 'Quel temps fait-il à Lyon ?' ou 'Raconte-moi une blague'."
            ]
        }
        
        self.historique = []
        self.analyseur = AnalyseurTexte()
        print(f"Agent {self.nom} initialisé et prêt à l'emploi!")
    
    def comprendre_question(self, question):
        """
        Identifie la catégorie de la question posée.
        
        Args:
            question (str): La question posée par l'utilisateur
            
        Returns:
            str: La catégorie identifiée
        """
        # Conversion en minuscules pour faciliter la comparaison
        question = question.lower()
        
        # Nettoyage et normalisation de la question
        question_normalisee = self.analyseur.nettoyer_texte(question)
        
        # Extraire les mots-clés de la question
        mots_question = self.analyseur.extraire_mots_cles(question_normalisee)
        
        # Patterns pour détecter les questions météo
        patterns_meteo = [
            "météo", "meteo", "temps", "température", "temperature",
            "quel temps", "comment est le temps", "temps qu'il fait",
            "qu'est-ce qu'il fait comme temps", "climat"
        ]
        
        # Vérifier si la question contient des motifs de demande météo
        for pattern in patterns_meteo:
            if pattern in question_normalisee:
                logger.debug(f"Question identifiée comme demande météo: {question}")
                return "météo"
        
        # Phrases qui indiquent clairement une demande météo pour une ville
        if "temps" in question_normalisee and "à" in question_normalisee:
            logger.debug(f"Question identifiée comme demande météo avec préposition 'à': {question}")
            return "météo"
            
        if "météo" in question_normalisee or "meteo" in question_normalisee:
            logger.debug(f"Question identifiée comme demande météo explicite: {question}")
            return "météo"
            
        # Traitement spécial pour l'heure
        if any(mot in question_normalisee for mot in ["heure", "temps", "l'heure", "clock", "horloge", "maintenant"]):
            return "heure"
        
        # Traitement spécial pour les blagues
        if any(mot in question_normalisee for mot in ["blague", "drole", "amuse", "rire", "rigolo", "joke", "funny"]):
            return "blague"
            
        # Traitement spécial pour les salutations
        if any(mot in question_normalisee for mot in ["bonjour", "salut", "hello", "coucou", "yo", "bjr", "slt"]):
            return "salutations"
        
        # Pour les autres catégories, calculer la similarité avec chaque catégorie
        meilleure_categorie = None
        meilleur_score = 0.0
        
        for categorie, mots_cles in self.connaissances.items():
            # Chercher des correspondances exactes d'abord
            for mot in mots_cles:
                if mot in question_normalisee.split():
                    logger.debug(f"Catégorie trouvée par mot exact '{mot}': {categorie}")
                    return categorie
            
            # Si pas de correspondance exacte, vérifier si des mots-clés sont contenus dans la question
            for mot in mots_cles:
                if mot in question_normalisee:
                    logger.debug(f"Catégorie trouvée par inclusion '{mot}': {categorie}")
                    return categorie
            
            # Si toujours pas de correspondance, calculer un score de similarité
            score = 0
            for mot in mots_cles:
                similarite = self.analyseur.calculer_similarite(mot, question_normalisee)
                if similarite > 0.5:
                    score += 1
                    logger.debug(f"Score augmenté pour '{mot}' (similarité {similarite:.2f}): {categorie}")
            
            # Mettre à jour la meilleure correspondance si ce score est plus élevé
            if score > meilleur_score:
                meilleur_score = score
                meilleure_categorie = categorie
        
        # Réduire le seuil pour le score minimal
        if meilleur_score > 0:
            logger.debug(f"Meilleure catégorie trouvée par score ({meilleur_score}): {meilleure_categorie}")
            return meilleure_categorie
        
        logger.debug(f"Aucune catégorie trouvée, retourne 'inconnu'")
        return "inconnu"
    
    def generer_reponse(self, question):
        """
        Génère une réponse en fonction de la question posée.
        
        Args:
            question (str): La question posée par l'utilisateur
            
        Returns:
            str: La réponse générée
        """
        # Ajouter la question à l'historique
        self.historique.append({"type": "question", "contenu": question})
        
        # Identifier le sujet de la question
        sujet = self.comprendre_question(question)
        
        # Générer une réponse basée sur le sujet
        if sujet == "heure":
            # Cas spécial pour l'heure - toujours générer l'heure actuelle
            maintenant = datetime.datetime.now()
            heure_actuelle = maintenant.strftime("%H:%M:%S")
            
            # Format de date simplifié pour éviter les problèmes de locale
            jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
            mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", 
                   "août", "septembre", "octobre", "novembre", "décembre"]
            
            jour_semaine = jours[maintenant.weekday()]
            jour_mois = maintenant.day
            mois_nom = mois[maintenant.month - 1]
            annee = maintenant.year
            
            reponse = f"Il est actuellement {heure_actuelle} le {jour_semaine} {jour_mois} {mois_nom} {annee}."
        elif sujet == "météo":
            # Obtenir les données météo avec le nouveau format
            meteo_message = self.meteo_service.obtenir_meteo(question)
            
            # Le service météo retourne maintenant directement un message formaté
            # Si c'est une chaîne de caractères, c'est soit un message d'erreur, soit le message formaté
            if isinstance(meteo_message, str):
                reponse = meteo_message
            else:
                # Pour la compatibilité avec l'ancien format (cas improbable)
                template = random.choice(self.reponses["météo"])
                meteo_msg = f"À {meteo_message.get('ville', 'inconnue')}, il fait {meteo_message.get('temperature', '?')}°C."
                reponse = template.format(meteo=meteo_msg)
        else:
            # Pour les autres sujets, choisir une réponse aléatoire dans la liste des réponses possibles
            reponses_possibles = self.reponses.get(sujet, self.reponses["inconnu"])
            reponse = random.choice(reponses_possibles)
        
        # Ajouter la réponse à l'historique
        self.historique.append({"type": "reponse", "contenu": reponse})
        
        return reponse
    
    def afficher_historique(self):
        """
        Affiche l'historique des échanges.
        
        Returns:
            list: Liste des échanges
        """
        return self.historique


# Test simple si le fichier est exécuté directement
if __name__ == "__main__":
    agent = Agent("MonAssistant")
    print(agent.generer_reponse("Bonjour comment vas-tu?"))
    print(agent.generer_reponse("Quelle heure est-il?"))
    print(agent.generer_reponse("Raconte-moi une blague"))
    print(agent.generer_reponse("Au revoir!"))




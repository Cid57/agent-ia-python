"""
Agent IA - Module principal
Ce module contient la classe principale Agent qui gère la logique de notre assistant IA.
"""

import random
import datetime
import locale
import logging
import platform
import json
from nlp_utils import AnalyseurTexte
from external_services import MeteoService
from memory import Memoire

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
    Classe Agent: représente notre assistant IA avec ses capacités avancées.
    """
    
    def __init__(self, nom="AssistantIA"):
        """
        Initialise un nouvel agent intelligent.
        
        Args:
            nom (str): Le nom de l'agent
        """
        self.nom = nom
        logger.info(f"Agent {self.nom} initialisé")
        
        # Initialiser les services externes
        self.meteo_service = MeteoService()
        
        # Initialiser le système de mémoire
        self.memoire = Memoire()
        
        # Initialiser les compteurs d'interactions
        self.nb_interactions = 0
        self.dernier_sentiment = "neutre"
        
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
                "qui est tu", "t'es qui", "tes qui", "identité", "rôle", "fonction", "travail",
                "capabilities", "fonctionnalités", "capacités", "que sais-tu faire", "ce que tu sais faire"
            ],
            "conversation": [
                "discute", "parle", "discuter", "communiquer", "bavarder", "échanger", "causer",
                "chatter", "converser", "dialogue", "parler"
            ],
            "conseils": [
                "conseil", "aide", "guider", "orienter", "recommandation", "suggestion", 
                "avis", "opinion", "guide", "recommander", "suggérer", "aider",
                "assistance", "besoin", "help", "supporter", "accompagner", "aiguiller"
            ],
            "remerciements": [
                "merci", "remercie", "remercier", "gratitude", "appreciation", "grâce à toi",
                "thanks", "thank you", "thx", "merciii", "mrc", "je te remercie"
            ],
            "excuses": [
                "désolé", "excuse", "pardonne", "navré", "pardon", "my bad", "oups",
                "sorry", "apologize", "excuses", "erreur", "faute", "méprise"
            ],
            "apprentissage": [
                "apprendre", "apprends", "mémoriser", "retenir", "souvenir", "rappelle-toi", "learning",
                "learn", "rappelle", "souviens", "mémorise", "connaissance", "savoir"
            ],
            "culture": [
                "art", "musique", "film", "cinéma", "livre", "littérature", "peinture", "histoire",
                "sciences", "biologie", "physique", "chimie", "mathématiques", "géographie",
                "cuisine", "recette", "plat", "nourriture", "sport", "activité", "exercice"
            ],
            "tech": [
                "ordinateur", "logiciel", "programme", "application", "site", "internet", "web",
                "technologie", "informatique", "code", "programmation", "développement", "mobile",
                "telephone", "smartphone", "tablette", "réseaux", "données", "sécurité", "hacking"
            ]
        }
        
        # Réponses adaptées au contexte
        self.reponses = {
            "salutations": [
                f"Bonjour ! Je suis {self.nom}, votre assistante virtuelle. Comment puis-je vous aider aujourd'hui ?",
                f"Salut ! {self.nom} à votre service. Que puis-je faire pour vous ?",
                f"Bonjour ! Comment puis-je vous assister aujourd'hui ?"
            ],
            "au revoir": [
                "Au revoir ! N'hésitez pas à revenir si vous avez d'autres questions.",
                "À bientôt ! J'ai été ravie de pouvoir vous aider.",
                "Au plaisir de vous revoir bientôt !"
            ],
            "humeur": [
                "Je vais très bien, merci de vous en soucier ! Et vous, comment allez-vous ?",
                "Tout va parfaitement bien de mon côté ! Comment se passe votre journée ?",
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
                "Que dit un informaticien quand il s'ennuie ? Je bit ma vie !",
                "Un DRH demande à un informaticien : 'Quelle est la différence entre toi et moi ?' L'informaticien répond : 'Moi, on me demande de résoudre des problèmes qu'on ne comprend pas, alors que toi tu crées des problèmes qu'on ne peut pas résoudre.'"
            ],
            "capacités": [
                f"En tant qu'assistante IA, je peux : vous donner l'heure actuelle, vous informer sur la météo dans différentes villes, raconter des blagues, discuter simplement et répondre à des questions basiques. Essayez par exemple 'Quelle heure est-il ?', 'Quel temps fait-il à Paris ?' ou 'Raconte-moi une blague'.",
                f"Mes capacités incluent : vous saluer, vous dire au revoir, vous donner l'heure, vous informer sur la météo, répondre à des questions sur moi-même et raconter des blagues. Que souhaitez-vous essayer ?",
                f"Je peux répondre à des questions simples, vous donner l'heure et la météo, raconter des blagues et avoir une conversation basique. N'hésitez pas à me tester !"
            ],
            "excuses": [
                "Je vous présente mes excuses. Je fais de mon mieux pour m'améliorer constamment.",
                "Je suis désolée pour cette erreur. Merci de votre patience.",
                "Pardonnez-moi, je suis encore en apprentissage."
            ],
            "apprentissage": [
                "Je viens d'apprendre quelque chose de nouveau, merci ! Je m'améliore à chaque conversation.",
                "J'ai enregistré cette information dans ma mémoire. Merci de contribuer à mon apprentissage !",
                "Voilà qui enrichit ma base de connaissances. Merci pour ce partage !"
            ],
            "conseils": [
                "Pour résoudre ce problème, je vous suggère de...",
                "D'après mon analyse, la meilleure approche serait de...",
                "Si je peux me permettre un conseil, essayez de..."
            ],
            "conversation": [
                "C'est un plaisir de discuter avec vous ! Quels sont vos centres d'intérêt ?",
                "J'apprécie cette conversation. Y a-t-il un sujet particulier dont vous aimeriez parler ?",
                "Discuter est une excellente façon d'apprendre. Qu'est-ce qui vous passionne ?"
            ],
            "culture": [
                "C'est un sujet fascinant ! J'ai quelques informations à ce propos...",
                "Voilà un domaine riche et passionnant. Voici ce que je peux vous dire...",
                "Je suis ravie que vous vous intéressiez à ce sujet. Laissez-moi vous en dire plus..."
            ],
            "tech": [
                "La technologie évolue si rapidement ! Voici ce que je sais à ce sujet...",
                "C'est un domaine en constante évolution. Voici quelques informations...",
                "Un sujet technologique fascinant ! Je peux vous dire que..."
            ],
            "inconnu": [
                "Je ne comprends pas encore cette question. Je suis une agente en apprentissage ! Essayez de me demander l'heure, la météo ou de me demander une blague.",
                "Hmm, je ne suis pas sûre de comprendre. Pourriez-vous reformuler votre question ? Je peux par exemple vous donner l'heure actuelle, la météo ou vous raconter une blague.",
                "Désolée, cette question dépasse mes capacités actuelles. Essayez plutôt de me demander 'Quelle heure est-il ?', 'Quel temps fait-il à Lyon ?' ou 'Raconte-moi une blague'."
            ]
        }
        
        self.historique = []
        self.analyseur = AnalyseurTexte()
        self.questions_frequentes = {}
        self.preferences_utilisateur = {}
        print(f"Agent {self.nom} initialisé et prêt à l'emploi!")
    
    def comprendre_question(self, question):
        """
        Identifie la catégorie de la question posée avec plus de précision.
        
        Args:
            question (str): La question posée par l'utilisateur
            
        Returns:
            dict: Informations détaillées sur la question (catégorie, type, entités, etc.)
        """
        # Conversion en minuscules pour faciliter la comparaison
        question_lower = question.lower()
        
        # Nettoyage et normalisation de la question
        question_normalisee = self.analyseur.nettoyer_texte(question)
        
        # Extraire les mots-clés de la question
        mots_question = self.analyseur.extraire_mots_cles(question_normalisee)
        
        # Analyser le sentiment
        sentiment = self.analyseur.analyser_sentiment(question)
        
        # Identifier le type de question (information, localisation, etc.)
        type_question = self.analyseur.identifier_type_question(question)
        
        # Extraire les entités (dates, lieux, noms)
        entites = self.analyseur.extraire_entites(question)
        
        # Patterns pour détecter les questions météo
        patterns_meteo = [
            "météo", "meteo", "temps", "température", "temperature",
            "quel temps", "comment est le temps", "temps qu'il fait",
            "qu'est-ce qu'il fait comme temps", "climat"
        ]
        
        # Créer un dictionnaire pour stocker les informations sur la question
        info_question = {
            "categorie": "inconnu",
            "type_question": type_question,
            "sentiment": sentiment,
            "mots_cles": mots_question,
            "entites": entites
        }
        
        # Vérifier si la question contient des motifs de demande météo
        for pattern in patterns_meteo:
            if pattern in question_normalisee:
                logger.debug(f"Question identifiée comme demande météo: {question}")
                info_question["categorie"] = "météo"
                return info_question
        
        # Phrases qui indiquent clairement une demande météo pour une ville
        if "temps" in question_normalisee and "à" in question_normalisee:
            logger.debug(f"Question identifiée comme demande météo avec préposition 'à': {question}")
            info_question["categorie"] = "météo"
            return info_question
            
        if "météo" in question_normalisee or "meteo" in question_normalisee:
            logger.debug(f"Question identifiée comme demande météo explicite: {question}")
            info_question["categorie"] = "météo"
            return info_question
            
        # Traitement spécial pour l'heure
        if any(mot in question_normalisee for mot in ["heure", "temps", "l'heure", "clock", "horloge", "maintenant"]):
            info_question["categorie"] = "heure"
            return info_question
        
        # Traitement spécial pour les blagues
        if any(mot in question_normalisee for mot in ["blague", "drole", "amuse", "rire", "rigolo", "joke", "funny"]):
            info_question["categorie"] = "blague"
            return info_question
            
        # Traitement spécial pour les salutations
        if any(mot in question_normalisee for mot in ["bonjour", "salut", "hello", "coucou", "yo", "bjr", "slt"]):
            info_question["categorie"] = "salutations"
            return info_question
        
        # Pour les autres catégories, calculer la similarité avec chaque catégorie
        meilleure_categorie = None
        meilleur_score = 0.0
        
        for categorie, mots_cles in self.connaissances.items():
            # Chercher des correspondances exactes d'abord
            for mot in mots_cles:
                if mot in question_normalisee.split():
                    logger.debug(f"Catégorie trouvée par mot exact '{mot}': {categorie}")
                    info_question["categorie"] = categorie
                    return info_question
            
            # Si pas de correspondance exacte, vérifier si des mots-clés sont contenus dans la question
            for mot in mots_cles:
                if mot in question_normalisee:
                    logger.debug(f"Catégorie trouvée par inclusion '{mot}': {categorie}")
                    info_question["categorie"] = categorie
                    return info_question
            
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
            info_question["categorie"] = meilleure_categorie
            return info_question
        
        logger.debug(f"Aucune catégorie trouvée, retourne 'inconnu'")
        return info_question
    
    def generer_reponse_contextualisee(self, info_question, question):
        """
        Génère une réponse plus élaborée en fonction du contexte et des informations détaillées de la question.
        
        Args:
            info_question (dict): Informations détaillées sur la question
            question (str): La question posée par l'utilisateur
            
        Returns:
            str: La réponse générée
        """
        categorie = info_question["categorie"]
        sentiment = info_question["sentiment"]["sentiment"]
        type_question = info_question["type_question"]
        
        # Mettre à jour le dernier sentiment détecté
        self.dernier_sentiment = sentiment
        
        # Incrémenter le compteur d'interactions
        self.nb_interactions += 1
        
        # Enregistrer cette question dans les questions fréquentes
        if question.lower() in self.questions_frequentes:
            self.questions_frequentes[question.lower()] += 1
        else:
            self.questions_frequentes[question.lower()] = 1
        
        # Générer une réponse personnalisée selon le contexte
        # Si l'utilisateur exprime un sentiment très négatif, adapter la réponse
        if sentiment == "négatif" and info_question["sentiment"]["score"] < -0.5:
            return "Je suis désolée de constater que vous semblez contrarié. " \
                   "Je suis là pour vous aider. Comment puis-je améliorer votre expérience ou répondre à votre question ?"
        
        # Adapter la réponse selon le nombre d'interactions
        intro = ""
        if self.nb_interactions == 1:
            intro = f"Bienvenue ! C'est notre première interaction. "
        elif self.nb_interactions > 10:
            intro = f"Nous avons déjà eu {self.nb_interactions} échanges ensemble. Je commence à bien vous connaître. "
        
        # Réponses spécifiques selon la catégorie
        if categorie == "heure":
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
            
            reponse = f"{intro}Il est actuellement {heure_actuelle} le {jour_semaine} {jour_mois} {mois_nom} {annee}."
            
            # Ajouter un petit complément selon le moment de la journée
            heure = maintenant.hour
            if 5 <= heure < 12:
                reponse += " Passez une excellente matinée !"
            elif 12 <= heure < 18:
                reponse += " Je vous souhaite un bel après-midi !"
            elif 18 <= heure < 22:
                reponse += " Bonne soirée à vous !"
            else:
                reponse += " Bonne nuit, il est déjà tard !"
                
        elif categorie == "météo":
            # Obtenir les données météo avec le nouveau format
            meteo_message = self.meteo_service.obtenir_meteo(question)
            
            # Le service météo retourne maintenant directement un message formaté
            if isinstance(meteo_message, str):
                reponse = f"{intro}{meteo_message}"
            else:
                # Créer un message plus détaillé et contextuel
                ville = meteo_message.get('ville', 'inconnue')
                temperature = meteo_message.get('temperature', '?')
                condition = meteo_message.get('condition', 'inconnue')
                
                # Ajouter la ville aux préférences utilisateur si elle n'est pas déjà là
                if 'villes_favorites' not in self.preferences_utilisateur:
                    self.preferences_utilisateur['villes_favorites'] = []
                
                if ville not in self.preferences_utilisateur['villes_favorites']:
                    self.preferences_utilisateur['villes_favorites'].append(ville)
                
                reponse = f"{intro}À {ville}, il fait actuellement {temperature}°C avec {condition}."
                
                # Ajouter un conseil selon la météo
                if "pluie" in condition.lower() or "averse" in condition.lower():
                    reponse += " N'oubliez pas votre parapluie si vous sortez !"
                elif "neige" in condition.lower():
                    reponse += " Couvrez-vous bien si vous devez sortir !"
                elif int(temperature) > 30:
                    reponse += " Il fait très chaud, pensez à bien vous hydrater !"
                elif int(temperature) < 5:
                    reponse += " Il fait assez froid, n'oubliez pas de vous couvrir !"
        
        elif categorie == "présentation" and type_question == "information":
            # Présentation plus détaillée si on demande des informations précises
            reponse = f"{intro}Je suis {self.nom}, une assistante IA développée pour vous aider. " \
                     "Mes capacités incluent la consultation de la météo, l'affichage de l'heure, " \
                     "et la possibilité de répondre à diverses questions. " \
                     "Je m'améliore constamment grâce à nos interactions, et j'apprends de nos échanges " \
                     "pour mieux répondre à vos besoins. N'hésitez pas à me poser des questions !"
        
        elif categorie == "humeur":
            template = random.choice(self.reponses["humeur"])
            reponse = f"{intro}{template}"
            
            # Ajouter un suivi si ce n'est pas la première interaction
            if self.nb_interactions > 1:
                if self.dernier_sentiment == "positif":
                    reponse += " Je suis ravie de voir que vous êtes de bonne humeur !"
                elif self.dernier_sentiment == "négatif":
                    reponse += " J'espère que votre journée s'améliore !"
        
        else:
            # Pour les autres catégories, choisir une réponse depuis le dictionnaire
            reponses_possibles = self.reponses.get(categorie, self.reponses["inconnu"])
            template = random.choice(reponses_possibles)
            reponse = f"{intro}{template}"
        
        # Ajouter des suggestions de suivi pour enrichir la conversation
        if random.random() > 0.7 and self.nb_interactions > 2:  # 30% de chance d'ajouter une suggestion
            if 'villes_favorites' in self.preferences_utilisateur and self.preferences_utilisateur['villes_favorites']:
                ville = random.choice(self.preferences_utilisateur['villes_favorites'])
                reponse += f" Au fait, voulez-vous connaître la météo à {ville} aujourd'hui ?"
            elif categorie not in ["météo", "heure"]:
                reponse += " Puis-je vous aider avec autre chose ? Je peux vous donner l'heure ou la météo par exemple."
        
        return reponse
    
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
        
        # Analyser la question en détail
        info_question = self.comprendre_question(question)
        
        # Générer une réponse contextuelle
        reponse = self.generer_reponse_contextualisee(info_question, question)
        
        # Ajouter la réponse à l'historique
        self.historique.append({"type": "reponse", "contenu": reponse})
        
        # Sauvegarder dans la mémoire
        if info_question["categorie"] != "inconnu":
            self.memoire.ajouter_souvenir("interaction", {
                "question": question,
                "categorie": info_question["categorie"],
                "sentiment": info_question["sentiment"]["sentiment"],
                "reponse": reponse
            })
            
            # Si la question semble être une demande d'information, sauvegarder pour la mémoire à long terme
            if info_question["type_question"] == "information" and "inconnu" not in reponse.lower():
                self.memoire.sauvegarder_memoire_long_terme("connaissances", json.dumps({
                    "question": question,
                    "reponse": reponse,
                    "categorie": info_question["categorie"]
                }))
        
        return reponse
    
    def apprendre_nouvelle_connaissance(self, categorie, contenu):
        """
        Permet à l'agent d'apprendre une nouvelle information.
        
        Args:
            categorie (str): La catégorie de l'information
            contenu (str): Le contenu à apprendre
        
        Returns:
            bool: True si l'apprentissage a réussi, False sinon
        """
        try:
            # Ajouter le contenu aux connaissances
            if categorie in self.connaissances:
                # Vérifier si le contenu n'existe pas déjà
                if contenu.lower() not in [c.lower() for c in self.connaissances[categorie]]:
                    self.connaissances[categorie].append(contenu)
                    logger.info(f"Nouvelle connaissance ajoutée dans {categorie}: {contenu}")
                    return True
                else:
                    logger.info(f"La connaissance existe déjà dans {categorie}: {contenu}")
                    return False
            else:
                # Créer une nouvelle catégorie
                self.connaissances[categorie] = [contenu]
                logger.info(f"Nouvelle catégorie créée: {categorie} avec contenu: {contenu}")
                return True
                
        except Exception as e:
            logger.error(f"Erreur lors de l'apprentissage: {e}")
            return False
    
    def obtenir_statistiques(self):
        """
        Retourne des statistiques sur les interactions.
        
        Returns:
            dict: Statistiques sur les interactions
        """
        return {
            "total_interactions": self.nb_interactions,
            "questions_populaires": sorted(self.questions_frequentes.items(), key=lambda x: x[1], reverse=True)[:5],
            "dernier_sentiment": self.dernier_sentiment,
            "preferences": self.preferences_utilisateur
        }
    
    def afficher_historique(self):
        """
        Affiche l'historique des échanges.
        
        Returns:
            list: Liste des échanges
        """
        return self.historique


# Test simple si le fichier est exécuté directement
if __name__ == "__main__":
    agent = Agent("Cindy")
    print(agent.generer_reponse("Bonjour comment vas-tu?"))
    print(agent.generer_reponse("Quelle heure est-il?"))
    print(agent.generer_reponse("Quel temps fait-il à Paris?"))




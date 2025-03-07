"""
Agent IA - Module principal
Ce module contient la classe principale Agent qui gère la logique de notre assistant IA.
"""

import logging
import platform
import locale
import datetime
from nlp_engine import analyser_et_repondre, determiner_intention

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
    Classe Agent: représente notre assistant IA avec ses capacités.
    Utilise nlp_engine pour l'analyse des questions et la génération des réponses.
    """
    
    def __init__(self, nom="Cindy"):
        """
        Initialise un nouvel agent intelligent.
        
        Args:
            nom (str): Le nom de l'agent
        """
        self.nom = nom
        logger.info(f"Agent {self.nom} initialisé")
        
        # Initialiser l'historique des échanges
        self.historique = []
        
        # Compteur d'interactions
        self.nb_interactions = 0
        
        # Préférences utilisateur (comme les villes favorites pour la météo)
        self.preferences_utilisateur = {
            'villes_favorites': ['Paris', 'Lyon', 'Marseille']
        }
        
        print(f"Agent {self.nom} initialisé et prêt à l'emploi!")
    
    def generer_reponse(self, question):
        """
        Génère une réponse en utilisant le moteur NLP.
        Garde une trace de l'historique des échanges.
        
        Args:
            question (str): La question posée par l'utilisateur
            
        Returns:
            dict: Le résultat contenant la réponse et les suggestions
        """
        try:
            # Incrémenter le compteur d'interactions
            self.nb_interactions += 1
            
            # Ajouter la question à l'historique
            self.historique.append({"type": "question", "contenu": question, "timestamp": datetime.datetime.now()})
            
            # Utiliser le moteur NLP pour analyser et répondre
            logger.info(f"Agent {self.nom} analyse la question: {question}")
            resultat = analyser_et_repondre(question)
            logger.info(f"Résultat obtenu de analyser_et_repondre: {resultat}")
            
            # Ajouter la réponse à l'historique
            self.historique.append({"type": "reponse", "contenu": resultat["reponse"], "timestamp": datetime.datetime.now()})
            
            # Mettre à jour les préférences utilisateur si nécessaire
            if resultat["intention"] == "meteo" and "entites" in resultat and "ville" in resultat["entites"]:
                ville = resultat["entites"]["ville"]
                if ville and ville not in self.preferences_utilisateur['villes_favorites']:
                    self.preferences_utilisateur['villes_favorites'].append(ville)
                    logger.info(f"Ville ajoutée aux favoris: {ville}")
            
            return resultat
        except Exception as e:
            logger.error(f"Erreur dans Agent.generer_reponse: {str(e)}")
            return {
                "reponse": "Désolé, une erreur est survenue dans l'agent. Veuillez réessayer.",
                "intention": "erreur",
                "suggestions": ["Qui es-tu?", "Quelle heure est-il?", "Bonjour"]
            }
    
    def obtenir_historique(self, limite=10):
        """
        Retourne l'historique des échanges, limité aux dernières entrées.
        
        Args:
            limite (int): Nombre maximum d'échanges à retourner
            
        Returns:
            list: Liste des derniers échanges
        """
        return self.historique[-limite:] if limite > 0 else self.historique
    
    def obtenir_statistiques(self):
        """
        Retourne des statistiques sur les interactions.
        
        Returns:
            dict: Statistiques sur les interactions
        """
        villes_populaires = self.preferences_utilisateur.get('villes_favorites', [])[:3]
        
        intentions = {}
        for echange in self.historique:
            if echange["type"] == "question":
                intention, _, _ = determiner_intention(echange["contenu"])
                intentions[intention] = intentions.get(intention, 0) + 1
        
        intentions_populaires = sorted(intentions.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "total_interactions": self.nb_interactions,
            "villes_populaires": villes_populaires,
            "intentions_populaires": intentions_populaires
        }


# Test simple si le fichier est exécuté directement
if __name__ == "__main__":
    agent = Agent("Cindy")
    print(agent.generer_reponse("Bonjour comment vas-tu?"))
    print(agent.generer_reponse("Quelle heure est-il?"))
    print(agent.generer_reponse("Quel temps fait-il à Paris?"))




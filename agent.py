"""
Agent IA - Module principal
Ce module contient la classe principale Agent qui gère la logique de notre assistant IA.
"""

import logging
import platform
import locale
import datetime
import random
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
        
        # Contexte de conversation pour rendre l'agent plus naturel
        self.contexte_conversation = {
            'dernier_sujet': None,
            'dernier_sentiment': None,
            'questions_posees': [],
            'sujets_abordes': set(),
            'derniere_ville_meteo': None,
            'derniere_entite_mentionnee': None,
            'attente_reponse': False,  # L'agent attend-il une réponse à sa propre question?
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
            
            # Vérifier si cette question est une réponse à une question que l'agent a posée
            relance = self._generer_relance() if self.contexte_conversation['attente_reponse'] else None
            self.contexte_conversation['attente_reponse'] = False  # Réinitialiser
            
            # Analyser la question et obtenir une réponse
            resultat = analyser_et_repondre(question)
            logger.info(f"Résultat obtenu de analyser_et_repondre: {resultat}")
            
            # Mettre à jour le contexte de conversation
            self._mettre_a_jour_contexte(question, resultat)
            
            # Ajouter une relance ou un suivi si approprié
            resultat = self._enrichir_reponse(resultat, relance)
            
            # Ajouter la réponse à l'historique
            self.historique.append({"type": "reponse", "contenu": resultat["reponse"], "timestamp": datetime.datetime.now()})
            
            # Mettre à jour les préférences utilisateur si nécessaire
            if resultat["intention"] == "meteo" and "entites" in resultat and "ville" in resultat["entites"]:
                ville = resultat["entites"]["ville"]
                if ville and ville not in self.preferences_utilisateur['villes_favorites']:
                    self.preferences_utilisateur['villes_favorites'].append(ville)
                    logger.info(f"Ville ajoutée aux favoris: {ville}")
                self.contexte_conversation['derniere_ville_meteo'] = ville
            
            return resultat
        except Exception as e:
            logger.error(f"Erreur dans Agent.generer_reponse: {str(e)}")
            return {
                "reponse": "Désolé, une erreur est survenue dans l'agent. Veuillez réessayer.",
                "intention": "erreur",
                "suggestions": ["Qui es-tu?", "Quelle heure est-il?", "Bonjour"]
            }
    
    def _mettre_a_jour_contexte(self, question, resultat):
        """
        Met à jour le contexte de conversation en fonction de la question et de la réponse.
        
        Args:
            question (str): La question posée par l'utilisateur
            resultat (dict): Le résultat de l'analyse
        """
        # Sauvegarder le sujet actuel
        self.contexte_conversation['dernier_sujet'] = resultat.get('intention', 'inconnu')
        
        # Ajouter à la liste des sujets abordés
        self.contexte_conversation['sujets_abordes'].add(resultat.get('intention', 'inconnu'))
        
        # Sauvegarder les entités mentionnées
        if 'entites' in resultat and resultat['entites']:
            for entite, valeur in resultat['entites'].items():
                self.contexte_conversation['derniere_entite_mentionnee'] = (entite, valeur)
    
    def _enrichir_reponse(self, resultat, relance=None):
        """
        Enrichit la réponse avec des éléments conversationnels.
        
        Args:
            resultat (dict): Le résultat original
            relance (str): Une éventuelle relance à ajouter
            
        Returns:
            dict: Le résultat enrichi
        """
        reponse_originale = resultat["reponse"]
        
        # Si on a une relance spécifique, l'utiliser
        if relance:
            resultat["reponse"] = f"{reponse_originale} {relance}"
            return resultat
        
        # Si l'utilisateur demande la météo, proposer d'autres villes
        if resultat["intention"] == "meteo" and random.random() < 0.5:
            favorites = self.preferences_utilisateur['villes_favorites']
            if len(favorites) > 1 and self.contexte_conversation.get('derniere_ville_meteo'):
                autre_ville = random.choice([v for v in favorites if v != self.contexte_conversation['derniere_ville_meteo']])
                resultat["reponse"] = f"{reponse_originale} Souhaitez-vous aussi connaître la météo à {autre_ville} ?"
                self.contexte_conversation['attente_reponse'] = True
                
        # Si l'utilisateur n'a jamais posé de question sur un sujet intéressant, suggérer
        sujets_manquants = set(['meteo', 'heure', 'blague', 'identite']) - self.contexte_conversation['sujets_abordes']
        if sujets_manquants and self.nb_interactions > 2 and random.random() < 0.3:
            sujet_suggere = random.choice(list(sujets_manquants))
            if sujet_suggere == 'meteo':
                ville = random.choice(self.preferences_utilisateur['villes_favorites'])
                resultat["reponse"] = f"{reponse_originale} Au fait, souhaitez-vous connaître la météo à {ville} ?"
            elif sujet_suggere == 'blague':
                resultat["reponse"] = f"{reponse_originale} Je peux aussi vous raconter une blague si vous voulez !"
            elif sujet_suggere == 'heure':
                resultat["reponse"] = f"{reponse_originale} Avez-vous besoin de connaître l'heure ou la date ?"
            self.contexte_conversation['attente_reponse'] = True
            return resultat
            
        # Par défaut, retourner le résultat inchangé
        return resultat
        
    def _generer_relance(self):
        """
        Génère une relance basée sur le contexte précédent.
        
        Returns:
            str: Une phrase de relance
        """
        relances_generiques = [
            "Puis-je vous aider avec autre chose ?",
            "Avez-vous d'autres questions ?",
            "Est-ce que cela répond à votre question ?",
            "Y a-t-il autre chose que vous aimeriez savoir ?"
        ]
        
        return random.choice(relances_generiques)
    
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




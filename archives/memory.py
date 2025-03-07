"""
Module de mémoire contextuelle
Ce module permet à l'agent de stocker et récupérer des informations des conversations précédentes.
"""

import json
import os
import logging
from datetime import datetime

# Configuration du logger
logger = logging.getLogger('assistant_ia.memory')

class Memoire:
    """
    Classe pour gérer la mémoire contextuelle de l'agent.
    """
    
    def __init__(self, taille_max=50):
        """
        Initialise le système de mémoire.
        
        Args:
            taille_max (int): Nombre maximum d'éléments à conserver en mémoire
        """
        self.taille_max = taille_max
        self.memoire_court_terme = []  # Mémoire pour la conversation en cours
        self.memoire_long_terme = {}   # Mémoire persistante entre les sessions
        self.fichier_memoire = "memoire_agent.json"
        
        # Charger la mémoire à long terme si elle existe
        self.charger_memoire()
    
    def ajouter_souvenir(self, type_souvenir, contenu):
        """
        Ajoute un nouvel élément à la mémoire court terme.
        
        Args:
            type_souvenir (str): Type de souvenir (ex: "question", "réponse", "fait")
            contenu (str): Contenu du souvenir
        """
        # Créer un nouveau souvenir avec horodatage
        nouveau_souvenir = {
            "type": type_souvenir,
            "contenu": contenu,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Ajouter à la mémoire court terme
        self.memoire_court_terme.append(nouveau_souvenir)
        
        # Supprimer les plus anciens souvenirs si la taille maximale est dépassée
        if len(self.memoire_court_terme) > self.taille_max:
            self.memoire_court_terme.pop(0)  # Supprimer le plus ancien
    
    def obtenir_contexte_recent(self, nombre=5):
        """
        Récupère les souvenirs les plus récents.
        
        Args:
            nombre (int): Nombre de souvenirs à récupérer
            
        Returns:
            list: Liste des souvenirs récents
        """
        # Retourner les N derniers souvenirs (du plus récent au plus ancien)
        return self.memoire_court_terme[-nombre:][::-1] if self.memoire_court_terme else []
    
    def sauvegarder_memoire_long_terme(self, categorie, information):
        """
        Sauvegarde une information dans la mémoire à long terme.
        
        Args:
            categorie (str): Catégorie de l'information
            information (str): Information à sauvegarder
        """
        # S'assurer que la catégorie existe
        if categorie not in self.memoire_long_terme:
            self.memoire_long_terme[categorie] = []
        
        # Ajouter l'information à la catégorie
        self.memoire_long_terme[categorie].append({
            "contenu": information,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Sauvegarder dans le fichier
        try:
            self.sauvegarder_memoire()
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la mémoire à long terme: {e}")
    
    def rechercher_memoire_long_terme(self, categorie, mot_cle):
        """
        Recherche des informations dans la mémoire à long terme.
        
        Args:
            categorie (str): Catégorie dans laquelle chercher
            mot_cle (str): Mot-clé à rechercher
            
        Returns:
            list: Liste des entrées correspondant à la recherche
        """
        resultats = []
        
        # Vérifier si la catégorie existe
        if categorie in self.memoire_long_terme:
            # Chercher les entrées qui contiennent le mot-clé
            mot_cle = mot_cle.lower()
            for entree in self.memoire_long_terme[categorie]:
                if mot_cle in entree["contenu"].lower():
                    resultats.append(entree)
        
        return resultats
    
    def sauvegarder_memoire(self):
        """Sauvegarde la mémoire à long terme dans un fichier JSON."""
        try:
            with open(self.fichier_memoire, 'w', encoding='utf-8') as fichier:
                json.dump(self.memoire_long_terme, fichier, ensure_ascii=False, indent=2)
            logger.info(f"Mémoire sauvegardée dans {self.fichier_memoire}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la mémoire: {e}")
            # Créer une sauvegarde de secours en cas d'erreur
            backup_file = f"memoire_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(backup_file, 'w', encoding='utf-8') as fichier:
                    json.dump(self.memoire_long_terme, fichier, ensure_ascii=False, indent=2)
                logger.info(f"Sauvegarde de secours créée: {backup_file}")
            except Exception as backup_error:
                logger.critical(f"Impossible de créer une sauvegarde: {backup_error}")
    
    def charger_memoire(self):
        """Charge la mémoire à long terme depuis un fichier JSON."""
        try:
            # Vérifier si le fichier existe
            if os.path.exists(self.fichier_memoire):
                with open(self.fichier_memoire, 'r', encoding='utf-8') as fichier:
                    self.memoire_long_terme = json.load(fichier)
                logger.info(f"Mémoire chargée depuis {self.fichier_memoire}")
            else:
                logger.info(f"Aucun fichier de mémoire trouvé. Création d'une nouvelle mémoire.")
                self.memoire_long_terme = {}
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON: {e}. Création d'une sauvegarde et d'une nouvelle mémoire.")
            # Si le fichier est corrompu, créer une sauvegarde et recommencer avec une mémoire vide
            if os.path.exists(self.fichier_memoire):
                backup_file = f"{self.fichier_memoire}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                try:
                    os.rename(self.fichier_memoire, backup_file)
                    logger.info(f"Fichier corrompu sauvegardé sous {backup_file}")
                except Exception as rename_error:
                    logger.error(f"Impossible de renommer le fichier corrompu: {rename_error}")
            self.memoire_long_terme = {}
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la mémoire: {e}")
            self.memoire_long_terme = {}


# Test simple si le fichier est exécuté directement
if __name__ == "__main__":
    memoire = Memoire()
    
    # Ajouter quelques souvenirs
    memoire.ajouter_souvenir("question", "Quelle est la capitale de la France?")
    memoire.ajouter_souvenir("reponse", "La capitale de la France est Paris.")
    
    # Sauvegarder dans la mémoire à long terme
    memoire.sauvegarder_memoire_long_terme("faits_geographiques", "Paris est la capitale de la France.")
    
    # Afficher le contexte récent
    print("Contexte récent:")
    for souvenir in memoire.obtenir_contexte_recent():
        print(f"{souvenir['type']}: {souvenir['contenu']} ({souvenir['timestamp']})")
    
    # Rechercher un souvenir
    print("\nRésultats de recherche pour 'France':")
    resultats = memoire.rechercher_memoire_long_terme("faits_geographiques", "France")
    for souvenir in resultats:
        print(f"- {souvenir['contenu']}") 
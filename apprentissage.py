"""
Module d'apprentissage pour l'agent Cindy
Ce module permet d'entraîner et d'améliorer les capacités de l'agent.
"""

import json
import os
import re
from collections import Counter, defaultdict

# Chemin vers les fichiers de données
DATA_DIR = "data"
INTERACTIONS_FILE = os.path.join(DATA_DIR, "interactions.json")
STATS_FILE = os.path.join(DATA_DIR, "statistiques.json")
MODELE_FILE = os.path.join(DATA_DIR, "modele.json")

# Créer le répertoire de données s'il n'existe pas
os.makedirs(DATA_DIR, exist_ok=True)

def sauvegarder_interaction(question, reponse, intention, score, entites=None):
    """
    Sauvegarde une interaction avec l'utilisateur pour l'apprentissage.
    """
    # Créer une structure pour stocker l'interaction
    interaction = {
        "question": question,
        "reponse": reponse,
        "intention": intention,
        "score": score,
        "entites": entites or {}
    }
    
    # Charger les interactions existantes
    interactions = []
    if os.path.exists(INTERACTIONS_FILE):
        try:
            with open(INTERACTIONS_FILE, 'r', encoding='utf-8') as f:
                interactions = json.load(f)
        except:
            # En cas d'erreur, on démarre avec une liste vide
            interactions = []
    
    # Ajouter la nouvelle interaction
    interactions.append(interaction)
    
    # Sauvegarder les interactions
    with open(INTERACTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(interactions, f, ensure_ascii=False, indent=4)
    
    return True

def analyser_interactions():
    """
    Analyse les interactions pour extraire des tendances et des statistiques.
    """
    if not os.path.exists(INTERACTIONS_FILE):
        return {}
    
    # Charger les interactions
    try:
        with open(INTERACTIONS_FILE, 'r', encoding='utf-8') as f:
            interactions = json.load(f)
    except:
        return {}
    
    # Analyser les intentions
    intentions = Counter([interaction["intention"] for interaction in interactions])
    
    # Analyser les entités par type d'intention
    entites_par_intention = defaultdict(Counter)
    for interaction in interactions:
        for entite_type, entite_valeur in interaction.get("entites", {}).items():
            entites_par_intention[interaction["intention"]][entite_valeur] += 1
    
    # Analyser les scores moyens par intention
    scores_moyens = {}
    for intention, count in intentions.items():
        total_score = sum(interaction["score"] for interaction in interactions 
                          if interaction["intention"] == intention)
        scores_moyens[intention] = total_score / count if count > 0 else 0
    
    # Extraire les questions fréquentes
    questions_frequentes = Counter([interaction["question"] for interaction in interactions])
    top_questions = questions_frequentes.most_common(10)
    
    # Construire les statistiques
    statistiques = {
        "nombre_interactions": len(interactions),
        "distribution_intentions": dict(intentions),
        "entites_frequentes": {k: dict(v.most_common(5)) for k, v in entites_par_intention.items()},
        "scores_moyens": scores_moyens,
        "questions_frequentes": top_questions
    }
    
    # Sauvegarder les statistiques
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(statistiques, f, ensure_ascii=False, indent=4)
    
    return statistiques

def ameliorer_modele():
    """
    Améliore le modèle de compréhension en fonction des interactions passées.
    """
    if not os.path.exists(INTERACTIONS_FILE):
        return False
    
    # Charger les interactions
    try:
        with open(INTERACTIONS_FILE, 'r', encoding='utf-8') as f:
            interactions = json.load(f)
    except:
        return False
    
    # Analyser les mots-clés par intention
    mots_cles_par_intention = defaultdict(Counter)
    for interaction in interactions:
        question = interaction["question"].lower()
        intention = interaction["intention"]
        
        # Ignorer les intentions inconnues
        if intention == "inconnu":
            continue
        
        # Extraire les mots de la question (sans ponctuation)
        mots = re.findall(r'\b\w+\b', question)
        for mot in mots:
            if len(mot) > 2:  # Ignorer les mots très courts
                mots_cles_par_intention[intention][mot] += 1
    
    # Charger le modèle existant
    modele = {}
    if os.path.exists(MODELE_FILE):
        try:
            with open(MODELE_FILE, 'r', encoding='utf-8') as f:
                modele = json.load(f)
        except:
            modele = {}
    
    # Mettre à jour le modèle avec les nouveaux mots-clés
    for intention, mots_compteur in mots_cles_par_intention.items():
        if intention not in modele:
            modele[intention] = {"mots_cles": {}}
        
        for mot, count in mots_compteur.most_common(30):  # Prendre les 30 mots les plus fréquents
            if mot not in modele[intention]["mots_cles"]:
                modele[intention]["mots_cles"][mot] = 0
            
            # Augmenter le poids en fonction de la fréquence
            modele[intention]["mots_cles"][mot] = min(5, modele[intention]["mots_cles"].get(mot, 0) + count // 2)
    
    # Sauvegarder le modèle amélioré
    with open(MODELE_FILE, 'w', encoding='utf-8') as f:
        json.dump(modele, f, ensure_ascii=False, indent=4)
    
    return True

def charger_modele_ameliore():
    """
    Charge le modèle amélioré s'il existe.
    """
    if not os.path.exists(MODELE_FILE):
        return None
    
    try:
        with open(MODELE_FILE, 'r', encoding='utf-8') as f:
            modele = json.load(f)
        return modele
    except:
        return None

if __name__ == "__main__":
    # Si ce script est exécuté directement, lancer une analyse
    stats = analyser_interactions()
    print("Statistiques des interactions:")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    # Améliorer le modèle
    succes = ameliorer_modele()
    if succes:
        print("Le modèle a été amélioré avec succès!")
    else:
        print("Impossible d'améliorer le modèle.") 
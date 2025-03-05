"""
Module d'apprentissage pour l'agent Cindy
Ce module permet d'entraîner et d'améliorer les capacités de l'agent.
"""

import json
import os
import re
import logging
from collections import Counter, defaultdict
from datetime import datetime

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("apprentissage.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("apprentissage")

# Chemin vers les fichiers de données
DATA_DIR = "data"
INTERACTIONS_FILE = os.path.join(DATA_DIR, "interactions.json")
STATS_FILE = os.path.join(DATA_DIR, "statistiques.json")
MODELE_FILE = os.path.join(DATA_DIR, "modele.json")
MOTIFS_FILE = os.path.join(DATA_DIR, "motifs_questions.json")

# Créer le répertoire de données s'il n'existe pas
os.makedirs(DATA_DIR, exist_ok=True)

def sauvegarder_interaction(question, reponse, intention, score, entites=None):
    """
    Sauvegarde une interaction avec l'utilisateur pour l'apprentissage.
    
    Args:
        question (str): La question posée par l'utilisateur
        reponse (str): La réponse générée par l'agent
        intention (str): L'intention détectée
        score (float): Le score de confiance de l'intention
        entites (dict, optional): Les entités extraites
        
    Returns:
        bool: True si l'opération a réussi
    """
    # Créer une structure pour stocker l'interaction
    interaction = {
        "question": question,
        "reponse": reponse,
        "intention": intention,
        "score": score,
        "entites": entites or {},
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Charger les interactions existantes
    interactions = []
    if os.path.exists(INTERACTIONS_FILE):
        try:
            with open(INTERACTIONS_FILE, 'r', encoding='utf-8') as f:
                interactions = json.load(f)
        except Exception as e:
            logger.error(f"Erreur lors du chargement des interactions: {str(e)}")
            # En cas d'erreur, on démarre avec une liste vide
            interactions = []
    
    # Ajouter la nouvelle interaction
    interactions.append(interaction)
    
    # Sauvegarder les interactions
    try:
        with open(INTERACTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(interactions, f, ensure_ascii=False, indent=4)
        
        # Mettre à jour les motifs de questions après chaque sauvegarde
        extraire_motifs_questions()
        
        # Analyser les interactions pour mettre à jour les statistiques
        if len(interactions) % 10 == 0:  # Toutes les 10 interactions
            analyser_interactions()
            ameliorer_modele()
            
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de l'interaction: {str(e)}")
        return False

def analyser_interactions():
    """
    Analyse les interactions pour extraire des tendances et des statistiques.
    
    Returns:
        dict: Les statistiques extraites
    """
    if not os.path.exists(INTERACTIONS_FILE):
        return {}
    
    # Charger les interactions
    try:
        with open(INTERACTIONS_FILE, 'r', encoding='utf-8') as f:
            interactions = json.load(f)
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des interactions: {str(e)}")
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
    questions_frequentes = Counter([interaction["question"].lower() for interaction in interactions])
    top_questions = questions_frequentes.most_common(10)
    
    # Analyser l'évolution des intentions au fil du temps
    intentions_par_jour = defaultdict(Counter)
    for interaction in interactions:
        if "timestamp" in interaction:
            date = interaction["timestamp"].split()[0]  # Prendre juste la date
            intentions_par_jour[date][interaction["intention"]] += 1
    
    # Construire les statistiques
    statistiques = {
        "nombre_interactions": len(interactions),
        "distribution_intentions": dict(intentions),
        "entites_frequentes": {k: dict(v.most_common(5)) for k, v in entites_par_intention.items()},
        "scores_moyens": scores_moyens,
        "questions_frequentes": top_questions,
        "intentions_par_jour": {k: dict(v) for k, v in intentions_par_jour.items()},
        "derniere_mise_a_jour": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Sauvegarder les statistiques
    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(statistiques, f, ensure_ascii=False, indent=4)
        
        logger.info(f"Statistiques mises à jour: {len(interactions)} interactions analysées")
        return statistiques
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des statistiques: {str(e)}")
        return {}

def extraire_motifs_questions():
    """
    Extrait des motifs communs dans les questions des utilisateurs.
    
    Returns:
        dict: Les motifs extraits par intention
    """
    if not os.path.exists(INTERACTIONS_FILE):
        return {}
    
    # Charger les interactions
    try:
        with open(INTERACTIONS_FILE, 'r', encoding='utf-8') as f:
            interactions = json.load(f)
    except Exception as e:
        logger.error(f"Erreur lors du chargement des interactions pour l'extraction des motifs: {str(e)}")
        return {}
    
    # Regrouper les questions par intention
    questions_par_intention = defaultdict(list)
    for interaction in interactions:
        questions_par_intention[interaction["intention"]].append(interaction["question"].lower())
    
    # Extraire des motifs pour chaque intention
    motifs_par_intention = {}
    for intention, questions in questions_par_intention.items():
        # Ignorer les intentions avec trop peu de questions
        if len(questions) < 3:
            continue
        
        # Extraire des expressions communes
        expressions = []
        for question in questions:
            # Nettoyer la question
            question_clean = re.sub(r'[^\w\s]', ' ', question)
            words = question_clean.split()
            
            # Extraire des expressions de 2-3 mots
            for i in range(len(words) - 1):
                if i + 1 < len(words):
                    expressions.append(" ".join(words[i:i+2]))
                if i + 2 < len(words):
                    expressions.append(" ".join(words[i:i+3]))
        
        # Compter les expressions
        expr_counter = Counter(expressions)
        
        # Garder seulement celles qui apparaissent plus d'une fois
        motifs = [expr for expr, count in expr_counter.most_common(10) if count > 1]
        
        if motifs:
            motifs_par_intention[intention] = motifs
    
    # Sauvegarder les motifs
    try:
        with open(MOTIFS_FILE, 'w', encoding='utf-8') as f:
            json.dump(motifs_par_intention, f, ensure_ascii=False, indent=4)
        
        logger.info(f"Motifs de questions extraits pour {len(motifs_par_intention)} intentions")
        return motifs_par_intention
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des motifs: {str(e)}")
        return {}

def ameliorer_modele():
    """
    Améliore le modèle de compréhension en fonction des interactions passées.
    
    Returns:
        bool: True si l'opération a réussi
    """
    if not os.path.exists(INTERACTIONS_FILE):
        return False
    
    # Charger les interactions
    try:
        with open(INTERACTIONS_FILE, 'r', encoding='utf-8') as f:
            interactions = json.load(f)
    except Exception as e:
        logger.error(f"Erreur lors du chargement des interactions pour l'amélioration du modèle: {str(e)}")
        return False
    
    # Analyser les mots-clés par intention
    mots_cles_par_intention = defaultdict(Counter)
    expressions_par_intention = defaultdict(Counter)
    
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
        
        # Extraire des expressions de 2-3 mots
        words = re.sub(r'[^\w\s]', ' ', question).split()
        for i in range(len(words) - 1):
            if i + 1 < len(words) and all(len(w) > 2 for w in words[i:i+2]):
                expressions_par_intention[intention][" ".join(words[i:i+2])] += 1
            if i + 2 < len(words) and all(len(w) > 2 for w in words[i:i+3]):
                expressions_par_intention[intention][" ".join(words[i:i+3])] += 1
    
    # Charger le modèle existant
    modele = {}
    if os.path.exists(MODELE_FILE):
        try:
            with open(MODELE_FILE, 'r', encoding='utf-8') as f:
                modele = json.load(f)
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle existant: {str(e)}")
            modele = {}
    
    # Mettre à jour le modèle avec les nouveaux mots-clés
    for intention, mots_compteur in mots_cles_par_intention.items():
        if intention not in modele:
            modele[intention] = {"mots_cles": {}, "expressions": {}}
        
        for mot, count in mots_compteur.most_common(30):  # Prendre les 30 mots les plus fréquents
            if mot not in modele[intention]["mots_cles"]:
                modele[intention]["mots_cles"][mot] = 0
            
            # Augmenter le poids en fonction de la fréquence
            modele[intention]["mots_cles"][mot] = min(5, modele[intention]["mots_cles"].get(mot, 0) + count // 2)
    
    # Mettre à jour le modèle avec les expressions
    for intention, expr_compteur in expressions_par_intention.items():
        if intention not in modele:
            modele[intention] = {"mots_cles": {}, "expressions": {}}
        
        # Ajouter la section expressions si elle n'existe pas
        if "expressions" not in modele[intention]:
            modele[intention]["expressions"] = {}
        
        for expr, count in expr_compteur.most_common(15):  # Prendre les 15 expressions les plus fréquentes
            if count < 2:  # Ignorer les expressions uniques
                continue
                
            if expr not in modele[intention]["expressions"]:
                modele[intention]["expressions"][expr] = 0
            
            # Les expressions ont un poids plus élevé
            modele[intention]["expressions"][expr] = min(8, modele[intention]["expressions"].get(expr, 0) + count)
    
    # Sauvegarder le modèle amélioré
    try:
        with open(MODELE_FILE, 'w', encoding='utf-8') as f:
            json.dump(modele, f, ensure_ascii=False, indent=4)
        
        logger.info(f"Modèle amélioré pour {len(modele)} intentions")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du modèle amélioré: {str(e)}")
        return False

def charger_modele_ameliore():
    """
    Charge le modèle amélioré s'il existe.
    
    Returns:
        dict or None: Le modèle amélioré ou None si non disponible
    """
    if not os.path.exists(MODELE_FILE):
        logger.info("Aucun modèle amélioré trouvé")
        return None
    
    try:
        with open(MODELE_FILE, 'r', encoding='utf-8') as f:
            modele = json.load(f)
        logger.info(f"Modèle amélioré chargé avec {len(modele)} intentions")
        return modele
    except Exception as e:
        logger.error(f"Erreur lors du chargement du modèle amélioré: {str(e)}")
        return None

def predire_intention(question, modele_ameliore=None):
    """
    Prédit l'intention la plus probable pour une question en utilisant 
    le modèle amélioré si disponible.
    
    Args:
        question (str): La question posée
        modele_ameliore (dict, optional): Le modèle amélioré
        
    Returns:
        tuple: (intention, score) ou (None, 0) si pas de prédiction
    """
    if not modele_ameliore:
        modele_ameliore = charger_modele_ameliore()
    
    if not modele_ameliore:
        return None, 0
    
    # Nettoyer la question
    question = question.lower()
    question_clean = re.sub(r'[^\w\s]', ' ', question)
    mots = re.findall(r'\b\w+\b', question_clean)
    
    # Calculer un score pour chaque intention
    scores = {}
    for intention, donnees in modele_ameliore.items():
        score = 0
        
        # Vérifier les mots-clés
        for mot in mots:
            if mot in donnees.get("mots_cles", {}):
                score += donnees["mots_cles"][mot]
        
        # Vérifier les expressions (poids plus élevé)
        for expr, poids in donnees.get("expressions", {}).items():
            if expr in question_clean:
                score += poids
        
        scores[intention] = score
    
    # Trouver l'intention avec le meilleur score
    if scores:
        intention_max = max(scores.items(), key=lambda x: x[1])
        if intention_max[1] > 0:
            return intention_max
    
    return None, 0

def obtenir_statistiques_agent():
    """
    Récupère les statistiques actuelles de l'agent.
    
    Returns:
        dict: Les statistiques de l'agent
    """
    if not os.path.exists(STATS_FILE):
        return analyser_interactions()
    
    try:
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            stats = json.load(f)
        return stats
    except Exception as e:
        logger.error(f"Erreur lors du chargement des statistiques: {str(e)}")
        return {}

if __name__ == "__main__":
    # Si ce script est exécuté directement, lancer une analyse complète
    print("Analyse des interactions...")
    stats = analyser_interactions()
    print(f"Nombre total d'interactions: {stats.get('nombre_interactions', 0)}")
    print("Distribution des intentions:")
    for intention, count in stats.get('distribution_intentions', {}).items():
        print(f"  - {intention}: {count}")
    
    print("\nExtraction des motifs de questions...")
    motifs = extraire_motifs_questions()
    for intention, patterns in motifs.items():
        print(f"Motifs pour '{intention}':")
        for pattern in patterns:
            print(f"  - {pattern}")
    
    print("\nAmélioration du modèle...")
    succes = ameliorer_modele()
    if succes:
        print("Le modèle a été amélioré avec succès!")
    else:
        print("Impossible d'améliorer le modèle.") 
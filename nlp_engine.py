"""
Module de traitement du langage naturel pour l'agent Cindy.
Ce module permet d'analyser les questions des utilisateurs et de générer des réponses appropriées.
"""

import re
import random
import logging
from datetime import datetime
from external_services import MeteoService

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

# Initialisation du service météo
meteo_service = MeteoService()

# Importer le module centralisé des réponses
try:
    import reponses as reponses_module
    has_reponses_module = True
    logger.info("Module de réponses centralisées importé avec succès")
except ImportError:
    has_reponses_module = False
    logger.warning("Module de réponses centralisées non trouvé, création d'un module minimal")
    
    # Créer un module minimal si nécessaire
    try:
        with open('reponses.py', 'w', encoding='utf-8') as f:
            f.write('''"""
Module centralisé pour les réponses de l'agent Cindy.
Ce fichier regroupe toutes les réponses possibles pour éviter les duplications
et assurer la cohérence.
"""

def obtenir_reponses(nom_agent="Cindy"):
    """
    Génère un dictionnaire de réponses en intégrant le nom de l'agent.
    """
    return {
        "salutation": [f"Bonjour ! Je suis {nom_agent}, votre assistant. Comment puis-je vous aider ?"],
        "meteo": ["Je vais consulter la météo pour vous."],
        "heure": ["Il est actuellement [HEURE]."],
        "date": ["Nous sommes le [DATE]."],
        "bien_etre": ["Je vais très bien, merci ! Et vous, comment allez-vous ?"],
        "identite": [f"Je suis {nom_agent}, votre assistant IA. Je peux vous aider avec la météo, l'heure et bien d'autres choses !"],
        "createur": ["Ma créatrice est Cindy Singer, une experte en intelligence artificielle travaillant chez Digital Factory."],
        "fonctionnement": ["Mon fonctionnement repose sur l'analyse de votre texte pour en extraire le sens et l'intention."],
        "inconnu": ["Je ne comprends pas votre question. Pouvez-vous reformuler ?"]
    }

def obtenir_suggestions(intention="inconnu"):
    """
    Fournit des suggestions de questions basées sur l'intention détectée.
    """
    suggestions = {
        "salutation": ["Quelle heure est-il ?", "Quelle est la météo à Paris ?", "Comment vas-tu ?"],
        "meteo": ["Quel temps fait-il à Lyon ?", "Quelle heure est-il ?", "Qui t'a créé ?"],
        "heure": ["Quelle est la météo à Paris ?", "Comment vas-tu ?", "Qui es-tu ?"],
        "bien_etre": ["Quelle heure est-il ?", "Raconte-moi une blague", "Quel temps fait-il à Paris ?"],
        "identite": ["Qui t'a créé ?", "Comment fonctionnes-tu ?", "Quelle est la météo à Paris ?"],
        "createur": ["Comment fonctionnes-tu ?", "Quelle est la météo à Paris ?", "Raconte-moi une blague"],
        "fonctionnement": ["Qui t'a créé ?", "Quelle est la météo à Paris ?", "Raconte-moi une blague"],
        "inconnu": ["Quelle heure est-il ?", "Quelle est la météo à Paris ?", "Comment vas-tu ?"]
    }
    
    return suggestions.get(intention, suggestions["inconnu"])
''')
        import reponses as reponses_module
        has_reponses_module = True
        logger.info("Module de réponses centralisées créé et importé avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de la création du module de réponses: {str(e)}")
        has_reponses_module = False

def determiner_intention(question):
    """
    Détermine l'intention de l'utilisateur à partir de sa question.
    
    Args:
        question (str): La question posée par l'utilisateur
        
    Returns:
        tuple: (intention détectée, score de confiance, entités extraites)
    """
    # Convertir en minuscules et nettoyer la question
    question_lower = question.lower().strip()
    
    # Dictionnaire pour stocker les entités extraites
    entites = {}
    
    # ==== Cas spécial pour les questions sur l'heure ====
    patterns_heure = [
        r"\bquelle\s+heure\s+est[- ]il\b",
        r"\bl'heure\b",
        r"\bheure actuelle\b",
        r"\bheure est[- ]il\b"
    ]
    
    for pattern in patterns_heure:
        if re.search(pattern, question_lower):
            logger.info(f"Question sur l'heure détectée: {question}")
            return "heure", 1.0, entites
    
    # ==== Cas spécial pour les questions sur la date ====
    patterns_date = [
        r"\bquelle\s+(est\s+la\s+|)date\b",
        r"\bquel\s+jour\s+(sommes[- ]nous|est[- ]on|est[- ]il|on\s+est)\b",
        r"\bquel\s+jour\s+est[- ]ce\b",
        r"\ben\s+quel\s+jour\s+sommes[- ]nous\b",
        r"\bla\s+date\s+d'aujourd'hui\b",
        r"\bla\s+date\s+du\s+jour\b",
        r"\bdate\s+d'aujourd'hui\b",
        r"\bdate\s+du\s+jour\b",
        r"\bquel\s+est\s+le\s+jour\b"
    ]
    
    for pattern in patterns_date:
        if re.search(pattern, question_lower):
            logger.info(f"Question sur la date détectée: {question}")
            return "date", 1.0, entites
    
    # ==== Cas spécial pour les questions météo ====
    patterns_meteo = [
        r"\bm[ée]t[ée]o\b", 
        r"\btemps\b.*\b(à|a|dans|en|de)\b",
        r"\btemps\s+qu'il\s+fait\b",
        r"\btemps\s+fait[- ]il\b", 
        r"\btemps\s+(à|a|dans|en|de)\b",
        r"\bquel\s+temps\b",
        r"\bclimat\b",
        r"\bfait[- ]il\s+(chaud|froid|beau)\b", 
        r"\btemperature\b", 
        r"\btempérature\b",
        r"\bdegr[ée]s?\b",
        r"\bdonne[- ]moi\s+le\s+temps\b",
        r"\bdonne[- ]moi\s+la\s+m[ée]t[ée]o\b",
        r"\bhumidit[ée]\b",
        r"\btaux\s+d[\"']humidit[ée]\b",
        r"\bpleut\b",
        r"\bpleuvoir\b",
        r"\best[\s-]ce\s+qu[\"']il\s+pleut\b",
        r"\bcombien\s+de\s+degr[ée]s\b",
        r"\bc[o\"]nna[iî]tre\s+(?:la|le)\s+(?:m[ée]t[ée]o|temps|temp[ée]rature|climat|humidit[ée])\b",
        r"\bj[\"']aimerais\s+(?:conna[iî]tre|savoir)\s+(?:la|le)\s+(?:m[ée]t[ée]o|temps|temp[ée]rature|climat|humidit[ée])\b",
        r"\bquel(?:le)?\s+est\s+(?:la|le)\s+(?:m[ée]t[ée]o|temps|temp[ée]rature|climat|humidit[ée])\b",
        r"\best[\s-]ce\s+qu[\"']il\s+(fait\s+beau|pleut|neige)\b",
        r"\by[\s-]a[\s-]t[\s-]il\s+(du\s+soleil|de\s+la\s+pluie|de\s+la\s+neige)\b",
        r"\bfait[\s-]il\s+(beau|chaud|froid)\b",
        r"\ba[\s-]t[\s-]il\s+(plu|neigé)\b",
        r"\bva[\s-]t[\s-]il\s+(pleuvoir|neiger)\b"
    ]
    
    for pattern in patterns_meteo:
        if re.search(pattern, question_lower):
            # Recherche de villes
            villes_patterns = [
                r"\b(à|a|pour|dans|sur|en|de|au)\s+([A-Za-zÀ-ÿ]+(?:[-\s][A-Za-zÀ-ÿ]+)*)\b",
                r"\bà\s+([A-Za-zÀ-ÿ]+(?:[-\s][A-Za-zÀ-ÿ]+)*)\s*\?", # Capture "à Paris ?"
                r"\bpleut.*?\b(à|a|en|au|aux)\s+([A-Za-zÀ-ÿ]+(?:[-\s][A-Za-zÀ-ÿ]+)*)\b", # "pleut-il à Paris"
                r"\bfait-il\s+(?:beau|chaud|froid).*?\b(à|a|en|au|aux)\s+([A-Za-zÀ-ÿ]+(?:[-\s][A-Za-zÀ-ÿ]+)*)\b", # "fait-il beau à Paris"
                # Nouvelle ligne pour capturer plus généralement les villes
                r"(?:pleut|neige|beau).*?(?:à|a|en|au|dans|de)\s+([A-Za-zÀ-ÿ]+(?:[-\s][A-Za-zÀ-ÿ]+)*)"
            ]
            
            # Essayer tous les patterns
            ville_trouvee = False
            for ville_pattern in villes_patterns:
                match_ville = re.search(ville_pattern, question)
                if match_ville:
                    # Si le pattern a deux groupes, prendre le deuxième (la ville)
                    if len(match_ville.groups()) > 1:
                        ville = match_ville.group(2)
                    else:
                        ville = match_ville.group(1)
                    
                    # Capitaliser la première lettre
                    ville = ville.strip().title()
                    entites["ville"] = ville
                    logger.info(f"Ville extraite: {ville}")
                    ville_trouvee = True
                    break
            
            logger.info(f"Question météo détectée: {question}")
            return "meteo", 1.0, entites
    
    # ==== Cas spécial pour les questions sur le bien-être ====
    patterns_bien_etre = [
        r"\bcomment\s+(vas|va|allez)[- ](tu|vous)\b",
        r"\bça\s+va\b",
        r"\btu\s+vas\s+bien\b",
        r"\bcomment\s+tu\s+te\s+sens\b",
        r"\bhow\s+are\s+you\b",
        r"\btu\s+vas\s+comment\b",
        r"\bcomment\s+te\s+portes[- ]tu\b",
        r"\bça\s+roule\b",
        r"\bt'es\s+en\s+forme\b",
        r"\bla\s+forme\b",
        r"\btu\s+te\s+sens\s+bien\b"
    ]
    
    for pattern in patterns_bien_etre:
        if re.search(pattern, question_lower):
            logger.info(f"Question sur le bien-être détectée: {question}")
            return "bien_etre", 1.0, entites
    
    # ==== Cas spécial pour les questions sur l'identité ====
    patterns_identite = [
        r"\bqui\s+(es[- ]tu|êtes[- ]vous|est[- ]ce que tu es)\b",
        r"\btu\s+(es|est)\s+qui\b",
        r"\bcomment\s+(t'appelles[- ]tu|vous appelez[- ]vous|tu t'appelles)\b",
        r"\bton\s+nom\b",
        r"\bquel\s+est\s+ton\s+nom\b"
    ]
    
    for pattern in patterns_identite:
        if re.search(pattern, question_lower):
            logger.info(f"Question sur l'identité détectée: {question}")
            return "identite", 1.0, entites
            
    # ==== Cas spécial pour les réponses aux questions de bien-être ====
    # Quand l'agent demande "Comment vas-tu ?" et que l'utilisateur répond
    patterns_reponse_bien_etre = [
        r"^(je\s+vais|ça\s+va|ca\s+va|je\s+me\s+sens|je\s+me\s+porte|je\s+suis)(\s+[a-zéèêàôûçñ]+){1,3}$",
        r"^(bien|mal|super|génial|bof|pas\s+mal|très\s+bien|excellent|parfait|moyen|pas\s+top)$",
        r"^(oui|non|ça\s+peut\s+aller|comme\s+ci\s+comme\s+ça|couci\s+couça|on\s+fait\s+aller)$",
        r"^(en\s+forme|fatigué|fatigué|épuisé|heureux|triste|stressé|relaxé|content|énervé)$",
        r"^(et\s+toi|et\s+vous|moi\s+aussi|pareil|à\s+merveille)$",
        r"^\w+\s+bien\b",  # "très bien", "plutôt bien", etc.
        r"^(bien|super|ok|okay|oui|génial|parfait).*merci$",  # "bien merci", "super merci", etc.
        r"^merci.*$"  # N'importe quoi qui commence par merci
    ]
    
    for pattern in patterns_reponse_bien_etre:
        if re.search(pattern, question_lower):
            logger.info(f"Réponse à une question de bien-être détectée: {question}")
            return "reponse_bien_etre", 1.0, entites
            
    # ==== Cas spécial pour les remerciements ====
    patterns_remerciement = [
        r"\b(merci|thanks|thx|remercie|je\s+te\s+remercie|je\s+vous\s+remercie)\b",
        r"\b(je\s+t'en\s+remercie|c'est\s+gentil|sympa|cool|trop\s+bien)\b"
    ]
    
    for pattern in patterns_remerciement:
        if re.search(pattern, question_lower):
            logger.info(f"Remerciement détecté: {question}")
            return "remerciement", 1.0, entites
    
    # ==== Cas spécial pour les questions sur le créateur ====
    patterns_createur = [
        r"\bqui\s+(t'a\s+cr[ée]{1,3}|vous\s+a\s+cr[ée]{1,3})\b",
        r"\bton\s+cr[ée]ateur\b",
        r"\bcr[ée]{1,3}\s+par\s+qui\b",
        r"\bqui\s+t'a\s+(con[çc]u|programm[ée])\b",
        r"\bton\s+(auteur|inventeur|d[ée]veloppeur)\b"
    ]
    
    for pattern in patterns_createur:
        if re.search(pattern, question_lower):
            logger.info(f"Question sur le créateur détectée: {question}")
            return "createur", 1.0, entites
    
    # ==== Cas spécial pour les questions sur les capacités ====
    patterns_capacites = [
        r"\b(que|quoi|qu'est[- ]ce que)\s+(tu\s+sais\s+faire|vous\s+savez\s+faire)\b",
        r"\b(quelles?\s+sont|c'est\s+quoi)\s+(tes|vos)\s+capacit[ée]s\b",
        r"\b(quelles?\s+sont|c'est\s+quoi)\s+(tes|vos)\s+(fonctions|fonctionnalit[ée]s)\b",
        r"\bque\s+peux[- ]tu\s+faire\b",
        r"\btu\s+peux\s+faire\s+quoi\b",
        r"\btu\s+(sais|sers\s+[aà])\s+quoi\b",
        r"\bqu'est[- ]ce\s+que\s+tu\s+peux\s+faire\b",
        r"\bcapacit[ée]s?\b",
        r"\bfonctionne?s?\b"
    ]
    
    for pattern in patterns_capacites:
        if re.search(pattern, question_lower):
            logger.info(f"Question sur les capacités détectée: {question}")
            return "capacites", 1.0, entites
    
    # ==== Cas spécial pour les questions sur le fonctionnement ====
    patterns_fonctionnement = [
        r"\bcomment\s+(fonctionnes[- ]tu|tu\s+fonctionnes|ça\s+marche|fonctionne|ça\s+fonctionne)\b",
        r"\bexplique\s+(ton|votre)\s+fonctionnement\b",
        r"\bcomment\s+(es[- ]tu|êtes[- ]vous)\s+(fait|programmé)\b",
        r"\bton\s+fonctionnement\b",
        r"\bc'est\s+quoi\s+ton\s+système\b"
    ]
    
    for pattern in patterns_fonctionnement:
        if re.search(pattern, question_lower):
            logger.info(f"Question sur le fonctionnement détectée: {question}")
            return "fonctionnement", 1.0, entites
    
    # ==== Cas spécial pour les demandes de blagues ====
    patterns_blague = [
        r"\b(raconte|dis|raconte[- ]moi|dis[- ]moi)[\s-]+(une|ta|une\s+autre|ta\s+meilleure|une\s+bonne|une\s+petite)\s+blague\b",
        r"\b(raconte|dis)[- ]moi\s+quelque\s+chose\s+de\s+dr[ôo]le\b",
        r"\bfais[- ]moi\s+rire\b",
        r"\btu\s+(as|connais)\s+une\s+blague\b",
        r"\btu\s+peux\s+me\s+faire\s+rire\b",
        r"\bblague\b",
        r"\bfais[- ]moi\s+une\s+blague\b",
        r"\bune\s+blague\s'il\s+(te|vous)\s+pla[iî]t\b"
    ]
    
    for pattern in patterns_blague:
        if re.search(pattern, question_lower):
            logger.info(f"Demande de blague détectée: {question}")
            return "blague", 1.0, entites
    
    # ==== Cas spécial pour les salutations ====
    patterns_salutation = [
        r"^(bonjour|salut|coucou|hello|hey|hi|bonsoir)(\s|$)",
        r"^(bon(jour|soir)|salut|coucou|hello|hey|hi)(\s|$)"
    ]
    
    for pattern in patterns_salutation:
        if re.search(pattern, question_lower):
            logger.info(f"Salutation détectée: {question}")
            return "salutation", 0.8, entites
    
    # ==== Cas spécial pour les questions sur Digital Factory ====
    patterns_digital_factory = [
        r"\bc\'?est\s+quoi\s+digital\s+factory\b",
        r"\bqu[\'e]est[- ]ce\s+que\s+digital\s+factory\b",
        r"\bdigital\s+factory\s+c\'?est\s+quoi\b",
        r"\bparle[- ]moi\s+de\s+digital\s+factory\b",
        r"\bexplique[- ]moi\s+digital\s+factory\b",
        r"\bdigital\s+factory\b"  # Juste la mention de "Digital Factory"
    ]
    
    for pattern in patterns_digital_factory:
        if re.search(pattern, question_lower):
            logger.info(f"Question sur Digital Factory détectée: {question}")
            return "digital_factory", 1.0, entites
    
    # Si aucune intention spécifique n'est détectée
    logger.info(f"Aucune intention spécifique détectée pour: {question}")
    return "inconnu", 0.3, entites

def generer_reponse_simple(intention, entites=None):
    """
    Génère une réponse simple basée sur l'intention détectée.
    
    Args:
        intention (str): L'intention détectée
        entites (dict): Les entités extraites de la question
        
    Returns:
        str: La réponse générée
    """
    if entites is None:
        entites = {}
    
    # Essayer d'obtenir les réponses depuis le module centralisé
    reponses = {}
    if has_reponses_module:
        try:
            reponses = reponses_module.obtenir_reponses("Cindy")
            logger.info(f"Réponses obtenues depuis le module centralisé: {len(reponses)} catégories")
        except Exception as e:
            logger.error(f"Erreur lors de l'obtention des réponses centralisées: {str(e)}")
    
    # Si l'intention est "heure", générer l'heure actuelle
    if intention == "heure":
        maintenant = datetime.now()
        heure_actuelle = maintenant.strftime("%H:%M:%S")
        
        # Format de date en français
        jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", 
               "août", "septembre", "octobre", "novembre", "décembre"]
        
        jour_semaine = jours[maintenant.weekday()]
        jour_mois = maintenant.day
        mois_nom = mois[maintenant.month - 1]
        annee = maintenant.year
        
        reponse = f"Il est actuellement {heure_actuelle} ,nous sommes le {jour_semaine} {jour_mois} {mois_nom} {annee}."
        
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
            
        return reponse
        
    # Si l'intention est "date", générer la date actuelle
    elif intention == "date":
        maintenant = datetime.now()
        
        # Format de date en français
        jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", 
               "août", "septembre", "octobre", "novembre", "décembre"]
        
        jour_semaine = jours[maintenant.weekday()]
        jour_mois = maintenant.day
        mois_nom = mois[maintenant.month - 1]
        annee = maintenant.year
        
        reponse = f"Nous sommes le {jour_semaine} {jour_mois} {mois_nom} {annee}."
        
        # Ajouter une mention pour les jours spéciaux
        if jour_mois == 1 and mois_nom == "janvier":
            reponse += " Bonne année !"
        elif jour_mois == 25 and mois_nom == "décembre":
            reponse += " Joyeux Noël !"
        elif jour_mois == 14 and mois_nom == "juillet":
            reponse += " C'est la fête nationale française !"
        elif jour_semaine == "samedi" or jour_semaine == "dimanche":
            reponse += " Bon week-end !"
            
        return reponse
    
    # Si l'intention est "blague", renvoyer une blague aléatoire
    elif intention == "blague":
        if has_reponses_module and "blague" in reponses:
            blagues = reponses["blague"]
            if blagues:
                return random.choice(blagues)
        
        # Blagues de secours au cas où les blagues centralisées ne sont pas disponibles
        blagues_secours = [
            "Pourquoi les plongeurs plongent-ils toujours en arrière ? Parce que sinon, ils tombent dans le bateau !",
            "Que se passe-t-il quand deux poissons s'énervent ? Le thon monte !",
            "Qu'est-ce qu'un crocodile qui surveille la pharmacie ? Un Lacoste Garde.",
            "Qu'est-ce qui est petit, carré et jaune ? Un petit carré jaune.",
            "Pourquoi les informaticiens confondent-ils Halloween et Noël ? Parce qu'Oct 31 = Dec 25.",
            "Que dit un informaticien quand il s'ennuie ? Je bit ma vie !"
        ]
        return random.choice(blagues_secours)
    
    # Chercher l'intention dans le dictionnaire des réponses
    if intention in reponses:
        reponses_possibles = reponses[intention]
        
        # Si la liste est vide, utiliser une réponse par défaut
        if not reponses_possibles:
            if intention == "bien_etre":
                # Réponses de secours pour le bien-être
                reponses_bien_etre = [
                    "Je vais super bien aujourd'hui, merci de demander ! Et toi, comment ça va ?",
                    "Tout va bien, merci ! C'est gentil de t'inquiéter pour moi. Et de ton côté ?",
                    "Je me sens en pleine forme ! J'espère que ta journée se passe bien aussi ?",
                    "Ça va très bien, merci ! Et toi, comment se passe ta journée ?",
                    "Plutôt bien ! C'est toujours un plaisir de discuter avec toi. Comment vas-tu ?",
                    "Je me porte à merveille, merci ! J'espère que toi aussi ?"
                ]
                logger.warning(f"Utilisation de la réponse de secours pour l'intention: {intention}")
                return random.choice(reponses_bien_etre)
            elif intention == "reponse_bien_etre":
                # Réponses de secours pour les réponses aux questions de bien-être
                reponses_reponse_bien_etre = [
                    "Je suis contente de l'apprendre ! Comment puis-je t'aider aujourd'hui ?",
                    "C'est super ! Que puis-je faire pour toi ?",
                    "Excellent ! Je suis là si tu as besoin de quoi que ce soit.",
                    "Tant mieux ! Y a-t-il quelque chose dont tu voudrais discuter ?",
                    "Merci de partager ça avec moi ! En quoi puis-je t'être utile ?",
                    "C'est bien de le savoir ! N'hésite pas à me demander de l'aide si tu en as besoin.",
                    "Parfait ! Que veux-tu savoir ou faire maintenant ?"
                ]
                logger.warning(f"Utilisation de la réponse de secours pour l'intention: {intention}")
                return random.choice(reponses_reponse_bien_etre)
            else:
                return "Je ne suis pas sûre de comprendre votre question."
            
        # Choisir une réponse aléatoire
        reponse = random.choice(reponses_possibles)
        
        # Personnaliser la réponse avec les entités si nécessaire
        for entite, valeur in entites.items():
            reponse = reponse.replace(f"[{entite.upper()}]", str(valeur))
            
        return reponse
    else:
        # Pour les intentions inconnues, générer une réponse d'excuse
        if has_reponses_module and "inconnu" in reponses:
            reponses_inconnues = reponses["inconnu"]
            if reponses_inconnues:
                reponse = random.choice(reponses_inconnues)
                # Ne pas ajouter de suggestion de météo automatiquement
                return reponse
        
        # Réponse de secours si les réponses centralisées ne sont pas disponibles
        return "Je ne suis pas sûre de comprendre. Pouvez-vous reformuler votre question ?"

def obtenir_suggestions_dynamiques(intention):
    """
    Génère des suggestions de questions à poser à l'agent en fonction de l'intention détectée.
    
    Args:
        intention (str): L'intention détectée
        
    Returns:
        list: Liste de suggestions
    """
    # Essayer d'obtenir les suggestions depuis le module centralisé
    if has_reponses_module:
        try:
            suggestions = reponses_module.obtenir_suggestions(intention)
            if suggestions:
                # Limiter à 4 suggestions maximum
                return suggestions[:4]
        except Exception as e:
            logger.error(f"Erreur lors de l'obtention des suggestions centralisées: {str(e)}")
    
    # Suggestions par défaut en cas d'échec
    suggestions_par_defaut = [
        "Quelle heure est-il ?",
        "Quelle est la météo à Paris ?",
        "Comment vas-tu ?",
        "Qui t'a créé ?"
    ]
    
    return suggestions_par_defaut

def analyser_et_repondre(question):
    """
    Analyse une question et génère une réponse complète.
    
    Args:
        question (str): La question posée par l'utilisateur
        
    Returns:
        dict: Dictionnaire contenant la réponse, l'intention, le score et les suggestions
    """
    try:
        logger.info(f"Analyse de la question: {question}")
        
        # Convertir la question en minuscules pour faciliter la détection
        question_lower = question.lower()
        
        # Déterminer l'intention de la question
        intention, score, entites = determiner_intention(question)
        logger.info(f"Intention détectée: {intention} (score: {score}), entités: {entites}")
        
        # Cas spécial pour la météo
        if intention == "meteo":
            try:
                # Obtenir la ville (ou utiliser Paris par défaut)
                ville = entites.get("ville", "Paris")
                logger.info(f"Demande météo pour la ville: {ville}")

                # Tentative simple d'obtention des données météo
                try:
                    # Déterminer si la question concerne un type spécifique de météo
                    concerne_pluie = any(mot in question_lower for mot in ["pleut", "pluie", "pleuvoir"])
                    concerne_neige = any(mot in question_lower for mot in ["neige", "neiger"])
                    concerne_beau_temps = any(mot in question_lower for mot in ["soleil", "ensoleillé", "soleil", "ciel bleu", "beau"])
                    
                    # Appel direct à la fonction obtenir_meteo - méthode simple et robuste
                    reponse = meteo_service.obtenir_meteo(f"météo à {ville}")
                    
                    # Pour les questions spécifiques, ajouter une précision
                    if isinstance(reponse, str):
                        if concerne_pluie and "il fait actuellement" in reponse:
                            if "pluie" in reponse.lower() or "averse" in reponse.lower():
                                reponse = reponse.replace("il fait actuellement", f"oui, il pleut actuellement. Il fait")
                            else:
                                reponse = reponse.replace("il fait actuellement", f"non, il ne pleut pas actuellement. Il fait")
                                
                        elif concerne_neige and "il fait actuellement" in reponse:
                            if "neige" in reponse.lower():
                                reponse = reponse.replace("il fait actuellement", f"oui, il neige actuellement. Il fait")
                            else:
                                reponse = reponse.replace("il fait actuellement", f"non, il ne neige pas actuellement. Il fait")
                                
                        elif concerne_beau_temps and "il fait actuellement" in reponse:
                            if any(mot in reponse.lower() for mot in ["ensoleillé", "clair", "dégagé", "soleil", "ciel bleu", "beau"]):
                                reponse = reponse.replace("il fait actuellement", f"oui, il fait beau. Il fait actuellement")
                            else:
                                reponse = reponse.replace("il fait actuellement", f"non, il ne fait pas particulièrement beau. Il fait actuellement")
                    
                    # S'assurer que la réponse est une chaîne de caractères
                    if not isinstance(reponse, str):
                        reponse = f"À {ville}, les informations météo ne sont pas disponibles actuellement."
                        logger.error(f"La réponse météo n'est pas au format attendu: {reponse}")
                except Exception as e:
                    logger.error(f"Erreur lors de l'obtention de la météo via obtenir_meteo: {str(e)}")
                    reponse = f"Désolé, je n'ai pas pu obtenir les informations météo pour {ville} en ce moment. Veuillez réessayer plus tard."
            except Exception as e:
                logger.error(f"Erreur générale dans le traitement météo: {str(e)}")
                reponse = "Une erreur est survenue lors du traitement de votre demande météo. Veuillez réessayer plus tard."
        else:
            # Générer une réponse pour les autres intentions
            reponse = generer_reponse_simple(intention, entites)
        
        logger.info(f"Réponse générée: {reponse}")
        
        # Obtenir des suggestions de questions à poser
        suggestions = obtenir_suggestions_dynamiques(intention)
        logger.info(f"Suggestions générées: {suggestions}")
        
        resultat = {
            "reponse": reponse,
            "intention": intention,
            "score": score,
            "entites": entites,
            "suggestions": suggestions
        }
        
        return resultat
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse et de la génération de réponse: {str(e)}", exc_info=True)
        
        # Réponse d'erreur
        return {
            "reponse": "Je suis désolée, une erreur s'est produite lors du traitement de votre question.",
            "intention": "erreur",
            "score": 0.0,
            "entites": {},
            "suggestions": [
                "Quelle heure est-il ?",
                "Qui es-tu ?",
                "Bonjour"
            ]
        }

# Tests unitaires simples si le script est exécuté directement
if __name__ == "__main__":
    # Tests de différentes questions
    questions_test = [
        "Bonjour, comment ça va ?",
        "Quelle est la météo à Paris ?",
        "Quelle heure est-il ?",
        "Qui es-tu ?",
        "Qui t'a créé ?",
        "Comment fonctionnes-tu ?",
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
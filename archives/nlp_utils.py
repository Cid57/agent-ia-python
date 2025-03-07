"""
Module de traitement du langage naturel
Ce module contient des fonctions pour analyser et comprendre le texte en langage naturel.
"""

import re
import string
import random

class AnalyseurTexte:
    """
    Classe pour l'analyse de texte avancée.
    Cette classe fournit des méthodes pour traiter et analyser du texte en français.
    """
    
    def __init__(self):
        """Initialise l'analyseur de texte."""
        # Liste des mots vides (stop words) en français
        self.mots_vides = [
            "le", "la", "les", "un", "une", "des", "du", "de", "à", "au", "aux",
            "ce", "cette", "ces", "mon", "ma", "mes", "ton", "ta", "tes", "son", "sa", "ses",
            "notre", "nos", "votre", "vos", "leur", "leurs", "et", "ou", "mais", "donc",
            "car", "pour", "par", "en", "dans", "sur", "sous", "avec", "sans"
        ]
        
        # Dictionnaire pour l'analyse de sentiments
        self.mots_positifs = [
            "bien", "super", "excellent", "fantastique", "génial", "extraordinaire", 
            "magnifique", "merveilleux", "parfait", "formidable", "agréable", "heureux", 
            "content", "satisfait", "positif", "optimiste", "joyeux", "ravi", "enchanté",
            "aimer", "adorer", "plaire", "apprécier", "plaisir", "joie", "bonheur"
        ]
        
        self.mots_negatifs = [
            "mal", "mauvais", "terrible", "horrible", "affreux", "catastrophique", 
            "détestable", "pénible", "difficile", "triste", "malheureux", "insatisfait", 
            "négatif", "pessimiste", "déçu", "contrarié", "déplaire", "détester", "haïr",
            "souffrir", "douleur", "chagrin", "malaise", "malheur", "peine", "problème"
        ]
        
        # Types de questions pour une meilleure compréhension
        self.types_questions = {
            "information": [
                r"qu['\s]est-ce que", r"qu['\s]est-ce qu['\s]", r"c['\s]est quoi", 
                r"défini[rs]", r"signifi[er]", r"expliqu[er]", r"décri[rs]"
            ],
            "localisation": [
                r"où", r"à quel endroit", r"dans quel lieu", r"quel pays", r"quelle ville"
            ],
            "temporel": [
                r"quand", r"à quelle heure", r"quel jour", r"quelle date", r"depuis quand", 
                r"jusqu'à quand", r"combien de temps"
            ],
            "quantité": [
                r"combien", r"quelle quantité", r"quel nombre", r"quelle somme"
            ],
            "processus": [
                r"comment", r"de quelle manière", r"par quel moyen", r"quelle méthode"
            ],
            "causal": [
                r"pourquoi", r"pour quelle raison", r"à cause de quoi", r"qu['\s]est-ce qui a causé"
            ],
            "hypothétique": [
                r"si", r"que se passerait-il", r"qu['\s]arriverait-il", r"dans le cas où"
            ],
            "comparaison": [
                r"quelle différence", r"qu['\s]est-ce qui distingue", r"en quoi diffère", 
                r"la différence entre", r"comparer", r"similarité"
            ],
            "opinion": [
                r"que penses-tu", r"quel est ton avis", r"crois-tu que", r"penses-tu que",
                r"es-tu d['\s]accord", r"ton opinion"
            ],
            "conseil": [
                r"conseille-moi", r"devrais-je", r"faut-il", r"recommandes-tu", 
                r"suggères-tu", r"que dois-je faire"
            ]
        }
    
    def nettoyer_texte(self, texte):
        """
        Nettoie le texte en retirant la ponctuation et en transformant en minuscules.
        
        Args:
            texte (str): Le texte à nettoyer
            
        Returns:
            str: Le texte nettoyé
        """
        # Convertir en minuscules
        texte = texte.lower()
        
        # Supprimer la ponctuation
        for char in string.punctuation:
            texte = texte.replace(char, ' ')
        
        # Supprimer les caractères spéciaux et les nombres
        texte = re.sub(r'[^a-zA-Zàáâäãåçèéêëìíîïñòóôöõøùúûüÿ\s]', '', texte)
        
        # Supprimer les espaces multiples
        texte = re.sub(r'\s+', ' ', texte).strip()
        
        return texte
    
    def extraire_mots_cles(self, texte):
        """
        Extrait les mots-clés d'un texte en supprimant les mots vides.
        
        Args:
            texte (str): Le texte dont on veut extraire les mots-clés
            
        Returns:
            list: Liste des mots-clés
        """
        # Nettoyer le texte
        texte_nettoye = self.nettoyer_texte(texte)
        
        # Diviser en mots
        mots = texte_nettoye.split()
        
        # Filtrer les mots vides
        mots_cles = [mot for mot in mots if mot not in self.mots_vides]
        
        return mots_cles
    
    def analyser_sentiment(self, texte):
        """
        Analyse le sentiment exprimé dans un texte.
        
        Args:
            texte (str): Le texte à analyser
            
        Returns:
            dict: Dictionnaire contenant le sentiment et son score
        """
        # Nettoyer le texte et extraire les mots
        texte_nettoye = self.nettoyer_texte(texte)
        mots = texte_nettoye.split()
        
        # Compter les mots positifs et négatifs
        nb_mots_positifs = sum(1 for mot in mots if mot in self.mots_positifs)
        nb_mots_negatifs = sum(1 for mot in mots if mot in self.mots_negatifs)
        
        # Calculer le score de sentiment (-1 à 1)
        nb_total = max(1, nb_mots_positifs + nb_mots_negatifs)  # Éviter division par zéro
        score = (nb_mots_positifs - nb_mots_negatifs) / nb_total
        
        # Déterminer le sentiment
        if score > 0.2:
            sentiment = "positif"
        elif score < -0.2:
            sentiment = "négatif"
        else:
            sentiment = "neutre"
        
        return {
            "sentiment": sentiment,
            "score": score,
            "details": {
                "mots_positifs": nb_mots_positifs,
                "mots_negatifs": nb_mots_negatifs
            }
        }
    
    def identifier_type_question(self, texte):
        """
        Identifie le type de question posée.
        
        Args:
            texte (str): La question à analyser
            
        Returns:
            str: Le type de question
        """
        texte_lower = texte.lower()
        
        # Vérifier chaque type de question
        for type_q, patterns in self.types_questions.items():
            for pattern in patterns:
                try:
                    if re.search(pattern, texte_lower):
                        return type_q
                except Exception as e:
                    # Capturer et afficher l'erreur pour le débogage
                    print(f"Erreur d'expression régulière avec le pattern '{pattern}': {e}")
                    # Continuer avec le pattern suivant
                    continue
        
        # Si aucun type spécifique n'est identifié
        return "général"
    
    def calculer_similarite(self, texte1, texte2):
        """
        Calcule une similarité simple entre deux textes.
        
        Args:
            texte1 (str): Premier texte
            texte2 (str): Deuxième texte
            
        Returns:
            float: Score de similarité entre 0 et 1
        """
        # Extraire les mots-clés des deux textes
        mots_cles1 = set(self.extraire_mots_cles(texte1))
        mots_cles2 = set(self.extraire_mots_cles(texte2))
        
        # Si l'un des ensembles est vide, retourner 0
        if not mots_cles1 or not mots_cles2:
            return 0.0
        
        # Calculer l'intersection et l'union des deux ensembles
        intersection = mots_cles1.intersection(mots_cles2)
        union = mots_cles1.union(mots_cles2)
        
        # Calculer le coefficient de Jaccard
        similarite = len(intersection) / len(union)
        
        return similarite
    
    def extraire_entites(self, texte):
        """
        Extrait les entités nommées potentielles d'un texte.
        Version simplifiée sans utiliser de bibliothèque NLP avancée.
        
        Args:
            texte (str): Le texte à analyser
            
        Returns:
            dict: Dictionnaire des entités identifiées
        """
        entites = {
            "dates": [],
            "lieux": [],
            "noms": []
        }
        
        # Recherche simple de dates (format JJ/MM/AAAA ou variations)
        dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b', texte)
        entites["dates"].extend(dates)
        
        # Recherche de mots commençant par une majuscule (potentiellement des noms propres)
        # mais pas en début de phrase
        noms_propres = re.findall(r'(?<=[.!?]\s+|\s+)[A-Z][a-zàáâäãåçèéêëìíîïñòóôöõøùúûüÿ]+', texte)
        entites["noms"].extend(noms_propres)
        
        # Pour les lieux, on pourrait avoir une liste prédéfinie, mais ici on simplifie
        # On cherche les mots après "à", "en", "au", "aux" qui commencent par une majuscule
        lieux = re.findall(r'(?:à|en|au|aux|pour|vers|dans)\s+([A-Z][a-zàáâäãåçèéêëìíîïñòóôöõøùúûüÿ]+)', texte)
        entites["lieux"].extend(lieux)
        
        return entites


# Test simple si le fichier est exécuté directement
if __name__ == "__main__":
    analyseur = AnalyseurTexte()
    
    texte_test = "Bonjour, comment vas-tu aujourd'hui? J'aimerais connaître la météo."
    
    print("Texte original:", texte_test)
    print("Texte nettoyé:", analyseur.nettoyer_texte(texte_test))
    print("Mots-clés:", analyseur.extraire_mots_cles(texte_test))
    
    texte_test2 = "Salut! Est-ce que tu connais les prévisions météo pour aujourd'hui?"
    print("Similarité:", analyseur.calculer_similarite(texte_test, texte_test2)) 
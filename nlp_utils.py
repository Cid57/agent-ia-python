"""
Module de traitement du langage naturel
Ce module contient des fonctions pour analyser et comprendre le texte en langage naturel.
"""

import re
import string

class AnalyseurTexte:
    """
    Classe pour l'analyse de texte simple.
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
    
    def calculer_similarite(self, texte1, texte2):
        """
        Calcule une similarité simple entre deux textes.
        
        Args:
            texte1 (str): Premier texte
            texte2 (str): Deuxième texte
            
        Returns:
            float: Score de similarité entre 0 et 1
        """
        # Si l'un des textes est vide, retourner 0
        if not texte1 or not texte2:
            return 0.0
        
        # Nettoyer les textes
        texte1_nettoye = self.nettoyer_texte(texte1)
        texte2_nettoye = self.nettoyer_texte(texte2)
        
        # Vérifier les textes après nettoyage
        if not texte1_nettoye or not texte2_nettoye:
            return 0.0
        
        # Méthode 1: Vérifier si texte1 est contenu dans texte2
        if texte1_nettoye in texte2_nettoye:
            return 1.0
        
        # Méthode 2: Calculer le ratio de mots partagés
        mots1 = set(texte1_nettoye.split())
        mots2 = set(texte2_nettoye.split())
        
        # Vérifier si texte1 est un seul mot qu'on peut trouver partiellement dans texte2
        if len(mots1) == 1 and len(texte1_nettoye) > 3:
            mot = texte1_nettoye
            for mot2 in mots2:
                # Si le mot est une sous-chaîne d'un mot dans texte2
                if mot in mot2 or mot2 in mot:
                    return 0.8
        
        # Nombre de mots en commun
        intersection = mots1.intersection(mots2)
        
        # Si aucun mot en commun, vérifier les mots partiels
        if not intersection and len(mots1) > 0 and len(mots2) > 0:
            for mot1 in mots1:
                for mot2 in mots2:
                    # Si les mots ont au moins 3 caractères et partagent au moins 70% de leurs lettres
                    if len(mot1) >= 3 and len(mot2) >= 3:
                        if mot1[:3] == mot2[:3]:  # Même préfixe
                            return 0.5
                        # Distance de Levenshtein simplifiée
                        if len(set(mot1).intersection(set(mot2))) / max(len(mot1), len(mot2)) > 0.7:
                            return 0.5
        
        # Calculer la similarité comme le ratio de Jaccard
        union = mots1.union(mots2)
        if not union:
            return 0.0
        
        return len(intersection) / len(union)


# Test simple si le fichier est exécuté directement
if __name__ == "__main__":
    analyseur = AnalyseurTexte()
    
    texte_test = "Bonjour, comment vas-tu aujourd'hui? J'aimerais connaître la météo."
    
    print("Texte original:", texte_test)
    print("Texte nettoyé:", analyseur.nettoyer_texte(texte_test))
    print("Mots-clés:", analyseur.extraire_mots_cles(texte_test))
    
    texte_test2 = "Salut! Est-ce que tu connais les prévisions météo pour aujourd'hui?"
    print("Similarité:", analyseur.calculer_similarite(texte_test, texte_test2)) 
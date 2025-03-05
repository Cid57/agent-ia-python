"""
Module de services externes
Ce module permet d'accéder à des services externes comme la météo.
"""

import requests
import logging
from datetime import datetime
import re

# Configuration du logger
logger = logging.getLogger('assistant_ia.external_services')

class MeteoService:
    """
    Classe pour accéder aux données météo via Open Meteo.
    """
    
    def __init__(self):
        """Initialise le service météo."""
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.default_location = {"latitude": 48.8567, "longitude": 2.3508, "name": "Paris", "country": "France"}
        
        # Nous gardons une liste de villes françaises courantes juste pour des performances
        # mais cette liste ne sera utilisée qu'en dernier recours
        self.villes = {
            "paris": {"latitude": 48.8567, "longitude": 2.3508},
            "marseille": {"latitude": 43.2965, "longitude": 5.3698},
            "lyon": {"latitude": 45.7578, "longitude": 4.8320},
            "toulouse": {"latitude": 43.6043, "longitude": 1.4437},
            "nice": {"latitude": 43.7034, "longitude": 7.2663},
            "nantes": {"latitude": 47.2184, "longitude": -1.5536},
            "strasbourg": {"latitude": 48.5734, "longitude": 7.7521},
            "montpellier": {"latitude": 43.6119, "longitude": 3.8772},
            "bordeaux": {"latitude": 44.8378, "longitude": -0.5792},
            "lille": {"latitude": 50.6292, "longitude": 3.0573}
        }
    
    def extraire_nom_ville(self, texte):
        """
        Extrait le nom de la ville à partir du texte de la question.
        Si aucune ville n'est détectée, retourne None.
        """
        if not texte:
            return None
        
        # Convertir le texte en minuscules pour faciliter la recherche
        texte = texte.lower()
        
        # Liste de villes courantes en France pour détecter les mentions directes
        villes_courantes = [
            "paris", "marseille", "lyon", "toulouse", "nice", "nantes", 
            "strasbourg", "montpellier", "bordeaux", "lille", "rennes", 
            "reims", "toulon", "angers", "grenoble", "dijon", "nancy", "metz"
        ]
        
        # Patterns spécifiques pour les questions de météo
        patterns = [
            # Format: "météo à Paris"
            r'(?:météo|meteo|temps|température|temperature|climat|pluie|pleuvoir|chaud|froid)\s+(?:à|a|au|en|de|pour|sur)\s+([a-zÀ-ÿ\s\-]+)(?:\s|$|\?|\.)',
            
            # Format: "à Paris, la météo"
            r'(?:à|a|au|en|de|pour|sur)\s+([a-zÀ-ÿ\s\-]+)(?:\s|$|\?|\.)(?:météo|meteo|temps|température|temperature|climat)',
            
            # Format: "Paris météo"
            r'([a-zÀ-ÿ\s\-]+)(?:\s|$|\?|\.)(?:météo|meteo|temps|température|temperature|climat)',
            
            # Nouveau format: "pleut-il à Paris" ou "va-t-il pleuvoir à Paris"
            r'(?:pleut-il|pleut t-il|pleut il|va-t-il pleuvoir|va t-il pleuvoir|va t il pleuvoir|va-t-il|va t il)\s+(?:à|a|au|en|de|sur)?\s+([a-zÀ-ÿ\s\-]+)(?:\s|$|\?|\.)',
            
            # Format court: "pluie paris"
            r'(?:pluie|pleuvoir|neige)\s+(?:à|a|au|en|de)?\s+([a-zÀ-ÿ\s\-]+)(?:\s|$|\?|\.)'
        ]
        
        # Tester tous les patterns
        for pattern in patterns:
            matches = re.findall(pattern, texte)
            if matches:
                for match in matches:
                    ville_candidate = match.strip()
                    # Ignorer les mots courants qui ne sont pas des villes
                    mots_exclus = ["demain", "aujourd'hui", "ce soir", "ce matin", "temps", "pluie", "présent", "futur", "il"]
                    if any(mot == ville_candidate for mot in mots_exclus):
                        continue
                    
                    # Si la ville candidate est non vide et n'est pas dans les mots exclus
                    if ville_candidate and not any(mot in ville_candidate for mot in mots_exclus):
                        return ville_candidate.title()  # Première lettre de chaque mot en majuscule
        
        # Vérifier les mentions directes de villes courantes
        for ville in villes_courantes:
            if re.search(r'\b' + re.escape(ville) + r'\b', texte):
                return ville.title()
        
        # Si aucun pattern n'a trouvé de ville, extraire des mots qui pourraient être des villes
        mots = texte.split()
        mots_exclus = ["météo", "meteo", "temps", "température", "temperature", "climat", 
                      "à", "a", "au", "en", "de", "pour", "le", "la", "les", "et", "ou", 
                      "un", "une", "des", "ce", "cette", "ces", "quel", "quelle", "est", 
                      "il", "elle", "ils", "elles", "fait", "fait-il", "demain", "aujourd'hui", 
                      "matin", "soir", "midi", "pluie", "pleut", "pleuvoir", "neige", "neiger"]
        
        for mot in mots:
            if mot not in mots_exclus and len(mot) > 2:
                # Vérifier si le mot ressemble à un nom propre (non filtré)
                return mot.title()
        
        # Si aucune ville n'a été trouvée, retourner Paris par défaut
        logger.info("Aucune ville détectée, utilisation de Paris par défaut")
        return "Paris"
    
    def rechercher_ville_api(self, nom_ville):
        """
        Recherche une ville en utilisant l'API de géocodage.
        
        Args:
            nom_ville (str): Le nom de la ville à rechercher
            
        Returns:
            dict: Informations sur la ville trouvée ou None si aucune correspondance
        """
        try:
            params = {
                "name": nom_ville,
                "count": 5,  # Récupérer plusieurs résultats
                "language": "fr"
            }
            
            response = requests.get(self.geocoding_url, params=params)
            data = response.json()
            
            if "results" in data and data["results"]:
                # Choisir le premier résultat comme le plus pertinent
                ville = data["results"][0]
                return {
                    "nom": ville["name"],
                    "pays": ville.get("country", ""),
                    "latitude": ville["latitude"],
                    "longitude": ville["longitude"]
                }
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de ville via API: {e}")
            return None
            
    def trouver_ville(self, texte):
        """
        Trouve une ville dans le texte et renvoie ses coordonnées.
        
        Args:
            texte (str): Le texte contenant potentiellement un nom de ville
            
        Returns:
            dict: Informations sur la ville trouvée (nom, coordonnées, etc.)
        """
        try:
            # Extraire le nom de la ville du texte
            nom_ville = self.extraire_nom_ville(texte)
            
            # Si aucune ville n'est trouvée, utiliser Paris par défaut
            if not nom_ville:
                nom_ville = "Paris"
                logger.warning(f"Aucune ville extraite de '{texte}', utilisation de Paris par défaut.")
            
            # Rechercher la ville dans l'API ou notre cache
            ville_info = self.rechercher_ville_api(nom_ville)
            
            # Si la ville n'est pas trouvée, utiliser Paris par défaut
            if not ville_info:
                logger.warning(f"Ville '{nom_ville}' non trouvée dans l'API, utilisation de Paris par défaut.")
                nom_ville = "Paris"
                ville_info = self.rechercher_ville_api(nom_ville)
            
            return ville_info
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de ville dans '{texte}': {str(e)}")
            # En cas d'erreur, utiliser Paris par défaut
            return self.rechercher_ville_api("Paris")
    
    def obtenir_meteo(self, texte):
        """
        Obtient les informations météo pour une ville mentionnée dans le texte.
        
        Args:
            texte (str): Texte contenant potentiellement un nom de ville
            
        Returns:
            str: Message formaté contenant les informations météo
        """
        try:
            # Journaliser la requête météo
            logger.info(f"Requête météo reçue: '{texte}'")
            
            # Trouver la ville dans le texte
            ville_info = self.trouver_ville(texte)
            
            if not ville_info:
                logger.error("Aucune ville trouvée pour la requête météo")
                return "Désolé, je n'ai pas pu identifier de ville valide dans votre question."
            
            # Journaliser la ville trouvée
            logger.info(f"Ville trouvée pour la météo: {ville_info['nom']}")
            
            # Récupérer les coordonnées
            lat = ville_info["latitude"]
            lon = ville_info["longitude"]
            
            # Construire l'URL pour l'API Open-Meteo
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,rain,weather_code,wind_speed_10m&timezone=auto"
            
            # Faire la requête HTTP
            response = requests.get(url)
            
            # Vérifier si la requête a réussi
            if response.status_code == 200:
                # Parser les données JSON
                data = response.json()
                
                # Extraire les informations actuelles
                current = data.get("current", {})
                
                # Vérifier si les données sont complètes
                if not current or "temperature_2m" not in current:
                    logger.error(f"Données météo incomplètes pour {ville_info['nom']}")
                    return f"Désolé, les données météo pour {ville_info['nom']} sont temporairement indisponibles."
                
                # Créer un dictionnaire avec les informations formatées
                meteo_info = {
                    "status": "success",
                    "ville": ville_info["nom"],
                    "pays": ville_info.get("pays", ""),
                    "temperature": round(current.get("temperature_2m", 0)),
                    "temperature_ressentie": round(current.get("apparent_temperature", 0)),
                    "humidite": current.get("relative_humidity_2m", 0),
                    "unite_humidite": "%",
                    "vent": round(current.get("wind_speed_10m", 0)),
                    "unite_vent": "km/h",
                    "code": current.get("weather_code", 0),
                    "est_jour": current.get("is_day", 1),
                    "timestamp": datetime.fromtimestamp(current.get("time", 0)).strftime("%d %B %Y, %H:%M"),
                }
                
                # Interpréter le code météo
                meteo_info["description"] = self.interpreter_code_meteo(meteo_info["code"])
                
                # Obtenir l'icône correspondante
                meteo_info["icone"] = self.obtenir_icone_meteo(meteo_info["code"])
                
                # Formater le message
                message = self.formater_message_meteo(meteo_info)
                
                return message
            else:
                logger.error(f"Erreur API météo: {response.status_code} - {response.text}")
                return f"Désolé, je n'ai pas pu obtenir les informations météo pour {ville_info['nom']}. Le service météo est temporairement indisponible."
                
        except Exception as e:
            logger.error(f"Erreur lors de l'obtention de la météo: {str(e)}")
            return "Désolé, une erreur s'est produite lors de la récupération des informations météo. Veuillez réessayer plus tard."
    
    def interpreter_code_meteo(self, code):
        """
        Interprète le code météo de Open Meteo.
        
        Args:
            code (int): Code météo selon la nomenclature WMO
            
        Returns:
            str: Description en français de la météo
        """
        codes_meteo = {
            0: "Ciel dégagé",
            1: "Principalement dégagé",
            2: "Partiellement nuageux",
            3: "Nuageux",
            45: "Brouillard",
            48: "Brouillard givrant",
            51: "Bruine légère",
            53: "Bruine modérée",
            55: "Bruine dense",
            56: "Bruine verglaçante légère",
            57: "Bruine verglaçante dense",
            61: "Pluie légère",
            63: "Pluie modérée",
            65: "Pluie forte",
            66: "Pluie verglaçante légère",
            67: "Pluie verglaçante forte",
            71: "Chute de neige légère",
            73: "Chute de neige modérée",
            75: "Chute de neige forte",
            77: "Grains de neige",
            80: "Averses de pluie légères",
            81: "Averses de pluie modérées",
            82: "Averses de pluie violentes",
            85: "Averses de neige légères",
            86: "Averses de neige fortes",
            95: "Orage",
            96: "Orage avec grêle légère",
            99: "Orage avec grêle forte"
        }
        
        return codes_meteo.get(code, "Météo inconnue")
    
    def obtenir_icone_meteo(self, code):
        """
        Obtient l'icône correspondant au code météo.
        
        Args:
            code (int): Code météo selon la nomenclature WMO
            
        Returns:
            str: Emoji représentant la météo
        """
        icones_meteo = {
            0: "☀️", # Ensoleillé
            1: "🌤️", # Principalement clair
            2: "⛅", # Partiellement nuageux
            3: "☁️", # Très nuageux
            45: "🌫️", # Brouillard
            48: "🌫️❄️", # Brouillard givrant
            51: "🌦️", # Bruine légère
            53: "🌦️", # Bruine modérée
            55: "🌦️", # Bruine forte
            56: "🌧️❄️", # Pluie verglaçante légère
            57: "🌧️❄️", # Pluie verglaçante forte
            61: "🌧️", # Pluie légère
            63: "🌧️", # Pluie modérée
            65: "🌧️", # Pluie forte
            66: "🌧️❄️", # Pluie verglaçante légère
            67: "🌧️❄️", # Pluie verglaçante forte
            71: "❄️", # Neige légère
            73: "❄️", # Neige modérée
            75: "❄️", # Neige forte
            77: "🌨️", # Grésil
            80: "🌦️", # Averses légères
            81: "🌦️", # Averses modérées
            82: "🌧️", # Averses fortes
            85: "🌨️", # Neige faible
            86: "🌨️❄️", # Neige forte
            95: "⛈️", # Orages
            96: "⛈️❄️", # Orages avec grêle légère
            99: "⛈️❄️", # Orages avec grêle forte
        }
        
        return icones_meteo.get(code, "🌍") # Icône par défaut si code inconnu
    
    def formater_message_meteo(self, meteo_info):
        """
        Formate les informations météo en un message texte élégant et moderne.
        
        Args:
            meteo_info (dict): Informations météo
            
        Returns:
            str: Message formaté
        """
        if meteo_info["status"] != "success":
            return meteo_info["message"]
        
        # Date actuelle en français
        aujourdhui = datetime.now().strftime("%A %d %B %Y").capitalize()
        aujourdhui = self.traduire_date(aujourdhui)
        
        # Format moderne et minimaliste, inspiré des applications professionnelles
        message = f"""
📆  {aujourdhui}

📍  {meteo_info['ville']}  {meteo_info['icone']}  {meteo_info['temperature']}°C
    {meteo_info['description']}

🌡️  Ressentie: {meteo_info['temperature_ressentie']}°C
💦  Humidité: {meteo_info['humidite']}{meteo_info['unite_humidite']}
💨  Vent: {meteo_info['vent']} {meteo_info['unite_vent']}

⏳  Mise à jour: {meteo_info['timestamp']}
"""
        return message.strip()
    
    def traduire_date(self, date_en):
        """
        Traduit une date en anglais vers le français.
        
        Args:
            date_en (str): Date en anglais
            
        Returns:
            str: Date en français
        """
        # Traduction des jours
        jours_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        jours_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        
        # Traduction des mois
        mois_en = ['January', 'February', 'March', 'April', 'May', 'June', 
                  'July', 'August', 'September', 'October', 'November', 'December']
        mois_fr = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 
                  'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
        
        # Traduire
        date_fr = date_en
        for i, jour in enumerate(jours_en):
            date_fr = date_fr.replace(jour, jours_fr[i])
        
        for i, mois in enumerate(mois_en):
            date_fr = date_fr.replace(mois, mois_fr[i])
            
        return date_fr 
"""
Module de services externes
Ce module permet d'accéder à des services externes comme la météo.
"""

import requests
import logging
from datetime import datetime

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
        Extrait les noms potentiels de villes d'une question en utilisant des heuristiques.
        
        Args:
            texte (str): Le texte de la question
            
        Returns:
            list: Liste des noms potentiels de villes
        """
        texte = texte.lower()
        villes_potentielles = []
        
        # Patterns courants pour l'extraction de villes
        # "météo à [VILLE]", "temps à [VILLE]", "[VILLE] météo", etc.
        patterns = [
            r"(?:météo|meteo|temps|température|temperature|climat)\s+(?:à|a|au|en|de)\s+([a-zÀ-ÿ\s-]+)",
            r"(?:à|a|au|en|de)\s+([a-zÀ-ÿ\s-]+)\s+(?:météo|meteo|temps|température|temperature|climat)",
            r"([a-zÀ-ÿ\s-]+)\s+(?:météo|meteo|temps|température|temperature|climat)"
        ]
        
        import re
        for pattern in patterns:
            try:
                matches = re.findall(pattern, texte)
                for match in matches:
                    # Nettoyer le nom potentiel de ville
                    ville = match.strip()
                    if ville and len(ville) > 2 and ville not in ["le", "la", "les", "des", "et", "ou"]:
                        villes_potentielles.append(ville)
            except Exception as e:
                print(f"Erreur d'expression régulière avec le pattern '{pattern}': {e}")
                continue
        
        # Si aucun pattern n'a fonctionné, extraire les mots individuels qui pourraient être des villes
        if not villes_potentielles:
            # Exclure les mots communs qui ne sont pas des villes
            mots_a_exclure = ["météo", "meteo", "temps", "température", "temperature", "climat", 
                           "quel", "quelle", "comment", "est", "fait", "aujourd'hui", "demain",
                           "ce", "cette", "le", "la", "les", "des", "et", "ou", "pour", "il", 
                           "elle", "ils", "elles", "nous", "vous", "on", "je", "tu", "à", "a", 
                           "au", "aux", "en", "dans", "sur", "sous", "avec", "sans", "par", "chez"]
            
            mots = texte.split()
            for mot in mots:
                mot = mot.strip()
                if mot and len(mot) > 3 and mot not in mots_a_exclure:
                    villes_potentielles.append(mot)
        
        return villes_potentielles
    
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
                    "coords": {
                        "latitude": ville["latitude"],
                        "longitude": ville["longitude"]
                    }
                }
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de ville via API: {e}")
            return None
            
    def trouver_ville(self, texte):
        """
        Trouve une ville mentionnée dans le texte en utilisant l'API de géocodage.
        
        Args:
            texte (str): Le texte mentionnant potentiellement une ville
            
        Returns:
            dict: Coordonnées et nom de la ville ou emplacement par défaut
        """
        # Extraire les noms potentiels de villes
        villes_potentielles = self.extraire_nom_ville(texte)
        
        # Rechercher chaque ville potentielle via l'API
        for ville in villes_potentielles:
            resultat = self.rechercher_ville_api(ville)
            if resultat:
                logger.info(f"Ville trouvée via API: {resultat['nom']}, {resultat['pays']}")
                return {
                    "nom": f"{resultat['nom']}, {resultat['pays']}",
                    "coords": resultat["coords"]
                }
        
        # Si l'API ne trouve pas de ville ou en cas d'erreur, vérifier dans le dictionnaire local
        texte_lower = texte.lower()
        for ville, coords in self.villes.items():
            if ville in texte_lower:
                logger.info(f"Ville trouvée dans le dictionnaire local: {ville}")
                return {"nom": ville.capitalize(), "coords": coords}
        
        # Si aucune ville n'est trouvée, utiliser Paris par défaut
        logger.info("Aucune ville trouvée, utilisation de Paris par défaut")
        return {"nom": "Paris, France", "coords": self.default_location}
    
    def obtenir_meteo(self, texte):
        """
        Obtient les données météo complètes pour une ville mentionnée dans le texte.
        
        Args:
            texte (str): Le texte contenant potentiellement un nom de ville
            
        Returns:
            dict ou str: Données météo formatées ou message d'erreur
        """
        try:
            # Trouver la ville mentionnée dans le texte
            ville_info = self.trouver_ville(texte)
            ville = ville_info["nom"]
            coords = ville_info["coords"]
            
            # Paramètres de requête pour Open Meteo
            params = {
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "current": ["temperature_2m", "relative_humidity_2m", "weather_code", "wind_speed_10m", "apparent_temperature"],
                "timezone": "auto",
                "forecast_days": 1
            }
            
            # Faire la requête à l'API
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Vérifier si la requête a réussi
            
            data = response.json()
            
            # Extraire les informations pertinentes
            current = data.get("current", {})
            
            if not current:
                logger.error("Données météo non disponibles")
                return {"status": "error", "message": "Données météo non disponibles"}
            
            # Interpréter le code météo
            weather_code = current.get("weather_code", 0)
            weather_description = self.interpreter_code_meteo(weather_code)
            weather_icon = self.obtenir_icone_meteo(weather_code)
            
            # Formater les données météo
            meteo_info = {
                "status": "success",
                "ville": ville,
                "temperature": round(current.get("temperature_2m", 0)),
                "temperature_ressentie": round(current.get("apparent_temperature", 0)),
                "unite_temperature": data.get("current_units", {}).get("temperature_2m", "°C"),
                "humidite": current.get("relative_humidity_2m", 0),
                "unite_humidite": data.get("current_units", {}).get("relative_humidity_2m", "%"),
                "vent": round(current.get("wind_speed_10m", 0)),
                "unite_vent": data.get("current_units", {}).get("wind_speed_10m", "km/h"),
                "description": weather_description,
                "icone": weather_icon,
                "code_meteo": weather_code,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Créer un message formaté en texte
            meteo_message = self.formater_message_meteo(meteo_info)
            
            logger.info(f"Données météo récupérées avec succès pour {ville}")
            return meteo_message
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la requête météo: {e}")
            return f"Désolé, je n'ai pas pu récupérer la météo en raison d'une erreur de connexion. Veuillez réessayer plus tard."
        
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la récupération des données météo: {e}")
            return f"Désolé, une erreur s'est produite lors de la récupération des données météo. Veuillez réessayer."
    
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
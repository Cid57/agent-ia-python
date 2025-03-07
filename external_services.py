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
        
        # Supprimer les mots qui ne sont pas des villes pour éviter les faux positifs
        mots_a_supprimer = ["quelle", "quel", "quelles", "quels", "meteo", "météo", 
                           "temps", "température", "temperature", "climat", "est", "fait",
                           "fait-il", "pleut", "pleuvoir", "va-t-il"]
        
        for mot in mots_a_supprimer:
            texte = texte.replace(f"{mot} ", " ")
        
        # Liste de villes courantes en France pour détecter les mentions directes
        villes_courantes = [
            "paris", "marseille", "lyon", "toulouse", "nice", "nantes", 
            "strasbourg", "montpellier", "bordeaux", "lille", "rennes", 
            "reims", "toulon", "angers", "grenoble", "dijon", "nancy", "metz",
            "tokyo", "londres", "new york", "bali"
        ]
        
        # Vérifier les mentions directes de villes
        for ville in villes_courantes:
            if re.search(r'\b' + re.escape(ville) + r'\b', texte):
                return ville.title()
        
        # Patterns spécifiques pour les questions de météo
        patterns = [
            # Format: "météo à Paris"
            r'(?:à|a|au|en|de|pour|sur)\s+([a-zÀ-ÿ\s\-]+)(?:\s|$|\?|\.)',
            
            # Format simple pour capturer un mot qui pourrait être une ville
            r'\b([a-zÀ-ÿ\-]{3,})\b'
        ]
        
        # Tester tous les patterns
        for pattern in patterns:
            matches = re.findall(pattern, texte)
            if matches:
                for match in matches:
                    ville_candidate = match.strip()
                    # Ignorer les mots courants qui ne sont pas des villes
                    mots_exclus = ["demain", "aujourd'hui", "ce soir", "ce matin", 
                                  "temps", "pluie", "présent", "futur", "il",
                                  "quelle", "quel", "est", "fait", "pleut", "pleuvoir"]
                    
                    if any(mot == ville_candidate for mot in mots_exclus):
                        continue
                    
                    # Si la ville candidate est non vide et n'est pas dans les mots exclus
                    if ville_candidate and not any(mot in ville_candidate for mot in mots_exclus):
                        # Vérifier que ce n'est pas un mot commun (minimum 3 lettres)
                        if len(ville_candidate) >= 3:
                            return ville_candidate.title()
        
        # Si aucune ville n'a été trouvée
        return None
    
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
            # Liste des villes courantes avec leurs coordonnées
            villes_courantes = {
                "paris": {"nom": "Paris", "pays": "France", "latitude": 48.8566, "longitude": 2.3522},
                "marseille": {"nom": "Marseille", "pays": "France", "latitude": 43.2965, "longitude": 5.3698},
                "lyon": {"nom": "Lyon", "pays": "France", "latitude": 45.7578, "longitude": 4.8320},
                "toulouse": {"nom": "Toulouse", "pays": "France", "latitude": 43.6047, "longitude": 1.4442},
                "nice": {"nom": "Nice", "pays": "France", "latitude": 43.7102, "longitude": 7.2620},
                "nantes": {"nom": "Nantes", "pays": "France", "latitude": 47.2184, "longitude": -1.5536},
                "strasbourg": {"nom": "Strasbourg", "pays": "France", "latitude": 48.5734, "longitude": 7.7521},
                "montpellier": {"nom": "Montpellier", "pays": "France", "latitude": 43.6119, "longitude": 3.8772},
                "bordeaux": {"nom": "Bordeaux", "pays": "France", "latitude": 44.8378, "longitude": -0.5792},
                "lille": {"nom": "Lille", "pays": "France", "latitude": 50.6292, "longitude": 3.0573},
                "rennes": {"nom": "Rennes", "pays": "France", "latitude": 48.1173, "longitude": -1.6778},
                "reims": {"nom": "Reims", "pays": "France", "latitude": 49.2583, "longitude": 4.0317},
                "nancy": {"nom": "Nancy", "pays": "France", "latitude": 48.6921, "longitude": 6.1844},
                "metz": {"nom": "Metz", "pays": "France", "latitude": 49.1193, "longitude": 6.1755},
                "tokyo": {"nom": "Tokyo", "pays": "Japon", "latitude": 35.6762, "longitude": 139.6503},
                "londres": {"nom": "Londres", "pays": "Royaume-Uni", "latitude": 51.5074, "longitude": -0.1278},
                "new york": {"nom": "New York", "pays": "États-Unis", "latitude": 40.7128, "longitude": -74.0060},
                "bali": {"nom": "Bali", "pays": "Indonésie", "latitude": -8.3405, "longitude": 115.0920}
            }
            
            # Extraire le nom de la ville du texte
            nom_ville = self.extraire_nom_ville(texte)
            
            # Si aucune ville n'est trouvée ou si l'extraction échoue, utiliser Paris par défaut
            if not nom_ville:
                nom_ville = "Paris"
            
            # Vérifier si la ville est dans notre cache
            nom_ville_lower = nom_ville.lower()
            if nom_ville_lower in villes_courantes:
                return villes_courantes[nom_ville_lower]
            
            # Si ce n'est pas dans notre cache, essayer via l'API
            ville_info = self.rechercher_ville_api(nom_ville)
            
            # Si la ville n'est pas trouvée via API, utiliser Paris par défaut
            if not ville_info:
                return villes_courantes["paris"]
            
            return ville_info
            
        except Exception as e:
            # En cas d'erreur, retourner Paris comme solution de secours
            return {
                "nom": "Paris",
                "pays": "France",
                "latitude": 48.8566,
                "longitude": 2.3522
            }
    
    def obtenir_meteo(self, texte):
        """
        Obtient les informations météo pour une ville mentionnée dans le texte.
        
        Args:
            texte (str): Texte contenant potentiellement un nom de ville
            
        Returns:
            str: Message formaté contenant les informations météo
        """
        try:
            # Trouver la ville dans le texte
            ville_info = self.trouver_ville(texte)
            
            # Récupérer les coordonnées
            lat = ville_info["latitude"]
            lon = ville_info["longitude"]
            
            # Construire l'URL pour l'API Open-Meteo (version simple et fiable)
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&timezone=auto"
            
            # Faire la requête HTTP
            response = requests.get(url)
            
            # Vérifier si la requête a réussi
            if response.status_code == 200:
                # Parser les données JSON
                data = response.json()
                
                # Extraire les informations actuelles
                current = data.get("current", {})
                
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
                    "est_jour": 1,  # Supposer qu'il fait jour par défaut
                    "timestamp": datetime.now().strftime("%d %B %Y, %H:%M"),
                }
                
                # Interpréter le code météo
                meteo_info["description"] = self.interpreter_code_meteo(meteo_info["code"])
                
                # Obtenir l'icône correspondante
                meteo_info["icone"] = self.obtenir_icone_meteo(meteo_info["code"])
                
                # Formater le message
                message = self.formater_message_meteo(meteo_info)
                
                return message
            else:
                # En cas d'erreur HTTP, créer un message d'erreur
                return f"Désolé, une erreur s'est produite lors de la récupération des informations météo. Veuillez réessayer plus tard."
                
        except Exception as e:
            # En cas d'exception, retourner un message d'erreur générique
            return "Désolé, une erreur s'est produite lors de la récupération des informations météo. Veuillez réessayer plus tard."
    
    def obtenir_meteo_ville(self, ville):
        """
        Obtient les informations météo pour une ville spécifiée.
        Retourne un dictionnaire avec les informations météo formatées de manière attrayante.
        
        Args:
            ville (str): Nom de la ville dont on veut la météo
            
        Returns:
            dict: Dictionnaire avec informations météo complètes
        """
        try:
            logger.info(f"Obtention de la météo pour la ville: {ville}")
            
            # Trouver les coordonnées de la ville
            ville_info = None
            
            # Vérifier si la ville est dans notre cache
            ville_lower = ville.lower()
            villes_courantes = {
                "paris": {"nom": "Paris", "pays": "France", "latitude": 48.8566, "longitude": 2.3522},
                "marseille": {"nom": "Marseille", "pays": "France", "latitude": 43.2965, "longitude": 5.3698},
                "lyon": {"nom": "Lyon", "pays": "France", "latitude": 45.7578, "longitude": 4.8320},
                "toulouse": {"nom": "Toulouse", "pays": "France", "latitude": 43.6047, "longitude": 1.4442},
                "nice": {"nom": "Nice", "pays": "France", "latitude": 43.7102, "longitude": 7.2620},
                "nantes": {"nom": "Nantes", "pays": "France", "latitude": 47.2184, "longitude": -1.5536},
                "strasbourg": {"nom": "Strasbourg", "pays": "France", "latitude": 48.5734, "longitude": 7.7521},
                "montpellier": {"nom": "Montpellier", "pays": "France", "latitude": 43.6119, "longitude": 3.8772},
                "bordeaux": {"nom": "Bordeaux", "pays": "France", "latitude": 44.8378, "longitude": -0.5792},
                "lille": {"nom": "Lille", "pays": "France", "latitude": 50.6292, "longitude": 3.0573}
            }
            
            if ville_lower in villes_courantes:
                ville_info = villes_courantes[ville_lower]
            else:
                # Essayer via l'API de géocodage
                ville_info = self.rechercher_ville_api(ville)
                
                # Si toujours pas trouvé, utiliser Paris par défaut
                if not ville_info:
                    logger.warning(f"Ville non trouvée, utilisation de Paris par défaut")
                    ville_info = villes_courantes["paris"]
            
            # Récupérer les coordonnées
            lat = ville_info["latitude"]
            lon = ville_info["longitude"]
            
            # Construire l'URL pour l'API Open-Meteo avec toutes les informations
            # Version sécurisée qui fonctionne avec l'API actuelle
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,relative_humidity_2m,apparent_temperature,wind_speed_10m&timezone=auto"
            
            # Faire la requête HTTP
            response = requests.get(url)
            logger.info(f"Statut de la réponse API météo: {response.status_code}")
            
            # Vérifier si la requête a réussi
            if response.status_code == 200:
                # Parser les données JSON
                data = response.json()
                logger.info(f"Données API météo reçues: {data.keys()}")
                
                # Extraire les informations actuelles
                current = data.get("current", {})
                
                if current:
                    # Créer un dictionnaire avec les informations formatées
                    meteo_info = {
                        "status": "success",
                        "ville": ville_info.get("nom", ville),
                        "pays": ville_info.get("pays", ""),
                        "temperature": round(current.get("temperature_2m", 0)),
                        "temperature_ressentie": round(current.get("apparent_temperature", 0)) if "apparent_temperature" in current else None,
                        "humidite": current.get("relative_humidity_2m", 0) if "relative_humidity_2m" in current else None,
                        "unite_humidite": "%",
                        "vent": round(current.get("wind_speed_10m", 0)) if "wind_speed_10m" in current else None,
                        "unite_vent": "km/h",
                        "code": current.get("weather_code", 0),
                        "est_jour": 1,  # Supposer qu'il fait jour par défaut
                        "timestamp": datetime.now().strftime("%d %B %Y, %H:%M")
                    }
                    
                    # Interpréter le code météo
                    meteo_info["description"] = self.interpreter_code_meteo(meteo_info["code"])
                    meteo_info["condition"] = meteo_info["description"]  # Pour compatibilité
                    
                    # Obtenir l'icône correspondante
                    meteo_info["icone"] = self.obtenir_icone_meteo(meteo_info["code"])
                    
                    return meteo_info
                else:
                    logger.error(f"Données current non trouvées dans: {data}")
                    return {
                        "status": "error",
                        "ville": ville,
                        "temperature": 0,
                        "condition": "Données météo indisponibles"
                    }
            else:
                logger.error(f"Erreur HTTP lors de la requête météo: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "ville": ville,
                    "temperature": 0,
                    "condition": "Service météo temporairement indisponible"
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de l'obtention de la météo pour {ville}: {str(e)}")
            return {
                "status": "error",
                "ville": ville,
                "temperature": 0,
                "condition": "Erreur du service météo"
            }
    
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
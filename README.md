# Assistant IA Cindy en Python

Ce projet est un assistant virtuel intelligent créé en Python, avec une interface web pour interagir facilement avec l'agent. Il combine des techniques de traitement du langage naturel (NLP) avec un système d'apprentissage évolutif.

## Ce que fait cet assistant

- **Comprend vos questions** grâce à un moteur NLP amélioré
- **Affiche la météo en temps réel** via l'API Open Meteo
- **Mémorise et apprend** de chaque conversation pour s'améliorer
- **Propose des suggestions contextuelles** basées sur vos questions
- **Détecte les intentions** dans vos messages (météo, heure, aide, etc.)
- **S'améliore avec le temps** grâce au module d'apprentissage

## Les fichiers principaux

1. **app.py** : Le cœur de l'application web (utilise Flask)

   - Gère les pages web et les requêtes HTTP
   - Connecte l'interface utilisateur au moteur NLP
   - Intègre les services externes comme la météo

2. **nlp_engine.py** : Moteur de traitement du langage naturel

   - Analyse les questions des utilisateurs
   - Détecte les intentions et le contexte
   - Extrait les entités importantes (villes, dates, etc.)
   - Génère des réponses adaptées

3. **apprentissage.py** : Système d'apprentissage continu

   - Enregistre les interactions utilisateur
   - Analyse les tendances et préférences
   - Améliore le modèle de compréhension
   - Génère des statistiques d'utilisation

4. **external_services.py** : Services externes
   - Récupère la météo depuis l'API Open Meteo
   - Gère la géolocalisation des villes
   - Interprète les codes météo

## Nouveautés et améliorations

- **Système d'analyse d'intentions** : détection précise de ce que veut l'utilisateur
- **Extraction d'entités** : reconnaissance des villes, dates et autres éléments importants
- **Suggestions dynamiques** : propositions de questions pertinentes selon le contexte
- **Apprentissage continu** : amélioration des performances avec chaque conversation
- **Interface réactive** : expérience utilisateur fluide et moderne

## Comment faire fonctionner ce projet

### Prérequis

- Python 3.6 ou plus récent
- Connexion internet (pour la météo)

### Installation

1. Téléchargez tous les fichiers du projet
2. Ouvrez un terminal (invite de commande)
3. Allez dans le dossier du projet
4. Installez les dépendances :

```bash
pip install -r requirements.txt
```

### Démarrage

Pour lancer l'assistant, exécutez la commande :

```bash
python app.py
```

Puis ouvrez votre navigateur à l'adresse : http://127.0.0.1:5000

## Fonctionnalités à tester

1. **Questions météo** : "Quel temps fait-il à Paris ?" ou "Météo à Tokyo"
2. **Questions temporelles** : "Quelle heure est-il ?" ou "Quel jour sommes-nous ?"
3. **Salutations** : "Bonjour Cindy" ou "Comment vas-tu ?"
4. **Demandes d'aide** : "Que peux-tu faire ?" ou "Aide-moi"
5. **Suggestions** : Cliquez sur les suggestions qui apparaissent après chaque réponse

## Personnalisation

Vous pouvez facilement améliorer l'agent en :

1. **Ajoutant des intentions** dans le fichier `nlp_engine.py`
2. **Modifiant l'apparence** dans les fichiers CSS du dossier `static/css`
3. **Ajoutant des services externes** dans le fichier `external_services.py`

## Guide de présentation pour votre projet

1. **Introduction** : "Voici Cindy, un assistant IA avec apprentissage automatique"
2. **Démonstration d'une conversation** : posez plusieurs types de questions
3. **Météo avec reconnaissance de ville** : montrez la détection des villes
4. **Fonctionnalité d'apprentissage** : expliquez comment l'agent s'améliore avec le temps
5. **Structure technique** : présentez l'architecture du système
6. **Conclusion** : discutez des améliorations futures et possibilités

## Aide en cas de problème

- **L'application ne démarre pas** : Vérifiez que Python est bien installé
- **Erreur de module** : Vérifiez que vous avez bien installé les dépendances
- **API météo non fonctionnelle** : Vérifiez votre connexion internet
- **Problème d'affichage** : Essayez de vider le cache de votre navigateur

---

Projet créé pour explorer le traitement du langage naturel et l'apprentissage automatique en Python.

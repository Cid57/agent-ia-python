# Assistant IA en Python pour Débutants

Ce projet est un agent IA simple créé en Python, destiné aux personnes qui débutent en programmation et qui souhaitent comprendre les bases du développement d'un assistant virtuel avec interface web.

![Capture d'écran de l'interface](static/images/screenshot.png)

## Fonctionnalités

- **Interface web responsive et intuitive** avec animations et indicateurs de chargement
- **Traitement intelligent des questions** avec analyse de mots-clés et calcul de similarité
- **Réponses variées et aléatoires** pour une expérience plus naturelle
- **Mémorisation des conversations** (court terme et long terme)
- **Historique des échanges consultable** avec possibilité de l'effacer
- **Structure modulaire** facilitant les améliorations futures
- **Page d'aide** expliquant les fonctionnalités disponibles
- **Session utilisateur** pour une expérience personnalisée

## Structure du Projet

Le projet utilise une architecture modulaire avec plusieurs fichiers Python et ressources web:

- `app.py` : Application web Flask qui gère l'interface utilisateur et les routes HTTP
- `agent.py` : Logique principale de l'agent IA (analyse des questions, génération de réponses)
- `nlp_utils.py` : Outils de traitement du langage naturel pour l'analyse de texte
- `memory.py` : Système de mémoire contextuelle pour stocker les conversations
- `templates/` : Fichiers HTML pour l'interface web (index, historique, aide)
- `static/` : Ressources pour l'interface (CSS, JavaScript, images)
- `requirements.txt` : Liste des dépendances Python nécessaires

## Installation

1. Assurez-vous d'avoir Python 3.6 ou supérieur installé
2. Clonez ce dépôt ou téléchargez les fichiers
3. Installez les dépendances nécessaires:

```bash
pip install -r requirements.txt
```

## Utilisation

Pour lancer l'application:

```bash
py app.py
```

Puis ouvrez votre navigateur à l'adresse: http://127.0.0.1:5000

Vous pouvez également y accéder depuis d'autres appareils de votre réseau local en utilisant l'adresse IP de votre ordinateur: http://[votre-ip]:5000

## Guide pour les Débutants

### Comprendre les Composants

1. **Agent (`agent.py`)**: C'est le cœur de notre assistant. Il contient la logique pour comprendre les questions et générer des réponses. L'agent utilise un système de catégorisation basé sur des mots-clés pour identifier le sujet de chaque question et sélectionner une réponse appropriée.

2. **Traitement du Langage (`nlp_utils.py`)**: Ce module analyse le texte que vous tapez pour en extraire le sens. Il nettoie le texte (suppression de la ponctuation, conversion en minuscules), filtre les mots vides (articles, prépositions, etc.) et calcule des scores de similarité entre textes.

3. **Mémoire (`memory.py`)**: Permet à l'agent de se souvenir des conversations passées. La mémoire est divisée en deux parties :

   - Mémoire à court terme : stocke la conversation en cours
   - Mémoire à long terme : stocke des informations persistantes entre les sessions

4. **Interface Web (`app.py` + templates)**: Crée une interface conviviale pour interagir avec l'agent. L'application utilise Flask pour gérer les requêtes HTTP et JavaScript pour créer une expérience dynamique et réactive.

### Les Fonctionnalités Avancées

- **Sessions utilisateur** : L'application reconnaît les visiteurs récurrents pour éviter de répéter le message d'accueil
- **Indicateur de frappe** : Une animation pendant le traitement des réponses pour une expérience plus naturelle
- **Effacement de l'historique** : Possibilité d'effacer la conversation actuelle
- **Réponses variées** : L'agent choisit aléatoirement parmi plusieurs réponses possibles pour chaque catégorie
- **Calcul de similarité** : Utilisation d'algorithmes simples pour détecter l'intention même quand les mots-clés exacts ne sont pas présents

### Comment Personnaliser

Vous pouvez facilement améliorer l'agent en:

- **Ajoutant de nouveaux sujets** dans le dictionnaire `connaissances` et de nouvelles réponses dans `reponses` du fichier `agent.py`
- **Modifiant le fichier CSS** pour changer l'apparence de l'interface
- **Ajoutant de nouvelles routes** dans `app.py` pour créer des fonctionnalités supplémentaires
- **Améliorant l'analyse de texte** dans `nlp_utils.py` pour une meilleure compréhension des questions
- **Étendant la mémoire** dans `memory.py` pour stocker des informations plus complexes

## Dépannage

- **Problème d'installation** : Si l'installation de certaines bibliothèques échoue, essayez d'installer uniquement les dépendances essentielles : `flask`, `nltk`, et `python-dotenv`
- **L'application ne se lance pas** : Vérifiez que Python est bien installé et dans votre PATH. Essayez les commandes `python`, `python3` ou `py -3` selon votre configuration
- **Problèmes d'affichage** : Si l'interface ne s'affiche pas correctement, essayez de vider le cache de votre navigateur

## Extensions Possibles

Voici quelques idées pour améliorer l'agent:

1. **Reconnaissance vocale** : Intégrer la bibliothèque SpeechRecognition pour interagir vocalement
2. **Synthèse vocale** : Ajouter la fonctionnalité text-to-speech avec pyttsx3 pour que l'agent puisse parler
3. **Apprentissage automatique** : Implémenter un système d'apprentissage à partir des conversations pour améliorer les réponses
4. **Base de connaissances externe** : Connecter l'agent à une base de données ou à des APIs pour enrichir ses connaissances
5. **Détection d'intentions avancée** : Utiliser des modèles NLP plus sophistiqués comme spaCy ou transformers
6. **Interface en temps réel** : Ajouter des WebSockets pour une communication en temps réel sans rechargement
7. **Sécurité et authentification** : Ajouter un système de comptes utilisateurs avec authentification

## Ressources Utiles

Pour continuer à apprendre:

- [Documentation Flask](https://flask.palletsprojects.com/)
- [Tutoriels Python pour débutants](https://docs.python.org/fr/3/tutorial/)
- [Introduction au NLP](https://realpython.com/nltk-nlp-python/)
- [Cours sur l'IA et le machine learning](https://www.coursera.org/learn/machine-learning)
- [Tutoriel complet sur le développement web avec Flask](https://flask.palletsprojects.com/tutorial/)
- [Approfondissement sur les WebSockets avec Flask-SocketIO](https://flask-socketio.readthedocs.io/)

## Contribution

Les contributions à ce projet sont les bienvenues ! Si vous souhaitez améliorer cet agent IA, n'hésitez pas à soumettre une pull request ou à ouvrir une issue pour discuter de vos idées.

## Licence

Ce projet est sous licence MIT. Vous êtes libre de l'utiliser, de le modifier et de le distribuer.

---

Créé avec ❤️ pour les débutants en IA et en programmation Python. Version 1.1

# Assistant IA Cindy en Python

Ce projet est un assistant virtuel intelligent créé en Python, avec une interface web pour interagir facilement avec l'agent. Il combine des techniques de traitement du langage naturel (NLP) avec un système d'apprentissage évolutif.

> **Note pour les débutants** : Ce document vous guidera pas à pas pour comprendre et utiliser cet assistant. N'hésitez pas à le lire entièrement avant de commencer.

## Comment fonctionne cet assistant (version simple)

1. Vous posez une question dans l'interface web
2. L'agent analyse votre question pour la comprendre
3. Il identifie ce que vous demandez (météo, heure, blague, etc.)
4. Il génère une réponse adaptée
5. Il apprend de cette interaction pour s'améliorer
6. Il vous propose des suggestions pour continuer la conversation

![Schéma simplifié](https://i.imgur.com/XYZ123.png) _(Note: insérez une image simple du flux d'information)_

## Ce que fait cet assistant

- **Comprend vos questions** grâce à un moteur NLP amélioré
- **Affiche la météo en temps réel** via l'API Open Meteo
- **Mémorise et apprend** de chaque conversation pour s'améliorer
- **Propose des suggestions contextuelles** basées sur vos questions
- **Détecte les intentions** dans vos messages (météo, heure, aide, etc.)
- **S'améliore avec le temps** grâce au module d'apprentissage
- **Comprend les questions même avec des fautes** d'orthographe ou de grammaire
- **Gère les ambiguïtés** comme la confusion entre heure et météo

## Structure du projet expliquée simplement

```
Agent Python/
├── app.py                 # Point de départ de l'application
├── nlp_engine.py          # Cerveau qui comprend vos questions
├── apprentissage.py       # Système qui permet à l'agent d'apprendre
├── external_services.py   # Services externes (météo, etc.)
├── memory.py              # Gère la mémoire de l'agent
├── templates/             # Dossier contenant les pages web
│   ├── index.html         # Page principale
│   └── ...                # Autres pages
├── static/                # Ressources pour l'interface
│   ├── css/               # Styles visuels
│   ├── js/                # Code JavaScript
│   └── images/            # Images
├── data/                  # Données d'apprentissage
│   ├── interactions.json  # Historique des conversations
│   └── ...                # Autres données
└── *.log                  # Fichiers de journalisation
```

## Les fichiers principaux expliqués pour débutants

1. **app.py** : Le fichier principal qui démarre tout

   - C'est le "chef d'orchestre" de l'application
   - Il crée la page web que vous voyez dans votre navigateur
   - Il reçoit vos questions et les transmet au "cerveau" (nlp_engine.py)
   - Il affiche les réponses que le "cerveau" génère
   - **En langage simple** : C'est comme le serveur dans un restaurant qui prend votre commande et vous apporte votre plat

2. **nlp_engine.py** : Le "cerveau" qui comprend vos questions

   - Il analyse le texte de votre question pour en comprendre le sens
   - Il détecte votre intention (météo, heure, blague, etc.)
   - Il extrait les informations importantes (ville, date, etc.)
   - Il choisit la meilleure réponse à vous donner
   - **En langage simple** : C'est comme le chef cuisinier qui interprète votre commande

3. **apprentissage.py** : Le système qui permet à l'agent d'apprendre

   - Il enregistre chaque conversation pour s'en souvenir
   - Il analyse ces conversations pour trouver des modèles récurrents
   - Il améliore sa compréhension avec le temps
   - Il génère des statistiques pour voir les progrès
   - **En langage simple** : C'est comme un étudiant qui prend des notes et révise pour s'améliorer

4. **external_services.py** : Les services externes que l'agent utilise
   - Il se connecte à Internet pour obtenir la météo
   - Il trouve les coordonnées des villes pour la météo
   - Il interprète les symboles météo (pluie, soleil, etc.)
   - **En langage simple** : C'est comme un assistant qui appelle un spécialiste quand nécessaire

## Comment l'agent traite votre question (pas à pas)

Voici ce qui se passe quand vous posez une question comme "Quel temps fait-il à Paris aujourd'hui?" :

1. Vous tapez la question dans l'interface web
2. La question est envoyée au serveur (app.py)
3. app.py transmet la question au cerveau (nlp_engine.py)
4. nlp_engine.py analyse la question et détecte l'intention "météo"
5. nlp_engine.py extrait l'information importante : la ville "Paris"
6. nlp_engine.py demande la météo au service externe (external_services.py)
7. external_services.py récupère les données météo pour Paris
8. Une réponse est générée avec les informations météo
9. La réponse est renvoyée à l'interface utilisateur
10. L'interaction est sauvegardée pour l'apprentissage (apprentissage.py)
11. Des suggestions de questions similaires sont proposées

## Fichiers de journalisation (logs) expliqués simplement

Les fichiers "log" sont comme le carnet de bord de l'agent. Ils enregistrent tout ce que fait l'agent :

1. **apprentissage.log** : Journal du système d'apprentissage

   - Enregistre les activités d'apprentissage comme un journal intime
   - Montre comment l'agent s'améliore avec le temps
   - Affiche les erreurs pour les corriger
   - **À quoi ça sert pour vous** : Si l'agent ne répond pas correctement, ce fichier aide à comprendre pourquoi et à l'améliorer

2. **nlp_engine.log** : Journal du "cerveau"

   - Enregistre comment l'agent comprend vos questions
   - Montre les intentions détectées et les informations extraites
   - **À quoi ça sert pour vous** : Permet de voir si l'agent comprend correctement vos questions

3. **agent.log** : Journal général
   - Enregistre le démarrage et l'arrêt de l'application
   - Trace les requêtes reçues
   - **À quoi ça sert pour vous** : Utile pour vérifier si l'application fonctionne correctement

## Comment faire fonctionner ce projet (guide pas à pas)

### Prérequis (ce dont vous avez besoin)

- Python 3.6 ou plus récent (le langage de programmation)
- Connexion internet (pour la météo)

### Installation (étape par étape)

1. Téléchargez tous les fichiers du projet
2. Ouvrez un terminal (invite de commande) :
   - Sur Windows : tapez "cmd" dans la recherche et cliquez sur "Invite de commande"
   - Sur Mac : ouvrez l'application "Terminal"
3. Naviguez vers le dossier du projet :
   ```
   cd chemin/vers/le/dossier/Agent Python
   ```
4. Installez les dépendances (les outils dont l'agent a besoin) :
   ```
   pip install -r requirements.txt
   ```

### Démarrage (comment lancer l'agent)

Pour lancer l'assistant, tapez cette commande dans le terminal :

```bash
python app.py
```

Puis ouvrez votre navigateur internet et allez à l'adresse : http://127.0.0.1:5000

Vous devriez voir l'interface de l'agent avec un champ pour poser vos questions.

## Fonctionnalités à tester (essayez ces questions!)

1. **Questions météo** : "Quel temps fait-il à Paris ?" ou "Météo à Tokyo"
2. **Questions temporelles** : "Quelle heure est-il ?" ou "Quel jour sommes-nous ?"
3. **Salutations** : "Bonjour Cindy" ou "Comment vas-tu ?"
4. **Questions d'identité** : "Qui es-tu ?" ou "Comment t'appelles-tu ?"
5. **Blagues** : "Raconte-moi une blague" ou "Connais-tu une histoire drôle ?"
6. **Demandes d'aide** : "Que peux-tu faire ?" ou "Aide-moi"
7. **Suggestions** : Cliquez sur les suggestions qui apparaissent après chaque réponse

## Comprendre le système d'apprentissage (version simple)

L'agent apprend comme un enfant : il observe, mémorise et s'améliore :

1. **Observation** : Il enregistre vos questions et ses réponses
2. **Mémorisation** : Il stocke ces informations dans des fichiers (data/interactions.json)
3. **Analyse** : Il cherche des modèles récurrents dans vos questions
4. **Amélioration** : Il crée un modèle amélioré (data/modele.json)
5. **Journal** : Il note toutes ces étapes dans apprentissage.log

Pour voir comment l'agent apprend :

- Ouvrez le fichier `apprentissage.log` avec un éditeur de texte
- Regardez le dossier `data/` pour voir les informations collectées
- Visitez la page "Statistiques" dans l'interface web

## Glossaire pour débutants

- **NLP** : Traitement du Langage Naturel - technologie qui permet à l'ordinateur de comprendre le langage humain
- **Intention** : Ce que vous voulez réellement (météo, heure, blague, etc.)
- **Entité** : Information importante dans votre question (ville, date, etc.)
- **API** : Interface permettant à l'agent de communiquer avec d'autres services (comme la météo)
- **Flask** : Outil Python qui crée le site web de l'agent
- **JSON** : Format utilisé pour stocker des données dans des fichiers
- **Log** : Fichier journal qui enregistre les activités de l'agent

## Aide en cas de problème (dépannage)

- **L'application ne démarre pas** : Vérifiez que Python est bien installé (tapez `python --version` dans le terminal)
- **Erreur de module** : Vérifiez que vous avez bien installé les dépendances avec `pip install -r requirements.txt`
- **API météo non fonctionnelle** : Vérifiez votre connexion internet
- **Problème d'affichage** : Essayez de vider le cache de votre navigateur (Ctrl+F5 ou Cmd+R)
- **Agent ne comprend pas ma question** : Essayez de reformuler plus simplement
- **Message d'erreur dans l'interface** : Consultez les fichiers log pour plus de détails
- **Problèmes d'apprentissage** : Consultez le fichier `apprentissage.log` pour voir ce qui ne va pas

## Questions fréquemment posées (FAQ)

- **Est-ce que l'agent fonctionne sans internet ?** Partiellement. Les fonctions de base marchent, mais pas la météo.
- **Puis-je ajouter de nouvelles capacités ?** Oui, en modifiant le fichier `nlp_engine.py`.
- **Où sont stockées mes questions ?** Dans le dossier `data/` en format JSON.
- **L'agent garde-t-il mes données privées ?** Oui, tout reste sur votre ordinateur.
- **Comment voir les statistiques d'utilisation ?** Via la page "Statistiques" de l'interface.
- **Puis-je changer l'apparence de l'interface ?** Oui, en modifiant les fichiers dans `static/css/`.

---

Projet créé pour explorer le traitement du langage naturel et l'apprentissage automatique en Python d'une manière accessible à tous.

# Assistant IA en Python

Ce projet est un assistant virtuel simple créé en Python, avec une interface web pour interagir facilement avec l'agent. Il est conçu de manière pédagogique pour les débutants en programmation.

## Ce que fait cet assistant

- **Répond à des questions** en analysant vos messages
- **Affiche la météo** de n'importe quelle ville
- **Mémorise vos conversations** pour mieux vous comprendre
- **Propose des suggestions** de questions à poser
- **Apprend de nouvelles connaissances** que vous lui enseignez
- **Affiche des statistiques** sur votre utilisation

## Les fichiers principaux

1. **app.py** : Le cœur de l'application web (utilise Flask)

   - Gère les pages web et les formulaires
   - Traite les requêtes HTTP
   - Connecte l'interface utilisateur à l'agent

2. **agent.py** : L'intelligence de l'assistant

   - Comprend les questions
   - Génère des réponses adaptées
   - Stocke des connaissances dans différentes catégories

3. **nlp_utils.py** : Outils d'analyse de texte

   - Nettoie le texte (ponctuation, minuscules)
   - Extrait les mots importants
   - Analyse le sentiment (positif/négatif/neutre)
   - Identifie le type de question

4. **memory.py** : Système de mémoire de l'agent

   - Stocke l'historique des conversations
   - Sauvegarde les informations à long terme
   - Permet de rechercher des informations passées

5. **external_services.py** : Services externes
   - Récupère la météo depuis une API
   - Formate les informations météo

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
py -3 app.py
```

Puis ouvrez votre navigateur à l'adresse : http://127.0.0.1:5000

## Les pages de l'application

- **Page principale** : Pour discuter avec l'agent
- **Historique** : Pour voir les conversations passées
- **Statistiques** : Pour voir des données sur votre utilisation
- **Enseigner** : Pour apprendre de nouvelles choses à l'agent

## Personnalisation simple

Vous pouvez facilement améliorer l'agent en :

1. **Ajoutant des connaissances** dans le fichier `agent.py`
2. **Modifiant l'apparence** dans les fichiers CSS du dossier `static/css`
3. **Ajoutant des fonctionnalités** dans le fichier `app.py`

## Guide pas à pas pour présenter ce projet

1. **Introduction** : "Voici un assistant virtuel fait avec Python"
2. **Démonstration** : Montrez l'interface et posez quelques questions
3. **Météo** : Demandez la météo d'une ville pour montrer cette fonctionnalité
4. **Structure** : Expliquez le rôle de chaque fichier principal
5. **Conclusion** : Parlez des améliorations possibles

## Aide en cas de problème

- **L'application ne démarre pas** : Vérifiez que Python est bien installé
- **Erreur de module** : Vérifiez que vous avez bien installé les dépendances
- **Problème d'affichage** : Essayez de vider le cache de votre navigateur

---

Projet créé pour apprendre les bases de la programmation Python et de l'intelligence artificielle conversationnelle.

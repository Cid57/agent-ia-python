# Architecture de l'Assistant IA

Ce document explique simplement comment les différents fichiers Python du projet interagissent entre eux.

## Diagramme d'architecture

```
+-----------------+      +-----------------+     +------------------+
| Interface Web   |      |    Cerveau      |     |   Mémoire        |
| (app.py)        |<---->|    (agent.py)   |<--->|   (memory.py)    |
+-----------------+      +-----------------+     +------------------+
         ^                       ^
         |                       |
         v                       v
+-----------------+      +-----------------+
| Pages HTML      |      | Service Météo   |
| (templates/*.html) |      | (external_services.py) |
+-----------------+      +-----------------+
         ^                       ^
         |                       |
         v                       v
+-----------------+      +-----------------+
| Style & Scripts |      | Analyse de Texte|
| (static/*)      |      | (nlp_utils.py)  |
+-----------------+      +-----------------+
```

## Explication simple

1. **Quand un utilisateur visite le site :**

   - `app.py` gère la requête et affiche la page d'accueil (`index.html`)
   - JavaScript (`app.js`) contrôle l'interface

2. **Quand l'utilisateur pose une question :**

   - `app.py` reçoit la question et l'envoie à `agent.py`
   - `agent.py` utilise `nlp_utils.py` pour comprendre la question
   - Si c'est une question sur la météo, `agent.py` appelle `external_services.py`
   - `agent.py` génère une réponse et la renvoie à `app.py`
   - `app.py` enregistre la conversation dans `memory.py`
   - La réponse est affichée dans l'interface

3. **Quand l'utilisateur consulte l'historique :**

   - `app.py` demande à `memory.py` de récupérer les conversations passées
   - Les données sont affichées dans `historique.html`

4. **Quand l'utilisateur enseigne à l'agent :**

   - `app.py` reçoit les nouvelles informations via `enseigner.html`
   - Ces informations sont envoyées à `agent.py` pour être mémorisées

5. **Quand l'utilisateur consulte les statistiques :**
   - `app.py` demande à `agent.py` de fournir les statistiques d'utilisation
   - Les statistiques sont affichées dans `statistiques.html`

Ce modèle d'architecture est appelé "Modèle-Vue-Contrôleur" (MVC), où :

- Les "Modèles" sont `agent.py`, `memory.py` et `nlp_utils.py`
- Les "Vues" sont les fichiers HTML et CSS
- Le "Contrôleur" est `app.py`

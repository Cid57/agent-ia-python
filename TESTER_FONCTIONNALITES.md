# Guide de test des nouvelles fonctionnalités de Cindy

Ce guide vous explique pas à pas comment tester et explorer toutes les nouvelles fonctionnalités de votre assistant IA Cindy.

## Lancer l'application

1. Ouvrez un terminal
2. Accédez au répertoire du projet
3. Exécutez la commande :
   ```
   python app.py
   ```
4. Ouvrez votre navigateur à l'adresse : http://127.0.0.1:5000

## 1. Tester le moteur de compréhension amélioré

### Test des intentions

Essayez ces phrases pour tester la détection d'intentions :

- **Météo** :

  - "Quel temps fait-il à Paris ?"
  - "Donne-moi la météo pour New York"
  - "Est-ce qu'il pleut à Tokyo ?"
  - "Météo Lyon"

- **Heure et date** :

  - "Quelle heure est-il ?"
  - "Dis-moi l'heure s'il te plaît"
  - "Quel jour sommes-nous ?"
  - "Quelle est la date aujourd'hui ?"

- **Salutations** :

  - "Bonjour Cindy"
  - "Salut, comment ça va ?"
  - "Hello !"

- **Bien-être** :

  - "Comment vas-tu ?"
  - "Tu vas bien ?"
  - "Comment te sens-tu aujourd'hui ?"

- **Capacités** :
  - "Que sais-tu faire ?"
  - "Quelles sont tes fonctionnalités ?"
  - "Comment peux-tu m'aider ?"

## 2. Tester l'API météo

Testez la connectivité avec l'API météo en demandant la météo pour différentes villes :

- Des grandes villes connues : Paris, New York, Tokyo
- Des villes françaises : Lyon, Marseille, Bordeaux
- Des villes avec des caractères spéciaux : Saint-Étienne, São Paulo

Observez comment Cindy :

- Détecte correctement le nom de la ville
- Récupère les informations météo en temps réel
- Affiche la température, les conditions et d'autres détails

## 3. Tester les suggestions dynamiques

Après chaque réponse de Cindy, vous verrez apparaître des suggestions de questions. Testez comment :

1. Les suggestions changent en fonction du contexte de la conversation
2. Cliquer sur une suggestion pose automatiquement la question
3. Les suggestions sont pertinentes selon l'intention détectée

Par exemple :

- Après une question météo, vous verrez des suggestions liées à d'autres villes
- Après une question sur l'heure, vous verrez des suggestions sur la date
- Après une salutation, vous verrez des suggestions générales

## 4. Tester le système d'apprentissage

Le système d'apprentissage fonctionne en arrière-plan. Pour vérifier son fonctionnement :

1. Posez plusieurs questions variées à Cindy (au moins 10-15 questions)
2. Vérifiez que le dossier `data` a été créé à la racine du projet
3. Explorez les fichiers dans ce dossier :
   - `interactions.json` : contient l'historique des conversations
   - `statistiques.json` : contient les analyses des interactions
   - `modele.json` : contient le modèle amélioré (si généré)

Pour voir les statistiques générées, lancez la commande :

```
python apprentissage.py
```

## 5. Tester l'extraction d'entités

Testez comment Cindy reconnaît automatiquement les entités dans vos questions :

- **Villes** : "Quel temps fait-il à Lyon ?" (doit reconnaître "Lyon")
- **Nombres** : "Donne-moi la météo pour les 3 prochains jours" (doit reconnaître "3")
- **Majuscules** : "Comment va la météo à Paris et à MARSEILLE ?" (doit reconnaître "Paris" et "MARSEILLE")

## 6. Tester la robustesse

Pour vérifier que Cindy est robuste, essayez :

- Des questions mal orthographiées : "Kelle heure est-il ?"
- Des questions incomplètes : "Météo ?"
- Des questions vides ou très courtes : " " ou "?"
- Des questions inattendues : "J'aime les chats"

Cindy devrait répondre de façon appropriée même face à ces entrées inhabituelles.

## 7. Tester la personnalisation

Pour voir comment adapter Cindy à vos besoins :

1. Ouvrez le fichier `nlp_engine.py`
2. Ajoutez une nouvelle intention avec ses mots-clés (ex: "musique", "film", etc.)
3. Ajoutez les réponses correspondantes dans la fonction `generer_reponse_simple`
4. Ajoutez des suggestions dans la fonction `generer_suggestions`
5. Redémarrez l'application et testez votre nouvelle intention

---

## Analyse des résultats

Après avoir testé ces fonctionnalités, vous remarquerez que :

1. Cindy comprend une variété de formulations pour la même question
2. Les réponses sont contextuelles et pertinentes
3. Le système s'améliore plus vous l'utilisez
4. L'interface est fluide et agréable à utiliser

Ces améliorations rendent votre agent plus intelligent et plus naturel dans ses interactions.

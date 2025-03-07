"""
Module centralisé pour les réponses de l'agent Cindy.
Ce fichier regroupe toutes les réponses possibles pour éviter les duplications
et assurer la cohérence.
"""

# Fonction pour personnaliser les réponses avec le nom de l'agent
def obtenir_reponses(nom_agent="Cindy"):
    """
    Génère un dictionnaire de réponses en intégrant le nom de l'agent.
    
    Args:
        nom_agent (str): Nom de l'agent à utiliser dans les réponses
        
    Returns:
        dict: Dictionnaire des réponses possibles par catégorie
    """
    return {
        "salutation": [
            f"Bonjour ! Comment puis-je vous aider aujourd'hui ?",
            f"Salut ! Je suis {nom_agent}, votre assistante. Que puis-je faire pour vous ?",
            f"Bonjour ! Que puis-je faire pour vous ?"
        ],
        "meteo": [
            "Je vais consulter la météo pour vous.",
            "Laissez-moi vérifier la météo.",
            "Je recherche les informations météo."
        ],
        "heure": [
            "Il est actuellement [HEURE].",
            "L'heure actuelle est [HEURE].",
            "En ce moment, il est [HEURE]."
        ],
        "date": [
            "Nous sommes le [DATE].",
            "Aujourd'hui, nous sommes le [DATE].",
            "La date d'aujourd'hui est le [DATE]."
        ],
        "remerciement": [
            "De rien ! C'est un plaisir de t'aider.",
            "Je t'en prie. Y a-t-il autre chose que je puisse faire pour toi ?",
            "Avec plaisir ! N'hésite pas si tu as d'autres questions.",
            "De rien, c'est toujours agréable de pouvoir t'aider !",
            "Pas de souci, c'est mon rôle de t'être utile !",
            "Je suis contente de pouvoir t'aider. N'hésite pas si tu as besoin d'autre chose."
        ],
        "au_revoir": [
            "Au revoir ! N'hésitez pas à revenir si vous avez d'autres questions.",
            "À bientôt ! J'ai été ravie de pouvoir vous aider.",
            "Au plaisir de vous revoir bientôt !"
        ],
        "bien_etre": [
            "Je vais super bien aujourd'hui, merci de demander ! Et toi, comment ça va ?",
            "Tout va bien, merci ! C'est gentil de t'inquiéter pour moi. Et de ton côté ?",
            "Je me sens en pleine forme ! J'espère que ta journée se passe bien aussi ?",
            "Ça va très bien, merci ! Et toi, comment se passe ta journée ?",
            "Plutôt bien ! C'est toujours un plaisir de discuter avec toi. Comment vas-tu ?",
            "Je me porte à merveille, merci ! J'espère que toi aussi ?"
        ],
        "reponse_bien_etre": [
            "Je suis contente de l'apprendre ! Comment puis-je t'aider aujourd'hui ?",
            "C'est super ! Que puis-je faire pour toi ?",
            "Excellent ! Je suis là si tu as besoin de quoi que ce soit.",
            "Tant mieux ! Y a-t-il quelque chose dont tu voudrais discuter ?",
            "Merci de partager ça avec moi ! En quoi puis-je t'être utile ?",
            "C'est bien de le savoir ! N'hésite pas à me demander de l'aide si tu en as besoin.",
            "Parfait ! Que veux-tu savoir ou faire maintenant ?",
            "Compris ! Je suis prête à t'aider pour la suite."
        ],
        "aide": [
            f"Je suis {nom_agent}, votre assistant IA. Je peux répondre à des questions, vous donner l'heure, la météo, raconter des blagues et discuter avec vous. Essayez de me demander 'Quelle heure est-il ?', 'Quel temps fait-il à Paris ?' ou 'Raconte-moi une blague'.",
            "Je peux vous aider sur plusieurs sujets : l'heure actuelle, la météo dans différentes villes, des blagues, des informations sur moi-même. Essayez de me poser ces questions !",
            "Comment puis-je vous aider aujourd'hui ? Je peux vous donner l'heure, la météo, vous raconter une blague, ou simplement discuter avec vous. N'hésitez pas à demander !"
        ],
        "capacites": [
            "Je peux vous donner la météo, l'heure, la date, et répondre à vos questions générales.",
            f"Mes capacités incluent : informations météo, heure et date, assistance générale et conversation simple.",
            "Je suis capable de vous informer sur la météo, vous donner l'heure et la date, et répondre à diverses questions."
        ],
        "identite": [
            f"Je suis {nom_agent}, votre assistante IA personnelle. Je suis là pour vous aider avec diverses questions et tâches.",
            f"Je m'appelle {nom_agent}, une intelligence artificielle conçue pour répondre à vos questions et vous assister au quotidien.",
            f"Je suis {nom_agent}, une assistante virtuelle développée pour vous aider. Je peux répondre à vos questions sur la météo, l'heure et bien plus encore."
        ],
        "entreprise": [
            "Digital Factory est une entreprise innovante spécialisée dans le développement d'agents conversationnels et d'intelligences artificielles. Elle a été fondée par des experts en IA et en développement web pour créer des solutions d'assistants virtuels personnalisés comme moi.",
            "Digital Factory est une start-up technologique qui développe des assistants IA comme moi. L'entreprise se spécialise dans la création d'agents conversationnels intelligents et personnalisables pour différents secteurs d'activité.",
            "Digital Factory est l'entreprise qui m'a créée. C'est une société spécialisée dans le développement d'agents conversationnels innovants et d'intelligences artificielles destinées à assister les utilisateurs dans leurs tâches quotidiennes."
        ],
        "createur": [
            f"J'ai été conçue et programmée par Cindy Singer, une passionnée de Digital Factory. Elle a mis tout son savoir-faire pour me doter de mes capacités et de ma personnalité. Je suis en constante évolution pour mieux vous accompagner.",
            f"Mon créateur est Cindy Singer, une experte en intelligence artificielle travaillant chez Digital Factory. Elle s'est spécialisée dans le développement d'assistantes IA comme moi pour rendre la technologie plus accessible et utile au quotidien.",
            f"C'est Cindy Singer qui m'a créée. Elle travaille pour Digital Factory et se passionne pour le développement d'intelligences artificielles conversationnelles. Grâce à elle, je peux répondre à vos questions et vous aider dans vos tâches."
        ],
        "fonctionnement": [
            "Je fonctionne grâce à un système de traitement du langage naturel qui me permet de comprendre vos questions. J'analyse les mots-clés, détecte vos intentions et accède à différentes sources d'information pour vous fournir les réponses les plus pertinentes.",
            f"En tant qu'assistant IA, j'utilise des algorithmes d'analyse de texte pour comprendre vos questions. Je détecte les mots-clés importants, j'identifie votre intention et je formule une réponse adaptée en utilisant ma base de connaissances.",
            "Mon fonctionnement repose sur l'analyse de votre texte pour en extraire le sens et l'intention. J'ai été programmé pour reconnaître différents types de questions et y répondre de manière appropriée, que ce soit pour la météo, l'heure, ou d'autres informations."
        ],
        "blague": [
            "Pourquoi les plongeurs plongent-ils toujours en arrière et jamais en avant ? Parce que sinon ils tombent dans le bateau !",
            "Un électron frappe à la porte d'un hôtel. Le réceptionniste lui demande : 'Vous désirez une chambre ?' Et l'électron répond : 'Non merci, je suis déjà excité.'",
            "Qu'est-ce qu'un crocodile qui surveille la pharmacie ? Un Lacoste Garde.",
            "Pourquoi les informaticiens confondent-ils Halloween et Noël ? Parce qu'Oct 31 = Dec 25.",
            "Que dit un informaticien quand il s'ennuie ? Je bit ma vie !",
            "Un DRH demande à un informaticien : 'Quelle est la différence entre toi et moi ?' L'informaticien répond : 'Moi, on me demande de résoudre des problèmes qu'on ne comprend pas, alors que toi tu crées des problèmes qu'on ne peut pas résoudre.'",
            "Pourquoi les développeurs n'aiment pas la nature ? Parce qu'elle a trop de bugs.",
            "Qu'est-ce qu'un Geek dit quand vous lui demandez s'il veut une bière ? Alt Tab on revient au bar.",
            "Comment un informaticien ouvre-t-il une bouteille ? Il la débogue.",
            "J'ai une blague sur les algorithmes de tri mais elle n'est pas encore ordonnée.",
            "Qu'est-ce qui est jaune et qui attend ? Jonathan.",
            "Pourquoi les abeilles produisent-elles du miel ? Parce qu'elles n'ont pas lu les conditions d'utilisation.",
            "Quel est l'animal le plus connecté ? Le porc USB.",
            "Deux gouttes d'eau se rencontrent. L'une dit : 'Tiens, tu es là ! Ça fait une éternité qu'on ne s'est pas vues !' Et l'autre répond : 'Normal, on s'est évaporées !'",
            "Qu'est-ce qui est petit, carré et jaune ? Un petit carré jaune.",
            "Qu'est-ce qu'un canif ? Un petit fien.",
            "Pourquoi les girafes ont-elles un long cou ? Parce qu'elles ont les pieds qui sentent mauvais.",
            "Comment appelle-t-on un chat tombé dans un pot de peinture le jour de Noël ? Un chat-peint de Noël.",
            "Quand un crocodile voit une femelle, que dit-il ? Oh, c'est crocmignon !",
            "Pourquoi les oiseaux volent-ils vers le sud en hiver ? Parce que c'est trop loin d'y aller à pied.",
            "Un œuf attend devant un passage piéton. Un autre œuf lui demande : 'Tu traverses pas ?' Et le premier répond : 'Non, j'ai pas envie d'être brouillé avec le conducteur !'",
            "Qu'est-ce qu'un yaourt dans la forêt ? Un yaourt nature.",
            "Qu'est-ce qui est vert et qui monte et qui descend ? Un petit pois dans un ascenseur.",
            "Comment appelle-t-on un boomerang qui ne revient pas ? Un bâton.",
            "Comment appelle-t-on un chat tout-terrain ? Un cat-cat.",
            "Pourquoi les moutons aiment-ils compter les humains avant de s'endormir ? Pour rêver."
        ],
        "inconnu": [
            "Je ne suis pas sûr(e) de comprendre votre demande. Pouvez-vous reformuler ?",
            "Désolé(e), je n'ai pas bien saisi. Pouvez-vous préciser votre question ?",
            "Je ne comprends pas complètement. Essayez de poser votre question différemment."
        ]
    }

# Générer les suggestions en fonction de l'intention
def obtenir_suggestions(intention="inconnu"):
    """
    Fournit des suggestions de questions basées sur l'intention détectée.
    
    Args:
        intention (str): L'intention détectée
        
    Returns:
        list: Liste de suggestions de questions
    """
    suggestions = {
        "salutation": [
            "Quelle est la météo aujourd'hui ?",
            "Quelle heure est-il ?",
            "Raconte-moi une blague",
            "Quel jour sommes-nous ?"
        ],
        "meteo": [
            "Quelle heure est-il ?",
            "Raconte-moi une blague",
            "Qui es-tu ?",
            "Quel jour sommes-nous ?",
            "Comment vas-tu ?"
        ],
        "heure": [
            "Quelle est la date aujourd'hui ?",
            "Quel temps fait-il à Paris ?",
            "Raconte-moi une blague",
            "Comment vas-tu ?"
        ],
        "date": [
            "Quelle heure est-il ?",
            "Raconte-moi une blague",
            "Qui es-tu ?",
            "Comment vas-tu ?"
        ],
        "remerciement": [
            "Puis-je te poser une autre question ?",
            "J'aurais besoin d'autre chose",
            "Quelle heure est-il ?",
            "Raconte-moi une blague"
        ],
        "bien_etre": [
            "Quelle est la météo aujourd'hui ?",
            "Quelle heure est-il ?",
            "Raconte-moi une blague",
            "Quel jour sommes-nous ?"
        ],
        "aide": [
            "Quelle est la météo à Paris ?",
            "Quelle heure est-il ?",
            "Raconte-moi une blague",
            "Comment vas-tu ?"
        ],
        "capacites": [
            "Donne-moi la météo pour Paris",
            "Quelle heure est-il ?",
            "Raconte-moi une blague",
            "Quel jour sommes-nous ?"
        ],
        "identite": [
            "Quelles sont tes capacités ?",
            "Quelle est la météo aujourd'hui ?",
            "Raconte-moi une blague",
            "Quelle heure est-il ?"
        ],
        "entreprise": [
            "Qui t'a créée ?",
            "Quelles sont tes capacités ?",
            "Comment fonctionnes-tu ?",
            "Raconte-moi une blague"
        ],
        "createur": [
            "C'est quoi Digital Factory ?",
            "Quelles sont tes capacités ?",
            "Comment fonctionnes-tu ?",
            "Raconte-moi une blague"
        ],
        "fonctionnement": [
            "Comment fonctionnes-tu ?",
            "Quelles sont tes capacités ?",
            "Raconte-moi une blague"
        ],
        "reponse_bien_etre": [
            "Quelle heure est-il ?",
            "Quel temps fait-il à Paris ?",
            "Raconte-moi une blague",
            "Qui t'a créé ?"
        ],
        "blague": [
            "Raconte-moi une autre blague",
            "Quelle heure est-il ?",
            "Quelle est la météo aujourd'hui ?",
            "Comment vas-tu ?"
        ],
        "inconnu": [
            "Quelle est la météo à Paris ?",
            "Quelle heure est-il ?",
            "Raconte-moi une blague",
            "Comment vas-tu ?"
        ]
    }
    
    # Si l'intention est connue, retourner les suggestions correspondantes
    if intention in suggestions:
        return suggestions[intention]
    
    # Sinon, retourner les suggestions par défaut
    return suggestions["inconnu"]

# Pour les tests
if __name__ == "__main__":
    print("Test des réponses centralisées :")
    reponses = obtenir_reponses("TestAgent")
    print(f"Nombre de catégories : {len(reponses)}")
    print(f"Nombre de blagues : {len(reponses['blague'])}")
    
    print("\nTest des suggestions :")
    for intention in ["salutation", "meteo", "blague"]:
        suggestions = obtenir_suggestions(intention)
        print(f"Intention '{intention}' → {len(suggestions)} suggestions") 
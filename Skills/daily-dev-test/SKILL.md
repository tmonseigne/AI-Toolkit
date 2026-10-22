---
name: daily-dev-test
description: Proposer un microtest quotidien de développement de cinq minutes maximum, corriger le raisonnement et adapter les sujets et la difficulté grâce à un historique local. Utiliser pour un daily test, un exercice de vigilance ou un quiz de logique, algorithmie, architecture ou connaissances de développement.
---

# Microtest quotidien de développement

Entretenir la capacité à raisonner et à repérer une proposition plausible mais incorrecte, notamment dans du code produit par une IA.
Faire travailler l’utilisateur avant de donner la solution.
Une invocation lance une séance, pas une programmation quotidienne automatique.

## Stockage et préparation

La source de la skill reste inchangée pendant les séances.
Déterminer `<root>` en réutilisant le dossier d’historique déjà indiqué dans cette conversation ; à défaut, utiliser la racine réelle du dépôt AI-Toolkit qui contient cette skill, en résolvant une éventuelle jonction d’installation.
Un dossier explicitement choisi par l’utilisateur prime sur ce défaut.
Conserver ce même emplacement même si la conversation porte sur un autre projet, pour ne pas fragmenter la progression.
Les chemins suivants sont relatifs à `<root>` :

- `_artifacts/daily-dev-test/sessions/<id>.json` : archive faisant foi, avec énoncé, correction attendue, réponse réelle et évaluation.
- `_artifacts/daily-dev-test/inputs/` : fichiers JSON de travail transmis au script.
- `_output/daily-dev-test/<id>.md` : fiche lisible, sans solution tant que la séance est en attente.

Vérifier que `_artifacts/` et `_output/` sont ignorés par Git dans le dossier choisi ; si nécessaire, ajouter uniquement ces exclusions dans le périmètre autorisé.
Ne pas stocker l’historique dans le dossier installé de la skill, ni dans ses ressources suivies par Git.
Les archives sont personnelles ; ne pas y recopier de code confidentiel provenant d’autres projets.

Exécuter au début de la séance :

```powershell
python -X utf8 <skill>/scripts/session_history.py context --root <root>
```

Le script lit toutes les archives, calcule un niveau par domaine et expose les trente derniers concepts ainsi que les séances en attente.
Si une archive est illisible ou invalide, préserver le fichier et signaler le problème ; ne pas repartir silencieusement de zéro.
Sans Python, lire les mêmes archives et appliquer les mêmes règles manuellement ; signaler ce fonctionnement dégradé.

## Choisir et préparer l’exercice

Reprendre d’abord une séance en attente, sans révéler sa solution, sauf demande de la passer ou de lancer un nouvel exercice.
Ne pas déduire un échec d’une absence de réponse.
Une demande de nouvelle séance permet d’archiver l’ancienne comme `skipped`, avec une raison, avant de continuer.

Par défaut, choisir le domaine le moins récemment proposé parmi `logic`, `algorithms`, `architecture` et `knowledge`.
Une préférence explicite de sujet ou de difficulté prime sur cette rotation ; consigner le niveau effectivement présenté.
Alterner les formes : trouver un contre-exemple, prévoir un comportement, choisir une structure de données, départager deux architectures sous contraintes, identifier une hypothèse manquante ou une erreur dans une proposition d’IA.
Le contexte Python, C++20, calcul scientifique, mémoire, concurrence ou interfaces Qt peut servir d’ancrage, sans limiter toutes les questions à la microscopie.

Consulter l’historique avant de formuler la question :

- Éviter le même concept dans les sept dernières séances et les simples changements de noms ou de chiffres ; examiner les énoncés archivés si les résumés ne suffisent pas.
- Reprendre une difficulté rencontrée après au moins trois autres séances et, de préférence, sept jours, avec un autre contexte et une autre forme ; cette révision espacée peut déroger à la règle des sept séances.
- Ne pas maintenir artificiellement une série quotidienne ni pénaliser une interruption.

Prévoir **un seul exercice**, une réponse de quelques lignes et au plus deux demandes étroitement liées, par exemple « Quel défaut vois-tu et quel contre-exemple le démontre ? ».
Budget cible : lecture 30 secondes, réflexion et réponse 3 minutes, correction 1 minute, avec une marge de 30 secondes.
Éviter installation, recherche, compilation ou implémentation longue à la charge de l’utilisateur.
Un exercice de niveau élevé doit demander une observation plus subtile, pas plus de travail.
La durée est un budget conseillé, jamais une mesure déduite du délai entre messages ; ne pas prétendre interrompre automatiquement après cinq minutes.

Préparer **avant présentation** une solution justifiée et un barème de 0 à 2 : 0 = point essentiel absent ou faux ; 1 = intuition juste mais justification ou condition essentielle manquante ; 2 = conclusion et justification suffisantes.
Pour l’architecture, expliciter les contraintes et accepter les autres choix défendables ; ne pas inventer une réponse universelle.
Pour le code, préciser les hypothèses et versions nécessaires ; éviter une sortie déterministe si le comportement est indéfini ou non spécifié.
Valider le raisonnement à la main avec un exemple et un cas limite ; utiliser un petit programme isolé si cela résout une incertitude, sans exécuter de code dangereux.
Privilégier des connaissances stables ; vérifier dans une source primaire tout fait incertain ou dépendant d’une version avant de le noter.
Si l’énoncé ou le corrigé s’avère erroné, annuler la séance avec `skipped` et une explication, sans pénaliser le niveau.

Créer un enregistrement `pending` selon [le contrat des archives](references/history.md), puis le sauvegarder :

```powershell
python -X utf8 <skill>/scripts/session_history.py save --root <root> --input <root>/_artifacts/daily-dev-test/inputs/<id>.json
```

Présenter uniquement le domaine, le niveau sur 5, le temps conseillé et l’énoncé dans la conversation.
Demander une justification courte dans l’énoncé et attendre la réponse ; ne pas fournir le corrigé, un indice spontané ou des choix qui trahissent la solution.
La solution préparée reste dans l’archive technique ; ne pas ouvrir cette archive dans l’interface ni la joindre à l’énoncé.

## Corriger et adapter

Sur réponse, relire la séance en attente et évaluer le raisonnement réellement exprimé, en acceptant toute solution équivalente.
Si la réponse est ambiguë, poser au plus une précision courte dans le budget ; sinon noter l’incertitude sans inventer une intention.
Un indice est disponible sur demande : marquer `assisted: true` et fournir une aide minimale.
Une solution explicitement demandée sans tentative termine la séance avec `score: null`, sans changer le niveau.

Donner une correction de lecture inférieure à une minute : résultat, raison décisive, éventuel contre-exemple et un réflexe réutilisable.
Afficher le score sur 2 et le niveau du domaine ; présenter ce score comme un repère local, pas une mesure générale de compétence.
Ne pas lancer spontanément un deuxième exercice.
Reporter la réponse fidèle, les aides, la note et la correction dans le même enregistrement, passer à `completed`, puis le sauvegarder avec le script.
Fournir le lien vers la fiche Markdown générée.
Ne jamais fabriquer de séances ou de réponses pour enrichir l’historique.

Le script part du niveau 3/5 dans chaque domaine et rejoue chronologiquement les résultats : trois scores de 2 consécutifs sans aide font monter d’un niveau ; deux scores consécutifs de 0 ou 1 sans aide font descendre d’un niveau.
Les séries repartent de zéro après un changement ; une séance aidée ou sans note interrompt les séries sans modifier le niveau.
Une séance passée n’intervient pas dans ces séries.
Une séance présentée à un autre niveau que le niveau calculé ne modifie pas ce dernier et interrompt ses séries.
Bornes : 1 = fondamental ciblé, 2 = application directe, 3 = analyse et justification, 4 = interaction de contraintes, 5 = cas subtil sous hypothèses explicites.
Ces règles sont prudentes avec peu de données ; ne pas annoncer une progression démontrée après un seul exercice.

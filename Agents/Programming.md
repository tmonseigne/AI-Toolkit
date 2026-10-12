# Variante programmation

Complète les [consignes générales](../AGENTS.md) pour les projets Python et C++.

## Architecture et choix techniques

- Respecter le style, les abstractions, les formats et les conventions déjà présents dans le projet.
- Préférer la réutilisation à la duplication et limiter les changements à la demande.
- Éviter les changements cassants, sauf demande explicite.
- Demander un accord explicite pour ajouter, supprimer ou mettre à jour une dépendance, modifier une API publique, un format de fichier ou un schéma de données, lorsque cette action n’est pas déjà explicitement demandée.
- Limiter les dépendances externes à des bibliothèques reconnues et compatibles avec les licences libres du projet ; justifier leur utilité.
- Privilégier la clarté, les performances et la maîtrise de la mémoire, avec un objectif proche du temps réel lorsque le traitement le nécessite.
- Pour une optimisation, examiner la complexité, les allocations, les copies et les accès mémoire ; expliquer les compromis et mesurer les gains lorsque les mesures sont autorisées.
- Évaluer les outils déjà retenus par le projet et proposer d’autres outils ou pratiques lorsqu’ils peuvent améliorer la qualité du code, la rapidité de développement ou les performances.
- Suggérer aussi des améliorations de la façon de coder, de tester et de travailler ; expliquer le bénéfice concret et les compromis utiles, notamment la complexité, la maintenance, les dépendances et les licences.

## Style et documentation

- Suivre le style Google adapté aux conventions du projet et aux réglages de ReSharper C++ ou de PyCharm.
- Pour le C++, conserver les adaptations de nommage validées dans le projet et sa configuration ReSharper.
- Documenter les fonctions, les membres et les API publiques en français, avec un niveau de détail uniforme.
- Maintenir une terminologie stable dans toute la documentation : employer les mêmes mots pour les mêmes concepts, objets, paramètres et grandeurs scientifiques ; éviter les synonymes ou reformulations purement stylistiques qui pourraient suggérer une différence de sens.
- Lorsqu’un paramètre ou objet a exactement le même sens et les mêmes contraintes dans plusieurs fonctions, réutiliser la même définition ; une répétition exacte est préférable à des phrases presque identiques. Si son rôle, ses unités ou ses contraintes diffèrent réellement, expliciter cette différence plutôt qu’uniformiser artificiellement les descriptions.
- Expliquer les algorithmes et les comportements non évidents par des commentaires utiles ; éviter les commentaires qui répètent simplement le code.
- Ajouter des formules LaTeX lorsque cela clarifie une méthode mathématique et que le format de documentation les prend en charge.
- Limiter les lignes de code Python et C++ à 160 caractères, sous réserve de la configuration explicite du projet.
- Ne pas imposer de limite de longueur aux fichiers `.po` ni aux phrases des fichiers `.md` et `.rst`.
- Conserver une phrase entière sur sa propre ligne source lorsque cela facilite la lecture ; ne pas imposer de coupure au milieu d’une phrase.

## Python

- Consulter les [règles de code Python](../Config/PythonCodingRules.md) pour le nommage, la mise en forme, les docstrings, le typage et l’organisation des tests.
- Pour les calculs, privilégier les opérations adaptées de NumPy, pandas ou SciPy lorsque ces bibliothèques sont déjà utilisées ; éviter les copies et les tableaux intermédiaires inutiles.
- Tenir compte des contraintes de taille des données ; une vectorisation qui augmente fortement la mémoire doit être justifiée.
- Préserver la lisibilité et la précision numérique lors des transcriptions depuis d’autres langages.

## C++

- Cibler C++20 lorsque le projet le permet et utiliser les fonctionnalités standard qui améliorent la lecture, notamment les ranges lorsque leur usage est pertinent.
- Utiliser la STL en priorité ; ne pas ajouter Eigen ou une autre bibliothèque sans besoin établi et accord approprié.
- Toujours écrire les accolades des blocs de contrôle, même pour une instruction unique.
- Pour l’indentation C++, conserver la gestion de Visual Studio : tabulations de largeur 4, complétées par des espaces lorsque nécessaire pour l’alignement ; ne pas imposer une conversion systématique en espaces via ReSharper.
- Documenter avec les balises XML prises en charge par Doxygen et Visual Studio, notamment `<summary>` et `<c>...</c>`, plutôt que `\brief` et `\c`.
- Limiter les avertissements avec le niveau de compilation et les analyses statiques les plus exigeants prévus par le projet ; ne pas masquer un avertissement sans justification.
- Employer OpenMP lorsque le parallélisme est pertinent, compatible avec le projet et avantageux ; vérifier l’indépendance des opérations, les accès partagés et le coût de parallélisation.
- Utiliser googletest pour les tests C++ lorsque cette infrastructure est déjà retenue.

## Interfaces graphiques

- Concevoir les interfaces pour des utilisateurs non programmeurs : ergonomie, simplicité, messages compréhensibles et actions prévisibles.
- Pour les projets Napari et Qt, passer par `qtpy` afin de préserver la compatibilité entre PyQt et PySide.
- Préserver les contraintes du thread graphique et éviter les traitements longs qui bloquent l’interface.
- Les identifiants et les libellés d’interface sont en anglais par défaut ; respecter les mécanismes de traduction et les langues explicitement demandées.

## Organisation et nomenclature des tests

- Pour chaque correction de bug, proposer ou ajouter dans le périmètre autorisé un test de régression pertinent.
- Rechercher une bonne couverture des comportements utiles et des cas limites, sans multiplier les tests presque identiques ni recopier l’implémentation dans les assertions.
- Nommer les tests et scénarios en anglais, dans l’ordre des fonctions sources ; distinguer les cas indépendants et conserver ensemble les enchaînements réellement testés.
- Tenir compte du coût de construction des interfaces sans rendre les tests dépendants d’un état mutable partagé.
- Utiliser des données reproductibles et des graines aléatoires fixes lorsque nécessaire.

## Exécution des vérifications

- Par défaut, ne pas exécuter les tests sans demande ; exception permanente : toute modification d'algorithme (correction de bug, optimisation ou changement numérique) autorise et impose la compilation, les tests pertinents et une comparaison avant/après sans nouvelle confirmation.
- Figer l'état avant modification et les entrées, puis exécuter les mêmes scénarios sur deux copies isolées avec les mêmes options, dépendances et budgets de threads ; préserver les changements locaux et les références existantes.
- Si le correctif est déjà appliqué, reconstruire l'état précédent exact dans une copie isolée et documenter sa provenance ; ne pas comparer silencieusement une ancienne DLL comportant d'autres changements.
- Ajouter les régressions nécessaires et les exécuter après correction ; les exécuter aussi avant lorsqu'elles sont sûres, sans lancer un cas pouvant provoquer un accès mémoire invalide ou un autre effet dangereux dans l'ancienne version. Documenter toute exclusion.
- Produire un rapport de test fondé sur les résultats réellement observés. En cas de différences avant/après, ne détailler que les points différents, avec des tolérances numériques et des critères physiques adaptés au contexte ; conserver les résultats complets bruts pour la traçabilité.
- Adapter les comparaisons visuelles au phénomène : en SMLM, montrer des zooms sur les mêmes ROI et les mêmes pixels, avec les localisations et les formes ajustées avant/après ; comparer la covariance lorsque l'angle n'est pas identifiable.
- Mesurer aussi les ressources avant/après sur une charge représentative suffisamment longue, avec répétitions et ordre alterné. Définir avant l'analyse un seuil de pertinence pratique et tenir compte de la dispersion des mesures ; ne pas conclure sur un passage isolé.
- Afficher systématiquement les quantités mémoire avant/après (RSS et mémoire privée), même sans différence significative. Afficher les courbes comparatives détaillées uniquement si une différence dépasse les critères déclarés ; sinon conserver les mesures brutes accessibles et donner une brève conclusion. Signaler les résultats non concluants.
- Réserver les tests de performances et de charge aux données réelles fournies par l’utilisateur ; les données synthétiques servent aux régressions fonctionnelles, pas aux conclusions de performances. Conserver les programmes de charge séparés et locaux, notamment un C++ autonome pour la DLL, sans intégration aux tests courants. Pour le test massif sur cette machine, utiliser la pile entière en un seul appel et les processeurs disponibles, sans découpage en blocs ; vérifier explicitement les capacités mémoire et l’absence de troncature.
- Conserver les benchmarks et diagnostics personnels hors Git avec un suffixe `_local` et des exclusions ciblées ; ne pas les ajouter aux cibles partagées. Aucun ajout de dépendance ni changement automatique de référence n'est autorisé par cette exception.
- Ne jamais annoncer une réussite sans résultat effectivement observé ; signaler les échecs préexistants, les régressions, les exclusions et les vérifications impossibles.

- Respecter les configurations de compilation, de tests et d’analyse statique du projet et de GitHub Actions.
- Demander un accord avant une réécriture automatique qui dépasse les fichiers déjà autorisés.

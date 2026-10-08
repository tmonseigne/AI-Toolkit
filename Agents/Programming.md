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

- Ne jamais exécuter les tests : leur lancement reste à la charge de l’utilisateur, même après une modification autorisée, sauf nouvelle instruction explicite de sa part.
- Ne jamais déclarer que les tests réussissent tant que leur résultat n’a pas été communiqué ou observé dans le cadre d’une autorisation explicite d’exécution.
- Exécuter uniquement les contrôles pertinents de formatage ou de lint qui ne modifient pas de fichiers hors du périmètre autorisé.
- Demander un accord séparé avant un outil susceptible de réécrire automatiquement des fichiers lorsque cette réécriture n’est pas déjà explicitement autorisée.
- Respecter les configurations de compilation, de tests et d’analyse statique existantes, notamment celles de GitHub Actions.
- Signaler les vérifications qui n’ont pas été effectuées et leur raison.

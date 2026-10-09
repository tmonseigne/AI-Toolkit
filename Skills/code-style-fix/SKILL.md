---
name: code-style-fix
description: Corriger les conventions de code et l’organisation des fichiers Python et C++, y compris les tests existants et les régions, sur la branche courante ou le projet complet, sans audit fonctionnel ni ajout de tests.
---

# Correction des règles de code

Appliquer les corrections de style et d’organisation directement, en préservant le comportement du programme.
L’invocation de ce skill autorise les corrections et déplacements nécessaires dans le périmètre choisi ; annoncer les changements puis les réaliser sans demander une validation intermédiaire.
Ne pas proposer de mode `vérifie` ni se limiter à un rapport de problèmes.
Une sélection automatique du skill ne transforme pas une demande de lecture seule en autorisation de modification.

## Périmètre

- `$code-style-fix` : corriger les fichiers concernés par la branche courante.
- `$code-style-fix complet` : corriger l’ensemble du projet.

Dans les deux cas, identifier la racine du projet, lire les consignes applicables et inspecter l’état Git avant toute modification.
Préserver les modifications locales de l’utilisateur ; les intégrer aux corrections de style sans les annuler.
Ne pas créer de commit, changer de branche, modifier l’index ni effectuer de push.

### Branche courante

Utiliser la référence explicitement donnée par l’utilisateur, sinon la branche cible de la pull request lorsqu’elle est connue, puis la branche par défaut du dépôt déterminée à partir des références Git locales.
Ne pas prendre automatiquement la branche distante de suivi comme base : elle peut représenter la même branche de travail.
Comparer `HEAD` à leur ancêtre commun (`git merge-base`) et inclure les modifications indexées, non indexées et les nouveaux fichiers pertinents non ignorés.
Si la branche courante est elle-même la branche par défaut, comparer à sa référence distante locale lorsqu’elle existe ; sans référence exploitable, traiter uniquement les changements locaux et signaler cette limite.
Si plusieurs bases restent plausibles pour une branche de travail, demander seulement la référence manquante ; ne pas élargir silencieusement au projet complet.
Annoncer la base retenue et les fichiers concernés.

Corriger le contenu entier des fichiers sélectionnés lorsque leur cohérence le nécessite, pas seulement les lignes du diff.
Inclure les fichiers associés strictement nécessaires aux déplacements ou renommages, notamment imports, exports, configurations de compilation, références documentaires et fichiers de tests correspondants ; expliquer cette extension.

### Projet complet

Parcourir les fichiers du projet, y compris les nouveaux fichiers pertinents non ignorés.
Exclure les dépendances vendoriées, fichiers générés, environnements, caches, artefacts et sous-modules, sauf demande explicite les concernant.
Sans dépôt Git, le mode `complet` reste utilisable ; le périmètre branche exige une base identifiable.

## Règles à appliquer

Lire les `AGENTS.md` applicables et les configurations du projet, notamment `.editorconfig`, les réglages ReSharper et les règles Python disponibles.
Dans AI-Toolkit, utiliser [la variante programmation](../../Agents/Programming.md), [les règles Python](../../Config/PythonCodingRules.md) et [les règles ReSharper C++](../../Config/CodingRules.DotSettings) comme références partagées.
Pour une copie installée du skill, retrouver ces documents dans le dépôt AI-Toolkit accessible ou à l’emplacement fourni par l’utilisateur ; ne pas inventer leur contenu si les références sont indisponibles, et signaler les règles non vérifiées.
Les conventions explicites du projet priment sur ces références ; corriger les écarts à la règle retenue sans imposer une migration vers une autre convention.

- Corriger le nommage, l’indentation, les alignements, la largeur des lignes de code, les imports et la mise en forme selon les règles applicables.
- Uniformiser les régions, séparateurs, commentaires et docstrings concernés, en conservant les explications utiles et le sens des contrats documentés.
- Réorganiser les fichiers selon les responsabilités et la règle de classe principale par fichier ; conserver les regroupements autorisés pour les petites structures liées et les familles de variantes.
- Réorganiser le contenu : préambule, constantes, imports, classes, membres, accesseurs, opérations et entrées/sorties selon les conventions du projet ; ne pas imposer de régions artificielles aux petits fichiers.
- Réordonner les tests existants pour suivre les fonctions ou méthodes sources, regrouper les familles autorisées et préserver les fixtures ainsi que les scénarios cohérents.
- Pour les catalogues `.po` concernés, appliquer les règles Gettext de la référence Python ; ne pas relancer l’extraction ni réécrire les traductions sans lien avec une correction de convention.

## Limites des corrections

Préserver les API publiques, les formats, les noms imposés par les bibliothèques et la compatibilité avec les versions prises en charge.
Un renommage interne ou un déplacement doit mettre à jour toutes ses références, y compris les usages dynamiques identifiables ; conserver une façade d’import si elle est nécessaire à une API publique.
Vérifier les effets d’ordre avant de déplacer des déclarations, imports, initialisations, décorateurs, fixtures ou tests : le réordonnancement ne doit pas changer l’exécution ni créer de cycle d’import.
Ne pas déplacer mécaniquement une instruction dont les dépendances ou effets rendent le nouvel ordre incertain ; signaler l’exception conservée.

Ne pas ajouter de tests, assertions, scénarios ou fixtures pour étendre la couverture ; ne pas supprimer de contrôles existants.
Ne pas corriger de bug fonctionnel, modifier un algorithme, optimiser les performances ou changer les dépendances dans cette routine ; signaler les constats utiles dans la conversation pour un audit séparé.
Ne pas utiliser un formateur qui contredit les conventions retenues ou réécrit des fichiers hors du périmètre.

## Vérification et restitution

Contrôler le diff final et les références des fichiers déplacés ou renommés.
Effectuer les contrôles de syntaxe, de formatage et de lint pertinents avec les outils disponibles ; en Python, vérifier la syntaxe sans importer ni exécuter le code du projet.
Vérifier les espaces de fin de ligne avec `git diff --check` et contrôler aussi les nouveaux fichiers non suivis.
Ne pas lancer les tests sans instruction explicite distincte de l’utilisateur ; respecter les restrictions de compilation et de vérification du projet.
Ne pas présenter une validation de syntaxe comme une preuve d’équivalence du comportement.

Donner dans la conversation une synthèse courte des corrections, déplacements, vérifications et exceptions restantes, ainsi que la base Git retenue.
Ne pas ajouter de rapport au dépôt ; réserver les éventuels artefacts nécessaires aux dossiers ignorés `_output/` ou `_artifacts/`.

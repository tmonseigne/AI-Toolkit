---
name: code-inspection-fix
description: Corriger des diagnostics PyCharm, ReSharper ou Ruff. Examiner les alertes Python et C++ et documenter les faux positifs dans le rapport.
---

# Inspection et correction du code

Lancer l’analyse statique, corriger autant de diagnostics justifiés que possible et poursuivre leur revue jusqu’à résolution ou identification précise d’un blocage.
L’invocation autorise les corrections dans le périmètre choisi, y compris les corrections manuelles après examen ; annoncer les fichiers concernés et agir sans validation intermédiaire pour les décisions établies.
Une sélection automatique ne transforme pas une demande d’analyse seule en autorisation de modification.
Ne pas se limiter à un rapport ni appliquer aveuglément toutes les corrections proposées par l’outil.

## Périmètre et références

- `$code-inspection-fix` : traiter les fichiers de la branche courante ; sur la branche principale, traiter tout le projet.
- `$code-inspection-fix complet` : traiter l’ensemble du projet.

Lire les `AGENTS.md`, inspecter l’état Git et préserver les modifications locales.
Pour une branche de travail, choisir la base explicitement donnée, sinon la cible connue de la pull request, puis la branche par défaut du dépôt déterminée par les références locales.
Comparer à l’ancêtre commun avec cette base et inclure les modifications indexées, non indexées et les nouveaux fichiers pertinents non ignorés.
La branche distante de suivi n’est pas nécessairement la base ; demander la référence si elle reste ambiguë.
Exclure les dépendances vendoriées, fichiers générés, environnements, caches et sous-modules, sauf demande explicite.
Annoncer la base, le périmètre et les outils retenus ; ne pas créer de commit, changer de branche, modifier l’index ni effectuer de push.

Consulter [la variante programmation](../../Agents/Programming.md), [les règles Python](../../Config/PythonCodingRules.md) et [les réglages ReSharper C++](../../Config/CodingRules.DotSettings), ainsi que les configurations locales du projet.
Les conventions explicites du projet priment ; signaler les références inaccessibles.
Le formatage et l’organisation suivent les règles de style existantes ; la documentation et les traductions suivent leurs conventions, sans déclencher un audit documentaire ou une génération complète sans nécessité.

## Analyse statique

Privilégier les outils et profils déjà utilisés par le projet : inspections PyCharm et ReSharper, puis analyseurs ou linters complémentaires déjà disponibles lorsqu’ils apportent un contrôle pertinent.
En Python, compléter Ruff par Mypy lorsqu’il est disponible : Ruff contrôle les règles de lint, tandis que Mypy apporte une analyse des types. Respecter la configuration du projet, sa version Python minimale et l’environnement de ses dépendances ; signaler l’absence de Mypy sans l’installer automatiquement.
Si le projet ne configure pas Mypy, commencer par ses contrôles ordinaires ; examiner les fonctions non annotées et tester les contrôles plus stricts pertinents dans une configuration temporaire. Ne pas imposer globalement le mode strict ni une campagne d’annotations contraire aux conventions du projet.
Identifier la version, le profil, l’interpréteur Python ou la configuration C++ réellement employés ; une erreur de configuration peut produire des diagnostics trompeurs.
Vérifier les capacités et options de la version installée avant de lancer une commande ; distinguer l’analyse, le nettoyage de code et les corrections proposées uniquement par l’IDE.
Ne pas supposer qu’une commande d’inspection applique les corrections ni qu’un profil de nettoyage les couvre toutes.
En l’absence d’accès automatisable à l’IDE, utiliser un rapport exporté ou un outil disponible en indiquant la couverture réellement obtenue ; ne pas présenter un autre analyseur comme équivalent aux inspections JetBrains.
Ne pas installer d’outil ou de dépendance ni modifier les réglages globaux pour contourner une limite.

L’analyse peut nécessiter l’ensemble du projet pour résoudre les dépendances, mais limiter les corrections au périmètre annoncé et aux références strictement nécessaires.
Examiner les opérations implicites de l’outil, notamment builds, scripts, restauration de dépendances et écritures ; respecter les restrictions du projet avant de les lancer.
Conserver les rapports nécessaires dans un dossier ignoré `_output/` ou `_artifacts/`, avec les identifiants d’inspection et les emplacements utiles à la revue.

## Corrections et revue continue

Examiner chaque famille de diagnostics dans son contexte, puis appliquer en lots cohérents les corrections établies, automatiquement ou manuellement.
Choisir les correctifs disponibles qui respectent les conventions du projet, puis contrôler le diff ; les corrections manuelles restent possibles lorsqu’aucun correctif automatique adapté n’existe.
Corriger les fautes de frappe avérées dans la langue attendue, en préservant les termes scientifiques, unités, noms propres, identifiants imposés et clés publiques.
Pour les imports ou symboles dits inutilisés, examiner les réexports, usages dynamiques, décorateurs, enregistrements et effets de bord avant suppression.

Les suggestions de modernisation demandent une revue dans la continuité du skill, sans arrêt automatique ni accord supplémentaire lorsqu’elles sont justifiées dans le périmètre :

- Pour `const`, vérifier les mutations, alias, surcharges, déplacements et contrats de l’objet ; ne pas imposer une modification d’API publique.
- Pour les algorithmes ou ranges C++20, vérifier l’équivalence, les types, l’ordre d’évaluation, les durées de vie des vues, les copies et allocations ; conserver une boucle si elle reste plus claire ou adaptée.
- Pour les simplifications Python, vérifier les effets de bord, l’évaluation paresseuse, les exceptions, les types et la compatibilité avec la version minimale.
- Valider et appliquer sans confirmation supplémentaire les suggestions Python `Use ternary operator` (notamment Ruff `SIM108`) et `Use contextlib.suppress(...)` (notamment Ruff `SIM105`) après vérification locale de leur équivalence.
  Pour le ternaire, conserver la branche évaluée, son ordre d’évaluation et une longueur lisible ; pour `suppress`, conserver exactement les exceptions interceptées et les instructions protégées, sans étendre le bloc.
  Si cette équivalence n’est pas établie ou si la suggestion masque une intention métier ambiguë, poursuivre la revue ciblée au lieu de l’appliquer automatiquement.

Corriger un bug révélé par l’inspection lorsque le comportement attendu est établi ; ajouter un test de régression pertinent dans le périmètre autorisé conformément aux consignes de programmation.
Ne pas transformer une suggestion locale en refonte, migration de dépendances ou optimisation générale, ni annoncer un gain de performances sans mesure.

Quand une décision dépend d’une intention métier, d’un contrat ambigu ou d’une extension sensible du périmètre, exposer le cas concret, les conséquences et l’option recommandée, puis poser une question ciblée.
Regrouper les questions liées et poursuivre les corrections indépendantes pendant l’attente ; reprendre les cas concernés dès la réponse.
Ne pas considérer l’absence de réponse comme une autorisation ni terminer prématurément tant que la revue autorisée peut avancer.

## Faux positifs et profils

Pour qualifier une alerte de signature, de typage, de flot de contrôle, de compatibilité ou de présentation, suivre les [critères de qualification Python et C++](references/false-positive-review.md).
Consigner chaque qualification motivée dans les décisions du rapport et garder les conventions conservées consultables hors de sa vue initiale.

Distinguer une erreur réelle, une suggestion facultative, une convention volontaire et un faux positif démontré.
Vérifier d’abord la configuration, les sources et usages effectifs, les types et le contexte des frameworks, notamment Qt, Napari et Pytest.
Préférer une configuration de projet correcte, un dictionnaire de termes légitimes ou une exception locale et motivée à la désactivation générale d’une inspection.
Ne pas ajouter de suppression uniquement pour obtenir un rapport vide ; éviter les commentaires d’exception redondants lorsque le profil partagé exprime déjà la règle.

Les modifications ciblées du profil de projet ou du dictionnaire partagé nécessaires à un faux positif établi sont couvertes par l’invocation ; annoncer leur portée et les conserver partageables.
Pour réactiver des inspections désactivées, tester les familles pertinentes dans un profil temporaire, examiner leurs résultats, puis conserver seulement les réglages justifiés.
Ne pas réactiver en bloc toutes les inspections ni modifier un profil global ; demander une précision si la raison d’une désactivation reste inconnue et détermine la décision.

## Vérification et restitution

Relancer les inspections concernées après les corrections et examiner les diagnostics nouveaux ou persistants ; arrêter les répétitions quand aucun changement ni nouvel élément ne justifie une relance.
Contrôler les références et le diff, puis effectuer les vérifications pertinentes de syntaxe, de lint et de compilation autorisées par le projet.
Ne pas exécuter les tests sans instruction explicite de l’utilisateur ; indiquer les tests ajoutés ou recommandés et ceux qui restent à sa charge.
Une disparition du diagnostic ou un contrôle de syntaxe ne prouve pas à lui seul l’équivalence du comportement.

Résumer les corrections, les faux positifs établis, les changements de profil, les vérifications réellement effectuées et les cas restants avec leur raison.
Identifier les outils ou inspections inaccessibles et les décisions encore en attente ; ne pas annoncer une analyse complète lorsque sa couverture est partielle.

## Rapport HTML automatique

À chaque invocation, créer ou mettre à jour automatiquement le rapport autonome `_output/remaining-diagnostics.html` (ou le dossier d’artefacts ignoré déjà retenu), après les corrections et les inspections finales, sans nouvelle confirmation.
Utiliser le [modèle partagé](assets/inspection_report.html) et le [générateur](scripts/generate_inspection_report.py). Ils ne lancent aucun analyseur, test, import du projet ni installation : ils lisent les exports fournis et écrivent uniquement le rapport.
Le rapport propose recherche, filtres, tri, pagination, extraits des sources, qualification des alertes, export CSV et relecture locale exportable. La vue initiale conserve les cas à examiner ; les conventions et alertes masquées restent consultables dans les autres statuts.
Fournir uniquement les derniers exports pertinents : Ruff JSON, journaux Mypy et dossiers XML PyCharm (familles `Py*` / `Rest*` ; les autres familles pertinentes passent par `--diagnostics` après revue). Pour ReSharper ou un autre outil, utiliser `--diagnostics` avec une liste JSON normalisée comportant `tool`, `file`, `line`, `code`, `message` et `severity`.
Pour un périmètre de branche, transmettre `--scope-file` avec les chemins relatifs retenus, un par ligne. Le générateur limite sinon les diagnostics aux fichiers suivis ou nouveaux non ignorés du dépôt.
Consigner les décisions vérifiées dans un JSON `--decisions`, indexé par identifiant de diagnostic et contenant `status`, `reason` et éventuellement `evidence`. Le fichier voisin `.data.json` fournit les identifiants pour les passes suivantes ; préserver la clé de relecture d’un ancien rapport avec `--review-key` lors de sa migration ; ne pas réutiliser une qualification si le contrat a changé.
Décrire le périmètre, les versions, les vérifications et les limites réelles avec les options `--note`. Signaler les outils indisponibles, exports partiels ou anciens ; ne pas présenter un rapport vide comme une analyse réussie. Ne pas relancer la documentation ou les tests pour générer ce rapport.

Exemple à adapter aux exports de la passe :

```powershell
python -X utf8 <skill>/scripts/generate_inspection_report.py --root <depot> --ruff <ruff-final.json> --mypy <mypy-final.log> --pycharm <dossier-xml> --note "Tests non exécutés ; limites précisées dans les journaux."
```

Vérifier le JSON embarqué et la validité du script JavaScript lorsque les outils nécessaires sont disponibles, puis fournir le lien vers le rapport dans le bilan.

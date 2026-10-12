---
name: code-doc-fix
description: Corriger et uniformiser la documentation Python et les traductions Gettext d’un projet, notamment les en-têtes, docstrings, commentaires, régions et chaînes visibles, sur la branche courante ou le projet complet.
---

# Correction de la documentation du code

Uniformiser directement la documentation du projet sans modifier le comportement du programme.
L’invocation de ce skill autorise les corrections dans le périmètre choisi ; annoncer les changements puis les réaliser sans demander une validation intermédiaire.
Elle autorise également la compilation locale du site Sphinx, l’extraction Gettext et la mise à jour des catalogues de traduction associés selon le pipeline du projet.
Ne pas proposer de mode `vérifie` ni se limiter à un rapport de problèmes.
Une sélection automatique du skill ne transforme pas une demande de lecture seule en autorisation de modification.

## Règles à appliquer

Lire les `AGENTS.md` applicables et les configurations documentaires du projet, notamment `.editorconfig` et les réglages Sphinx/Gettext.
Utiliser [la variante programmation](../../Agents/Programming.md) pour la terminologie et l’uniformité des contrats, [les règles Python](../../Config/PythonCodingRules.md) pour les docstrings, commentaires, régions et catalogues PO, puis [les compléments documentaires](references/conventions.md) pour la revue sémantique.
Les conventions explicites du projet priment ; si une référence est inaccessible, signaler le lien manquant sans inventer son contenu.

## Périmètre

- `$code-doc-fix` : corriger les fichiers concernés par la branche courante ; si celle-ci est la branche principale du dépôt, corriger tout le projet.
- `$code-doc-fix complet` : corriger tout le projet, quelle que soit la branche courante.

Lire les consignes applicables et inspecter l’état Git avant de modifier les fichiers.
Identifier la branche principale à partir des références Git locales, notamment la branche par défaut du dépôt distant ; utiliser `main` ou `master` seulement lorsque les références du projet le confirment.
Sur une branche de travail, utiliser la référence donnée par l’utilisateur, sinon la cible connue de la pull request, puis la branche principale ; comparer depuis l’ancêtre commun avec `HEAD`.
Inclure les modifications indexées, non indexées et les nouveaux fichiers pertinents non ignorés ; corriger tout le contenu des fichiers sélectionnés lorsque leur cohérence le nécessite.
Si la base reste ambiguë, demander seulement la référence manquante ; ne pas choisir arbitrairement le périmètre complet.
En périmètre complet, inclure les fichiers du projet et les nouveaux fichiers pertinents non ignorés ; exclure les dépendances vendoriées, fichiers générés, environnements, caches, artefacts et sous-modules sauf demande explicite.
Annoncer le périmètre retenu et les fichiers concernés, puis corriger directement.
Préserver les modifications locales de l’utilisateur ; ne pas créer de commit, changer de branche, modifier l’index ni effectuer de push.

## Audit mécanique

Exécuter le script en lecture seule :

```powershell
python <skill-dir>/scripts/audit_documentation.py --root <repo> --scope branch
```

Passer `--base <référence>` avec la base retenue sur une branche de travail.
Utiliser `--scope all` pour `complet` et lorsque la branche courante est la branche principale.
Le script analyse les fichiers Python et PO suivis en mode `all` ; examiner également les nouveaux fichiers pertinents non ignorés et les éléments documentaires du périmètre qu’il ne couvre pas.

Le script fournit des indices, pas des décisions automatiques. Examiner chaque signalement dans son contexte et écarter les faux positifs justifiés, notamment les méthodes héritées et les fonctions volontairement triviales.

## Revue sémantique

Effectuer les passes dans cet ordre :

1. en-têtes de fichiers ;
2. docstrings des classes ;
3. docstrings des membres, méthodes, fonctions et tests ;
4. commentaires et régions ;
5. chaînes visibles par l'utilisateur ;
6. traductions Gettext.

Comparer les formulations entre fichiers voisins avant de corriger. Préserver les informations utiles, les notes et les TODO ; déplacer ces éléments vers la classe ou la fonction pertinente lorsqu'ils n'ont pas leur place dans l'en-tête.

Pour les méthodes héritées ou redéfinies dans une classe enfant, ne pas ajouter ni recopier la docstring de la classe mère lorsque son contrat reste applicable.
Laisser l’IDE et Sphinx restituer la documentation héritée, notamment pour des méthodes comme `to_compact_dict` et `update_from_compact_dict`, afin d’éviter les divergences lors d’une mise à jour du parent.
Avant de traiter un signalement de docstring absente, rechercher la documentation dans la hiérarchie et écarter le signalement si elle suffit.
Si l’implémentation enfant introduit une différence de contrat qui doit être documentée, décrire seulement cette particularité sans recopier la documentation commune ; préserver les explications spécifiques déjà utiles.

Limiter les changements à la documentation et aux traductions. Ne pas refactoriser le code ni modifier une API, un format ou une dépendance dans le cadre de cette routine.

## Traductions

Après les corrections des textes sources, exécuter le pipeline documentaire décrit ci-dessous pour actualiser les `msgid`, puis travailler à partir des catalogues obtenus.
Préserver les traductions actives et métadonnées existantes lors de la mise à jour ; les marqueurs `fuzzy` produits par la fusion doivent être examinés, pas supprimés automatiquement.

Appliquer les règles Gettext de la référence Python, notamment pour l’en-tête, les traductions identiques au texte source, les marqueurs `fuzzy` et la suppression complète des anciennes entrées `#~` après mise à jour.
Examiner les traductions existantes par rapport au sens actuel du `msgid` ; conserver celles qui sont exactes et corriger ou compléter celles qui ne le sont pas.
Un `msgstr` vide n’indique pas à lui seul si une traduction est nécessaire : décider d’après le texte source, la langue cible et les conventions du projet.
Vérifier aussi les pluriels, paramètres de substitution et références documentaires ; conserver les cibles Sphinx et les littéraux techniques.

## Pipeline Sphinx et Gettext

Examiner les commandes et configurations existantes, notamment les scripts documentaires, `conf.py` et la CI ; utiliser l’environnement et le pipeline prévus par le projet.
Annoncer les dossiers de sortie et les catalogues susceptibles d’être actualisés, y compris les fichiers générés nécessaires hors du périmètre initial des sources.

Pour les projets de l’utilisateur qui suivent cette organisation, le pipeline de référence s’exécute depuis la racine du dépôt, dans cet ordre :

```powershell
python.exe .\docs\tools\generate_api_files.py
python ./docs/tools/pytest_json_to_rst.py ./reports/test_report.json ./docs/reports/test_report.rst
cp ./reports/monitoring.html ./docs/reports/monitoring.html
python ./docs/tools/generate_test_reports_toc.py  # Mise à jour du fichier principal des rapports de tests
sphinx-build -b html -D language=fr docs docs/_build/html
sphinx-build -b html -D language=en docs docs/_build/html/en
sphinx-build -b gettext docs/ docs/_build/gettext
sphinx-intl update -p docs/_build/gettext -d docs/locale -l en -w 0
```

La génération des pages API et des rapports documentaires, la copie du graphique de suivi et la mise à jour de la table des matières font partie de l’autorisation documentaire ; examiner les scripts pour identifier les fichiers qu’ils produisent avant de les exécuter.
Utiliser les rapports existants sans relancer les tests ; si le JSON ou le graphique de suivi est absent, signaler l’étape impossible plutôt qu’inventer un rapport.
Conserver `-w 0` pour éviter le découpage automatique des lignes des catalogues PO.
Adapter les commandes seulement lorsque l’environnement ou les conventions explicites du projet le nécessitent.

1. Compiler localement le site Sphinx avec le builder HTML et les options de diagnostic du projet.
2. Lancer le builder Gettext pour générer les fichiers POT, puis la commande de mise à jour des PO utilisée par le projet, lorsqu’elle existe ; le builder Gettext seul ne met pas à jour les PO.
3. Examiner le diff des catalogues, corriger les traductions concernées et valider les entrées `fuzzy` selon les règles partagées.
4. Recompiler les versions traduites concernées après modification des catalogues pour vérifier leur intégration au site.

Conserver les avertissements visibles et relever le code de sortie de chaque étape ; un build réussi peut contenir des avertissements.
Corriger les erreurs documentaires directement liées aux fichiers autorisés, puis relancer les étapes affectées.
Signaler les problèmes hors périmètre, les dépendances absentes et les étapes impossibles à exécuter ; ne pas installer de composant ni masquer les diagnostics pour obtenir un résultat positif.
Si une étape échoue, ne pas utiliser ses sorties incomplètes pour actualiser les catalogues ; poursuivre uniquement les étapes indépendantes.
Utiliser les dossiers de génération ignorés prévus par le projet, sinon `_output/` ou `_artifacts/` ; cette compilation locale n’autorise aucune publication.

## Vérification finale

Après les corrections :

- relancer le script sur le même périmètre ;
- analyser tous les fichiers Python concernés avec `ast.parse` ;
- valider les catalogues PO concernés et leur compilation en mémoire lorsque Babel est disponible ;
- vérifier les résultats du pipeline Sphinx/Gettext et des versions traduites concernées ;
- exécuter `git diff --check` ;
- vérifier que seuls les fichiers annoncés ont changé ;
- signaler les contrôles non exécutés et les avertissements restant volontairement ouverts.

Ne pas lancer les tests sans instruction explicite distincte de l’utilisateur.
Présenter d’abord le résultat, puis le périmètre retenu, les fichiers modifiés, les validations et les exceptions conservées.
Pour le pipeline documentaire, indiquer les commandes exécutées, les étapes réussies ou échouées, ainsi que les erreurs et avertissements avec leurs fichiers et lignes lorsque disponibles ; distinguer les problèmes corrigés de ceux qui restent ouverts.
Réserver le bilan à la conversation et les éventuels artefacts nécessaires aux dossiers ignorés `_output/` ou `_artifacts/`.

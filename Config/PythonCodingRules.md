# Règles de code Python

Référence partageable pour les agents et les développeurs, fondée sur [PEP 8](https://peps.python.org/pep-0008/) et le [guide Python Google](https://google.github.io/styleguide/pyguide.html), avec les adaptations ci-dessous.
Les conventions explicites du projet priment ; ne pas renommer ou reformater tout un projet pour appliquer ce document.
Ce fichier décrit les règles ; il ne configure pas automatiquement PyCharm.
Les langues, autorisations et règles générales de travail restent définies dans les fichiers `AGENTS.md` du projet.

## Nommage et organisation

| Élément | Convention |
|---|---|
| Classes et exceptions | `PascalCase`, par exemple `BaseSettingType` et `InvalidDataError`. |
| Fonctions, méthodes, paramètres et variables | `snake_case`, par exemple `get_value` et `frame_index`. |
| Constantes globales ou de classe | `UPPER_SNAKE_CASE`, par exemple `MAX_FRAME_COUNT`, sans préfixe `k`. |
| Variables locales | `snake_case`, même lorsqu’elles ne sont pas réaffectées ; ne pas reprendre automatiquement le PascalCase des constantes locales C++. |
| Attributs internes | `_snake_case`, par exemple `self._value` ; les attributs publics restent sans préfixe. |
| Nouveaux modules et packages | Noms anglais courts en minuscules, avec des underscores au besoin ; conserver les noms de fichiers en PascalCase des projets qui les utilisent déjà. |
| Tests et identifiants de scénarios | Noms anglais descriptifs ; fonctions `test_...`, identifiants tels que `empty-data`. |

- Un fichier par classe principale ; les petites structures auxiliaires directement liées peuvent rester dans ce fichier lorsqu’un découpage supplémentaire n’apporte rien.
- Éviter les fichiers fourre-tout ; placer les utilitaires cohérents dans un module dédié.
- Placer les imports en tête : bibliothèque standard, bibliothèques tierces, puis projet, avec une ligne vide entre groupes ; éviter les imports `*` hors convention justifiée.
- Respecter les noms imposés par les API et les méthodes héritées, notamment Qt ; ne pas les renommer pour satisfaire un contrôle de style.

## Mise en forme

- Largeur maximale habituelle : 160 caractères dans les fichiers Python, commentaires et docstrings compris ; couper les lignes lorsque cela améliore la lecture, même avant cette limite.
- Dans les commentaires et docstrings, si la fin d’une ligne ne permet d’écrire que le début d’une nouvelle phrase, placer cette phrase sur la ligne suivante plutôt que la couper après quelques mots ; si elle dépasse elle-même la limite, la couper à une articulation logique.
- Toujours utiliser de vraies tabulations pour l’indentation, avec une largeur de 4 ; ne pas les remplacer par des groupes d’espaces. Ce choix est une adaptation explicite à PEP 8.
- Réserver les espaces à l’alignement complémentaire lorsque nécessaire ; ils ne doivent pas remplacer une tabulation d’indentation ni créer un mélange incohérent au début des blocs.
- Garder deux lignes vides entre déclarations au niveau du module et une entre méthodes, hors regroupement existant de fonctions triviales.
- Pour les expressions longues, préférer les parenthèses et les retours à la ligne lisibles aux continuations par antislash.
- Préférer les corps à une seule instruction sur une ligne lorsqu’ils sont courts et immédiatement compréhensibles, par exemple `if value is None: return` ou `for widget in widgets: widget.hide()`.
- Exception pour les `raise` : toujours placer la levée d’exception sur une ligne distincte de la condition, même si elle est courte ; éviter `if condition: raise ...` pour que la couverture par ligne distingue clairement la condition du chemin qui lève l’exception.
- Cette compacité est une adaptation locale : conserver plusieurs lignes pour les branches multiples, blocs imbriqués ou opérations complexes ; ne pas regrouper des instructions indépendantes avec des points-virgules.
- Pour une fonction triviale, une définition sur une ligne est acceptable si aucune documentation supplémentaire n’est nécessaire ; une docstring utile justifie un corps sur plusieurs lignes.
- La limite de 160 caractères ne s’applique pas aux phrases des fichiers Markdown et reStructuredText ni aux lignes des catalogues `.po`.

## Catalogues Gettext (`.po`)

- Conserver l’entrée d’en-tête `msgid ""` / `msgstr ""` et ses métadonnées utiles, notamment la langue, l’encodage et les règles de pluriel ; compléter les valeurs génériques plutôt que supprimer ce bloc.
- Supprimer les commentaires de modèle inutiles, mais préserver les mentions de copyright et de licence applicables ainsi que les commentaires utiles à la traduction.
- Retirer uniquement le marqueur `fuzzy` après correction et vérification de la traduction par rapport au `msgid`, y compris les pluriels et paramètres de substitution ; une simple modification ne suffit pas à valider l’entrée. Conserver les autres marqueurs, notamment `python-format` et `python-brace-format`.

## Régions et séparateurs

Employer des noms de régions français, stables et fonctionnels : initialisation, accesseurs, opérations métier, puis `Entrées / sorties` lorsque ces groupes existent.
Les petits fichiers n’ont pas besoin de régions artificielles.

```python
# ==================================================
# region Accesseurs
# ==================================================

# --------------------------------------------------
def get_value(self) -> int:
	"""Renvoie la valeur actuelle."""
	return self._value

# ==================================================
# endregion Accesseurs
# ==================================================
```

- Utiliser `# --------------------------------------------------` avant chaque déclaration de fonction ou méthode ; le placer avant le premier décorateur, jamais entre un décorateur et sa fonction.
- Éviter deux séparateurs consécutifs lorsque l’ouverture de région assure déjà cette séparation ; conserver les séparateurs existants jusqu’à une harmonisation demandée.
- Aligner les marqueurs de région sur le bloc concerné. Ne pas réindenter une fermeture artificiellement ; la dernière région d’une classe peut rester ouverte si le formateur déplacerait sa fermeture hors de la classe.

## Commentaires alignés

Lorsque des commentaires courts consécutifs forment un groupe visuel, conserver le marqueur `# .`, puis des tabulations et des espaces de complément pour aligner le texte dans l’éditeur.
Prendre comme référence le commentaire le plus à gauche et garder une largeur de tabulation de 4.
Cette convention ne concerne que la partie après `#` ; elle ne permet pas de mélanger l’indentation du code.
Limiter cet alignement aux groupes utiles, sans gonfler les commentaires ni dépasser inutilement 160 caractères.
Dans les commentaires ordinaires, ne pas ajouter les doubles accents graves propres à reStructuredText.

## Documentation

- Utiliser des docstrings reStructuredText compatibles avec PyCharm et Sphinx ; l’en-tête du module décrit son rôle sans dupliquer les classes et fonctions.
- Documenter les classes, fonctions, méthodes, attributs et champs de dataclasses avec des informations utiles et uniformes ; garder les docstrings des tests succinctes.
- Une docstring réellement monoligne reste entre triples guillemets sur une ligne.
- Pour plusieurs lignes, placer le premier texte après un retour à la ligne suivant les triples guillemets, puis aligner tout le contenu sur leur indentation ; séparer le résumé des détails par une ligne vide.
- Décrire chaque `:param:` présent ; utiliser `:return:` et `:rtype:` uniquement pour un résultat utile. Ne pas conserver une balise vide ou un type contradictoire avec la signature.
- Ne pas répéter les types déjà lisibles dans les annotations, sauf si le rendu documentaire ou une précision sur le contenu le nécessite.
- Préserver les explications, formules et TODO utiles ; ne pas recopier la documentation d’une méthode héritée si Sphinx la restitue correctement et que son contrat est inchangé.
- Employer les doubles accents graves pour les littéraux documentaires et les rôles Sphinx abrégés pour les références, par exemple ``:class:`~package.module.Class` ``.

```python
# --------------------------------------------------
def clamp_value(value: int, minimum: int, maximum: int) -> int:
	"""
	Ramène une valeur dans les bornes autorisées.

	:param value: Valeur à borner.
	:param minimum: Borne minimale.
	:param maximum: Borne maximale.
	:return: Valeur bornée.
	"""
	return min(max(value, minimum), maximum)
```

Cette présentation multiligne est compatible avec [PEP 257](https://peps.python.org/pep-0257/).
Le format reStructuredText est préféré au format de docstrings Google.

## Typage

- Annoter les paramètres et le retour des fonctions qui produisent une valeur ; ne pas annoter systématiquement `self` et `cls`.
- Annoter les attributs et variables dont le type n’est pas évident, notamment les collections vides et les frontières entre composants ; éviter les annotations répétitives comme `count: int = 0` sans besoin particulier.
- Préférer un type précis ou une interface adaptée à `Any` ; réserver `Any` aux valeurs réellement hétérogènes ou aux limites d’intégration qui le nécessitent.
- Employer la syntaxe de types compatible avec la version Python minimale du projet ; ne pas moderniser des annotations en cassant cette compatibilité.
- Par préférence visuelle, omettre `-> None` pour une fonction sans résultat utile, y compris lorsqu’elle emploie un `return` sans valeur ; l’ajouter si un contrat de bibliothèque, une surcharge ou un contrôle de typage explicitement retenu l’exige.
- Cette omission est un compromis de style : un retour non annoté peut être moins précisément contrôlé selon l’analyseur. Les annotations facilitent les contrôles statiques, mais n’imposent pas les types à l’exécution.

Les bénéfices et limites des annotations sont décrits dans le [guide de typage des bibliothèques Python](https://typing.python.org/en/latest/guides/libraries.html).

## Tests

- Un fichier de test par fichier source, ou un fichier commun pour une famille de classes très proches partageant le même contrat, comme les types et groupes de settings.
- Mutualiser les fixtures et contrôles communs ; paramétrer les classes ou scénarios indépendants avec `pytest.mark.parametrize`, pour que chaque cas soit identifiable et exécutable séparément.
- Ajouter des tests dédiés aux comportements propres à chaque variante ; le contrat commun ne suffit pas à couvrir ses particularités.
- Séparer les comportements distincts, cas valides, erreurs et entrées vides acceptées ; conserver ensemble les opérations dont l’enchaînement est précisément testé.
- Les boucles de préparation et de vérification d’un résultat collectif restent adaptées ; éviter les boucles qui cachent plusieurs scénarios indépendants dans un seul test.
- Organiser les tests dans l’ordre des fonctions ou méthodes sources ; placer constantes, fixtures et utilitaires dans un préambule et reprendre les régions pertinentes du code.
- Pour les interfaces coûteuses, réutiliser une construction dans un scénario cohérent sans partager d’état mutable entre tests indépendants.
- Initialiser les générateurs aléatoires avec une graine fixe par test ou pour un jeu de données commun inchangé ; éviter un générateur mutable partagé entre fichiers.
- Placer les rendus de confirmation visuelle en fin de fichier dans `Rendus spéciaux`, avec des données reproductibles adaptées au phénomène illustré.

L’autorisation de lancer les tests reste définie dans `AGENTS.md` ; ce document n’en modifie pas les permissions.

## Réglages PyCharm et compatibilité des outils

- Régler la marge Python à 160, activer les tabulations avec une largeur et un niveau d’indentation de 4, et désactiver leur conversion en espaces ; utiliser les inspections pour signaler les erreurs réelles plutôt que masquer toutes les alertes.
- L’inspection [PEP 8 coding style](https://www.jetbrains.com/help/inspectopedia/PyPep8.html) accepte une liste d’erreurs ignorées : autoriser de façon ciblée `E701` pour les corps courts sur une ligne et `W191` pour les tabulations imposées par cette convention. Ne pas ignorer les erreurs de mélange incohérent d’indentation comme `E101`.
- L’inspection [PEP 8 naming](https://www.jetbrains.com/help/inspectopedia/PyPep8Naming.html) est distincte ; conserver `snake_case` pour les fonctions et variables ordinaires, et les exceptions ciblées pour les méthodes héritées ou noms imposés.
- Un [profil d’inspection PyCharm](https://www.jetbrains.com/help/pycharm/code-inspection-profiles.html) peut être partagé ; préparer son export à partir des règles retenues plutôt qu’en inventer les réglages XML.
- Avant d’adopter un formateur automatique, vérifier qu’il respecte les corps sur une ligne, les régions, les commentaires alignés et l’indentation ; un formateur peut réécrire ces choix même si les inspections les tolèrent.

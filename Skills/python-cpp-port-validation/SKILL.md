---
name: python-cpp-port-validation
description: Valider un portage entre Python et C++. Comparer une référence et son portage sur les résultats numériques, le débit et la mémoire.
---

# Validation des portages Python et C++

Appliquer intégralement le [protocole de validation existant](../../Agents/Programming.md#exécution-des-vérifications) et les consignes du projet.
Si le chemin n’est pas accessible depuis une installation liée, résoudre le dossier source réel du skill.
Si le protocole reste indisponible, signaler la limite et poursuivre uniquement les vérifications indépendantes autorisées.

## Figer la comparaison

1. Identifier l’implémentation de référence, le portage, le point d’entrée réellement appelé et les contrats à préserver.
   Relever pour chacun la révision et les modifications locales, les options de construction, les versions des dépendances, la provenance du binaire chargé et les paramètres d’exécution.
   Dans PALM-Tracer, vérifier quelle DLL est chargée par Python et à quelle compilation elle correspond.
2. Réutiliser les cibles de compilation et les scénarios du projet.
   Isoler les deux états et leurs sorties, figer les mêmes entrées et budgets de threads, puis définir avant la comparaison ce qui constitue une différence significative.
   Si le point de comparaison est ambigu, préciser ce qui manque et avancer sur le contrat ou les contrôles indépendants.
3. Vérifier les conventions à la frontière Python/C++ qui affectent le résultat, en particulier unités, axes, indexation, formes, types et traitements des valeurs non finies.
   Lorsque le contrat le prévoit, inclure les cas vides, les limites de taille et les ordres de sortie non garantis.

## Comparer et restituer

- Vérifier les cas exacts et les invariants avant les écarts à tolérance.
  Utiliser les critères physiques ou numériques établis pour le projet et justifier chaque tolérance qui change l’interprétation.
  Si l’ordre n’est pas contractuel, comparer après un appariement justifié et signaler séparément les éléments non appariés.
- En SMLM, documenter le rayon et les unités de l’appariement lorsqu’il est pertinent, distinguer les détections manquantes ou excédentaires des écarts de localisation et suivre les règles du protocole pour les vues et les paramètres mal identifiables.
- Exécuter les régressions autorisées et mesurer débit, RSS et mémoire privée selon le protocole, avec répétitions alternées sur les données réelles représentatives fournies.
  En l’absence de pile réelle, poursuivre les régressions fonctionnelles et indiquer que la performance reste non mesurée.
- Restituer les états comparés, les écarts observés, les mesures, les limitations et les chemins des données brutes dans le dossier d’artefacts du projet.
  Distinguer les conclusions numériques des conclusions de performance et signaler précisément les scénarios non comparables.

Exemple de résultat attendu pour une localisation portée en C++ : nombre d’objets appariés et non appariés, écarts dans les unités physiques, seuils appliqués et provenance de la DLL mesurée.

Pour les métriques d’appariement SMLM, voir la [référence de l’EPFL](https://srm.epfl.ch/srm/metric.html).

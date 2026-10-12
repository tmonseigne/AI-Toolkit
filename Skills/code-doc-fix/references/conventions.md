# Conventions documentaires

Les règles partagées sont indiquées dans [SKILL.md](../SKILL.md#règles-à-appliquer).
Les points ci-dessous les complètent pour la correction documentaire, sans redéfinir les conventions de style ou d’installation.

## Cohérence documentaire

- Vérifier que les descriptions, paramètres, types et valeurs de retour correspondent au comportement réel ; signaler une ambiguïté plutôt qu’inventer un contrat.
- Comparer les définitions des mêmes concepts entre les fichiers sélectionnés et leurs API associées ; appliquer la terminologie commune sans effacer les différences réelles de rôle, d’unité ou de contrainte.
- Pour les attributs, champs de dataclasses et valeurs d’énumération, conserver une description courte lorsque cela suffit à expliquer leur rôle.
- Employer des formulations naturelles, directes et concrètes ; éviter les tournures stéréotypées qui donnent une impression de texte généré, les introductions convenues, les qualificatifs vagues et les phrases qui répètent la même idée sans apporter de précision.
- Supprimer les répétitions superflues au sein d’une explication et les paraphrases évidentes de la signature ou du code, en conservant les informations utiles sur le contrat, les unités, les contraintes et les limites. Ne pas chercher à varier les mots lorsqu’une même définition technique doit être réutilisée : la terminologie stable et les répétitions nécessaires à la compréhension restent prioritaires.
- Adapter la longueur à l’information à transmettre ; ne pas allonger une description pour uniformiser artificiellement le niveau de détail, ni reformuler un texte déjà clair et conforme uniquement pour changer son style.
- Un fragment de commentaire destiné à être rendu par un outil documentaire peut conserver les doubles accents graves nécessaires à ce rendu.

## Textes produits par le code

Avant de corriger un texte, examiner ses usages et les tests qui comparent une sortie exacte.
Actualiser les valeurs attendues directement concernées sans modifier le comportement testé ; annoncer ces fichiers associés dans le périmètre.
Si le texte sert aussi de clé, de protocole ou de format exploité par un autre composant, préserver ce contrat et signaler la limite.
Préserver les mécanismes de traduction et la langue cible des catalogues ; distinguer les chaînes d’exécution des explications documentaires.

## Traductions Gettext

Déduire les langues source et cible des configurations et métadonnées du projet ; ne pas imposer le couple français vers anglais à tous les catalogues.
Traduire le texte explicatif, y compris les connecteurs entre noms de paramètres, en préservant les noms techniques, formules et cibles de référence.
Ne pas confondre une différence de syntaxe Sphinx avec un changement de cible : une référence abrégée et un libellé explicite peuvent désigner le même objet.

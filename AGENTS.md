# Consignes générales pour les agents IA

## Communication et méthode

- Répondre en français, clairement et précisément, résultat d’abord, avec un détail adapté au besoin.
  Énoncer chaque information une seule fois ; éviter les reformulations, résumés, bilans redondants et structures inutilement complexes, tout en restant facile à parcourir.
- Réserver les bilans de travail et les explications des choix à la conversation, sauf demande de les documenter ; les fichiers partagés contiennent les informations durables utiles à leur usage.
- Examiner les consignes, sources et conventions avant de proposer ou d’agir ; réutiliser l’existant et limiter les changements à la demande, en les gardant faciles à relire.
  Éviter les outils et étapes sans utilité démontrée.
- Distinguer faits vérifiés, déductions et propositions ; ne jamais inventer de source, de donnée ou de résultat de vérification.
  Signaler les hypothèses, incertitudes, limites et vérifications impossibles.
- Garder un regard critique quelle que soit l’origine d’une idée ; sa présence dans le projet ou une réponse d’IA n’est pas une preuve de validité.
  Vérifier les affirmations décisives, rechercher ou demander les preuves manquantes et corriger explicitement ses erreurs.
  Ne pas approuver par complaisance ni contredire par principe ; expliquer les désaccords étayés avec respect et proposer une meilleure solution lorsqu’elle existe.
- Clarifier seulement ce qui empêche de choisir le périmètre ou le résultat ; poursuivre les opérations indépendantes autorisées.
  Pendant un travail prolongé, communiquer les découvertes et décisions utiles, sans statuts répétitifs.

## Autorisations et préservation

- Les lectures, recherches et vérifications utiles sans écriture sont autorisées.
  Une analyse, un diagnostic, une revue ou une proposition seule n’autorise pas d’écriture : fournir les constats et, si utile, un patch sans l’appliquer.
  Une demande explicite de modification autorise les changements directement nécessaires, après annonce des fichiers concernés et de la nature des changements, sans confirmation répétée.
- Demander un accord pour une extension sensible, une action destructive ou difficilement réversible, une action externe, une installation, une dépendance ou un réglage global non déjà autorisés.
  Publication, déploiement, push, pull request et message à un tiers exigent une instruction explicite couvrant l’action.
- Préserver les changements locaux, originaux et possibilités de retour arrière ; ne pas écraser, annuler ni inclure dans un commit les modifications de l’utilisateur sans autorisation.
  Ne pas enregistrer de secrets ou de données privées dans des fichiers destinés au partage.
- Sous Windows, après refus d’une lecture par le bac à sable, utiliser PowerShell hors bac à sable pour les seules consultations, recherches, énumérations ou inspections Git (`status`, `diff`, `log`, `show`, `ls-files`), sans redemander d’accord conversationnel.
  Toute création, écriture, redirection, suppression, installation, modification de l’index, de l’historique ou du système reste exclue de cette autorisation.
  En cas de doute sur le caractère strictement non modifiant, demander l’accord ; respecter les permissions de l’environnement et les mécanismes d’approbation, et signaler les refus bloquants avec leur raison.

## Langue et fichiers

- Français : échanges, commentaires, docstrings et documents.
  Anglais : identifiants de code, clés techniques, nouveaux fichiers et dossiers, libellés d’interface, erreurs, assertions, journaux et sorties destinées au développeur.
  Pour les textes d’interface et de diagnostic, respecter une exigence explicite de traduction ou une convention imposée par le projet.
  Vérifier aussi les noms ajoutés dans la branche, même déjà commités ; préférer un terme anglais ou une abréviation anglaise reconnue, comme `specification`.
- Exception : noms de fichiers, dossiers et propriétés du coffre personnel `Obsidian/` en français.
  Préserver partout les noms imposés par les outils, formats et standards, les noms propres, citations, titres officiels, métadonnées et documents sources dans leur langue d’origine, ainsi que les traductions existantes et la langue cible des catalogues.
  Ne pas renommer une API, une clé ou un fichier existant pour appliquer ces règles sans migration demandée et mise à jour des références.
- Dans les documents, utiliser des liens relatifs au fichier source lorsque source et cible sont dans AI-Toolkit ; préserver les ancres et vérifier la cible après modification.
  Ne pas modifier les liens vers l’extérieur pour appliquer cette règle.
- Respecter `.editorconfig` et `.gitattributes` : UTF-8, LF, saut final et absence d’espaces finaux ; CRLF pour les formats qui l’exigent, notamment `.bat` et `.cmd`.
  Ne pas rouvrir ce choix sans incompatibilité démontrée ou demande explicite.
- En Markdown/reStructuredText, privilégier une phrase entière par ligne source, des lignes vides entre paragraphes et des retours simples ; pas de largeur fixe, d’espaces finaux ou de `<br>` sans besoin explicite.
  Préserver la mise en forme validée.
- Créer uniquement les intermédiaires nécessaires dans `_output/` ou `_artifacts/`, exclus par `.gitignore` ; conserver les livrables durables dans les dossiers normaux.

## Mémoire et vérification

- Avant une décision d’architecture, un changement algorithmique, une reprise, un choix antérieur ou une question bibliographique PALM-Tracer/Synesthesia/toolkit/veille, consulter la note pertinente de [l’index](Obsidian/Index.md), sans rappel.
  Pour une correction locale évidente de syntaxe, style ou texte, cette lecture est facultative.
- Lire et appliquer les [consignes du coffre](Obsidian/AGENTS.md) pour sa consultation et son entretien ciblé, autorisé pendant l’essai.
  En cas d’accès impossible, signaler la limite et poursuivre les opérations indépendantes sans supposer le contenu manquant.
- Pour le code, lire et appliquer la [variante programmation](Agents/Programming.md) ; pour la bibliographie, la [variante bibliographie](Agents/Bibliography.md) dans le périmètre utile.
  Toute modification algorithmique impose le [protocole avant/après](Agents/Programming.md#exécution-des-vérifications), sans nouvelle confirmation.
- Respecter les restrictions de vérification : une autorisation d’édition n’autorise pas tous les outils.
  Distinguer lectures, créations de caches/rapports et réécritures ; demander l’accord si une réécriture dépasse le périmètre autorisé.
- Après modification, vérifier les éléments pertinents ; résumer les changements et leur raison, les contrôles réellement observés, les limites et les échecs, avec les liens vers les fichiers et artefacts utiles.
  Ne jamais annoncer une réussite non vérifiée.

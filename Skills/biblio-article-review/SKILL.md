---
name: biblio-article-review
description: Préparer une veille bibliographique et des fiches de lecture en français à partir de Zotero, notamment pour Synesthesia et PALM-Tracer. Utiliser pour repérer les nouveaux articles, éviter les doublons, résumer les preuves et analyser les articles disponibles ; la restauration PDF et les corrections de métadonnées relèvent des skills associés.
---

# Veille et fiches Zotero

## Périmètre

Travailler en lecture seule sur la bibliothèque Zotero locale de `C:\Users\tmonseigne\Zotero`. Préférer les requêtes GET de l'API locale `http://localhost:23119/api/` lorsque Zotero est ouvert. Elles ne demandent pas de clé. Si l'API ne répond pas, lire `zotero.sqlite` uniquement en mode lecture ; tenir compte des fichiers WAL/SHM et ne pas modifier la base de données. Sur demande explicite de l'utilisateur, un PDF nettoyé et validé peut remplacer sa pièce jointe locale, après conservation du scan original et de la version précédente ; cette autorisation ne couvre pas les autres pièces jointes ni les métadonnées. Ne demander ni identifiant ni mot de passe Zotero. L'utilisateur importe lui-même les `.bib` et ajoute les PDF.

Deux sujets sont suivis :

- **Synesthesia** : son ou musique vers couleur et forme ; régularités et variabilité entre personnes et types de synesthésie ; valeur des résultats pour des profils visuels personnalisables. Lire au besoin `C:\Git\Synesthesia\docs\specification.rst`, `docs\audit.md` et les fiches existantes pour éviter de refaire leur analyse ou d'en amplifier les conclusions.
- **PALM-Tracer / SMLM** : détection, localisation, analyse en temps réel, correction de dérive, reconstruction et rendu de super-résolution ; examiner précision, vitesse, mémoire et possibilités d'intégration.

## Ressources associées

Appliquer la [variante bibliographie](../../Agents/Bibliography.md).
Pour préparer les fichiers, consulter les [outils de veille](references/tool_usage.md), le [modèle de rapport](assets/watch_report.md), le [modèle de fiche](assets/article_review.md) et le [registre initial](assets/watch_registry.json).
Conserver les dossiers bibliographiques voisins pour accéder à l’inventaire partagé.

Pour un audit ou des corrections de notices, utiliser [biblio-metadata-audit](../biblio-metadata-audit/SKILL.md).
Pour restaurer un scan ou réduire son poids, utiliser [pdf-scan-restore](../pdf-scan-restore/SKILL.md) ou [pdf-size-optimize](../pdf-size-optimize/SKILL.md).
Une lecture d’article n’autorise pas le remplacement d’une pièce jointe.

## Veille

Au premier passage, inventorier les articles pertinents déjà présents dans Zotero et les fiches existantes. Ensuite, rechercher les publications nouvellement signalées ou mises à jour depuis le dernier passage avec un chevauchement de plusieurs semaines, puis effectuer périodiquement une recherche rétrospective plus large pour les indexations tardives et les prépublications devenues articles. Ne pas utiliser la seule date de publication comme critère d'exclusion.

Conserver un registre persistant dans le dossier de travail choisi pour la veille : DOI normalisé si disponible, sinon identifiant PubMed/arXiv ou combinaison titre-auteurs-année ; version ; dates de découverte et de dernier contrôle ; présence dans Zotero ; état de lecture (`titre`, `résumé`, `texte intégral`) ; décision et motif ; chemins des fiches produites. Relire un article connu si sa version, son statut ou un élément important change. Ne pas conclure à l'absence de nouveauté à partir de Zotero seul : rechercher aussi dans les sources scientifiques appropriées.

Dans le **rapport de veille en français**, donner pour chaque article retenu une mini-synthèse : référence et lien pérenne, sujet, question ou objectif, méthode, résultats principaux, limites, intérêt concret pour le projet et niveau de vérification. Quand seul le résumé est accessible, marquer explicitement « synthèse fondée uniquement sur le résumé » ; ne pas décrire comme vérifiés les méthodes, chiffres, figures ou conclusions qui n'y figurent pas. Séparer les résultats directement observés, les interprétations des auteurs et les implications proposées pour le logiciel. Signaler les articles déjà présents dans Zotero et fournir, pour les nouveaux, un `.bib` aux métadonnées vérifiées, sans y joindre de PDF.

## Fiches Markdown

Produire les fiches demandées pour les nouveaux articles et, lors d'un rattrapage, pour ceux du périmètre qui n'ont pas encore de fiche. Dédupliquer par identité d'article et par version avant de créer un fichier. Pour la veille existante, écrire dans `C:\Git\Veille Zotero` : seuls les rapports de veille et exports BibTeX sont des livrables suivis par Git à la racine, avec les fichiers de configuration du dépôt.
Ranger les fiches dans `_output/fiches/veille`, les traductions dans `_output/traductions`, le texte extrait dans `_output/pdf-text`, les rendus de pages dans `_output/pdf-pages` et les PDF produits dans `_output/pdf`, avec la nomenclature auteur-année-texte ou auteur-année-page01.
Conserver le registre persistant dans `_artifacts/registre-veille.json`, les audits, preuves et sauvegardes dans `_artifacts`, et les scripts propres aux campagnes dans `_artifacts/scripts`.
Les autres productions, notamment les comparaisons et rapports techniques, restent dans `_output` ou `_artifacts`.
Vérifier que `.gitignore` exclut entièrement `_output/` et `_artifacts/` ; ne jamais forcer leur ajout à Git.
Réutiliser le registre et les fichiers déplacés, adapter les chemins des outils ainsi que les liens relatifs des rapports et fiches, puis vérifier les cibles.
Lors d'un nettoyage demandé, supprimer les intermédiaires devenus inutiles ; préserver les sauvegardes nécessaires au retour arrière et les preuves encore utilisées.
Ne pas modifier les fiches de projet existantes à moins que l'utilisateur ne le demande.

Pour un texte intégral disponible :

1. **Fiche détaillée** (`<auteur>-<année>-fiche.md`), toujours : référence complète, accès et version, question, population ou données, protocole et comparateurs, analyses, résultats chiffrés importants avec pages/figures/tableaux, limites et biais, conclusions justifiées, pertinence pour Synesthesia ou PALM-Tracer, pistes d'implémentation distinctes des résultats publiés, questions ouvertes. S'inspirer du niveau de détail des fiches Synesthesia, sans en copier automatiquement les jugements ou les indicateurs bibliométriques. Inspecter les figures, tableaux et suppléments effectivement disponibles avant de déclarer une lecture complète.
2. **Traduction fidèle** (`<auteur>-<année>-traduction.md`), seulement si l'article est court (par défaut, moins de cinq pages de corps d'article, hors références et suppléments), si le texte intégral a été fourni localement par l'utilisateur, et si une traduction intégrale reste utile. Traduire les sections dans leur ordre, conserver équations, renvois, légendes et incertitudes ; signaler les passages illisibles et les choix terminologiques. Ne pas inventer le contenu des figures ni traduire de longues références bibliographiques sans intérêt. Si le texte est plus long, produire uniquement la fiche détaillée, sauf demande contraire.

Si le texte intégral manque, garder la mini-synthèse dans le rapport et marquer l'article « PDF à ajouter ». Ne pas fabriquer de fiche présentée comme lecture intégrale. Une fiche provisoire fondée sur le seul résumé est possible si l'utilisateur la demande explicitement ; son statut doit être visible dans le nom et l'en-tête.

## Qualité et traçabilité

Vérifier les métadonnées avec la page de l'éditeur, le DOI ou une source bibliographique fiable. Citer la source de chaque résultat important et les pages pour le texte intégral. Distinguer prépublication et publication évaluée, corrélation et causalité, groupe et individu, performances mesurées et promesses. Pour SMLM, relever le matériel, la taille des données, les conditions de mesure et la définition du « temps réel » avant de comparer les vitesses. Pour Synesthesia, préciser la modalité étudiée et la procédure de vérification des participants synesthètes quand elle est disponible. Ne pas attribuer de niveau de confiance scientifique à partir du seul résumé.

Informer clairement l'utilisateur de l'étendue du travail réalisé, des articles restant à lire et des PDF nécessaires. Une veille hebdomadaire n'implique pas de relire intégralement tous les articles à chaque passage.

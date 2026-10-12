---
name: biblio-metadata-audit
description: Auditer et normaliser sur demande les métadonnées Zotero, les identités des auteurs et les synthèses françaises, avec un rapport HTML triable et filtrable. Ne remplace pas la veille de nouvelles publications.
---

# Audit des métadonnées Zotero

Appliquer la [variante bibliographie](../../Agents/Bibliography.md), notamment les conventions des auteurs, des versions, des synthèses françaises et des validations déjà données.
Les preuves et autorisations restent propres à la bibliothèque concernée.

## Audit et rapport

Définir la bibliothèque et les champs concernés ; inventorier les valeurs actuelles en lecture seule avec les clés des notices.
Préférer les requêtes GET de l’API locale lorsque Zotero est ouvert ; les [outils d’audit](references/tool_usage.md) permettent aussi une lecture SQLite cohérente et la reprise d’un inventaire existant.

Contrôler les anomalies avec les articles, les notices éditeur et les sources bibliographiques.
Un score de titre ou une initiale compatible ne prouve pas l’identité ; les résultats automatiques sont des propositions.
Comparer DOI, titre, auteurs, année et version avant toute correction.
Conserver les absences légitimes et recontrôler les coordonnées des publications anticipées.

Produire le tableau avec le [modèle HTML](assets/metadata_report.html) : notice, champ, valeur actuelle, proposition, motif, sources et statut.
Vérifier le tri par chaque colonne, les filtres et les liens.
Actualiser le rapport permanent et le journal cumulatif sans perdre les décisions antérieures.

Les synthèses françaises reflètent le contenu effectivement lu.
Conserver leur provenance et leurs limites ; sauvegarder les résumés remplacés.
La recherche PubMed fournit des candidats, sans rédiger ou appliquer de synthèse.

## Corrections autorisées

Une demande d’audit seule n’autorise aucune correction de Zotero.
Préparer les corrections relues dans un [manifeste précis](assets/reviewed_changes.json), lié à la base et à une bibliothèque.
La validation du script s’effectue par défaut sur une copie temporaire.

Appliquer seulement dans le périmètre autorisé, en privilégiant une interface ou une API prise en charge.
Une écriture SQLite directe exige Zotero fermé, une sauvegarde cohérente, une validation sur copie et des contrôles d’intégrité et de clés étrangères.
Ne pas fermer l’application de force.
L’option `--commit` est réservée à cette application explicite ; ne pas sélectionner automatiquement tout le plan d’audit.
Préserver les pièces jointes, annotations et autres notices.

Après application, contrôler les dernières valeurs applicables du journal, rafraîchir l’inventaire puis retirer les anomalies effectivement résolues du rapport.
Un journal inachevé impose un diagnostic avant toute reprise ; ne pas réappliquer aveuglément le lot.

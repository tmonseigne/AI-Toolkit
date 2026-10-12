# Outils d’audit et suivi

Les trois scripts adaptent `audit_metadata.py`, `pubmed_metadata.py` et `apply_verified_metadata.py` de `Veille Zotero`.
Ils utilisent uniquement la bibliothèque standard Python.
Les décisions propres à des notices, chemins personnels, identifiants PubMed imposés et tailles de lots fixes ont été retirés.
Le [modèle HTML](../assets/metadata_report.html) conserve le tableau, les filtres et le tri du rapport original.

## Inventaire et propositions

```powershell
python -B Skills/biblio-metadata-audit/scripts/audit_metadata.py --database "C:/Users/tmonseigne/Zotero/zotero.sqlite" --library-id 1 --output "_output/metadata-audit" --offline
```

`--database` rafraîchit l’inventaire depuis SQLite en lecture seule, avec transaction cohérente et prise en compte du WAL.
Sans cette option, un `inventaire.json` existant est requis.
Choisir une seule bibliothèque : les clés des notices ne sont pas globalement uniques.
Le dossier de sortie doit être extérieur aux données Zotero.
Les fichiers de suivi sont remplacés en place ; conserver une copie préalable si nécessaire.

Sans `--offline`, le script interroge Crossref, puis DataCite en secours pour les DOI.
Le cache est lié au titre, au DOI, à la date et aux créateurs de la notice ; les anciennes entrées sans cette empreinte sont recontrôlées.
`--retry-unavailable` relance les recherches indisponibles.
Les rapprochements automatiques restent des propositions, y compris en présence d’un DOI : contrôler auteurs, année et version avant application.

```powershell
python -B Skills/biblio-metadata-audit/scripts/pubmed_metadata.py --output "_output/metadata-audit"
```

PubMed enrichit les notices signalées comme manquantes ; le fichier `sources-pubmed.json` est remplacé.
Préserver ses validations manuelles avant de relancer cet enrichissement.
Les correspondances restent candidates ; le script ne rédige pas de synthèse française.

## Conventions de suivi conservées

Pour une bibliothèque déjà auditée, réutiliser son dossier `audit-metadonnees` et ses fichiers existants.
Pour une nouvelle bibliothèque, choisir un dossier permanent extérieur à Zotero ; les noms de fichiers restent compatibles avec le suivi existant.

- `inventaire.json` : liste des notices, avec `key`, `library`, `type`, `fields` et `creators`.
- `sources.json`, `sources-pubmed.json` : caches et rapprochements, sans autorisation d’application.
- `corrections.json` : plan courant dans `issues`, avec `key`, `title`, `field`, `before`, `after`, `status`, `reason` et `source`.
- `rapport.html` : tableau courant, sans duplication datée.
- `auteurs-reference.json` : dictionnaire `hints`, indexé par `key|field` ; une piste contient `before`, `candidate`, `confidence`, `evidence` et `source`.
  Ajouter `reviewed: true` seulement après contrôle et validation ; les pistes restent attachées à la notice concernée.
- `champs-valides-sans-valeur.json` : liste d’absences contrôlées avec `key`, `field`, `before`, motif et provenance.
  Une absence provisoire utilise `recheck_due` et reste visible dans l’audit.
- `syntheses-fr.json` : dictionnaire clé de notice → synthèse française courante.
- `provenance-syntheses-fr.json` : dictionnaire clé → `title`, `basis`, `source`, `summary` et limites utiles.
- `modifications-appliquees.json` : journal cumulatif avant/après ; `historique/` : sauvegardes des lots.
  Un journal `prepared` interdit une reprise automatique : comparer la base, le lot et la sauvegarde.

Les preuves et validations réelles restent dans le dossier de la bibliothèque.
Elles ne sont pas livrées dans ce dépôt comme exemples génériques.

## Validation d’un lot sur copie

Compléter [reviewed_changes.json](../assets/reviewed_changes.json) dans le dossier de travail.
Renseigner le chemin de la base, `library_id` et une liste exacte de corrections.
Chaque correction contient `key`, `field`, `before`, `after`, `source` et `reason`.
Le champ `reviewed` indique que ce lot précis a été relu ; il ne remplace pas l’autorisation de l’utilisateur.

```powershell
python -B Skills/biblio-metadata-audit/scripts/apply_verified_metadata.py --database "C:/Users/tmonseigne/Zotero/zotero.sqlite" --output "_output/metadata-audit" --manifest "_output/reviewed_changes.json"
```

Sans `--commit`, seules une copie SQLite temporaire et ses transactions sont modifiées.
Le script contrôle les valeurs avant/après, les types, l’intégrité et les clés étrangères.
Pour `date`, `before` doit contenir la valeur SQLite brute, et `after` une année ou date ISO.
Pour `authors`, utiliser la liste complète avec `firstName`, `lastName`, `fieldMode` et `role` ; préserver les auteurs collectifs.

## Application explicitement autorisée

Ajouter `--commit` uniquement après une demande d’application couvrant le lot et la bibliothèque.
L’application directe est prévue sous Windows : elle refuse Zotero ouvert, conserve une sauvegarde cohérente, valide sur copie et écrit dans une transaction exclusive.
Elle préserve les créateurs partagés et refuse une conversion de type nécessitant une migration implicite.
Les pièces jointes et annotations restent hors périmètre.
Après application, régénérer l’audit avec `--database` ; le journal est interprété selon la dernière correction de chaque champ.
Préférer une interface ou une API prise en charge si disponible ; la structure interne SQLite peut évoluer et doit être vérifiée avant réutilisation.

## Vérification des outils

Les tests Python utilisent uniquement des bases et fichiers synthétiques ; aucune bibliothèque réelle n’est modifiée.

```powershell
python -B -X utf8 -m unittest discover -s Skills/biblio-metadata-audit/tests -v
```

Le test du modèle HTML nécessite Playwright et un navigateur Edge disponibles ; ne pas les installer automatiquement.
Il contrôle les huit colonnes dans les deux sens, les filtres combinés et l’activation au clavier.

```powershell
node Skills/biblio-metadata-audit/tests/test_metadata_report.cjs
```

Un chemin de module Playwright déjà présent peut être passé comme premier argument.

# Préparation de la veille

Les outils proviennent des scripts de préparation de `Veille Zotero` ; les clés de pièces jointes, dates de campagne et chemins personnels ont été retirés.
Les modèles reprennent le rapport, le registre et les fiches de ce dossier sans leurs données bibliographiques.

## Lecture et déduplication

Lire Zotero par l’API locale GET lorsque disponible ; sinon lire SQLite en mode `ro`, sans `immutable=1` lorsque des écritures WAL sont possibles.
Si la base est verrouillée et que l'API locale ne répond pas, un instantané `immutable=1` peut dépanner en lecture seule seulement après contrôle des journaux SQLite, de sa date et de la présence des notices recherchées ; signaler qu'il peut ignorer des écritures non consolidées.
L’outil [inventory](../../biblio-metadata-audit/scripts/audit_metadata.py) est partagé avec l’audit et permet d’inventorier une bibliothèque sans dupliquer les requêtes SQL.
Un audit local et des recherches DOI ne remplacent pas la recherche de nouveautés dans les sources scientifiques.

Le modèle [watch_registry.json](../assets/watch_registry.json) conserve le schéma existant.
Pour Veille Zotero, relire et actualiser `_artifacts/registre-veille.json`, exclu de Git.
Copier le modèle uniquement pour une nouvelle veille ; préserver les registres déjà remplis.
Les chemins `fiche` et `traduction` sont relatifs à la racine de la veille et pointent dans `_output/fiches` et `_output/traductions`.
Pour chaque entrée de `records`, conserver `id`, `zotero_key`, `title`, `year_or_date`, `doi`, `projects`, `version`, `discovered`, `last_checked`, `in_zotero`, `reading_state_this_veille`, `decision`, `reason` et `fiche`.
Employer `doi:<DOI normalisé en minuscules>` comme identité ; à défaut, un identifiant PubMed/arXiv ou un rapprochement titre-auteurs-année contrôlé.
Les valeurs de lecture existantes sont `titre`, `résumé` et `texte intégral`.
Conserver les versions et distinguer découverte, publication et dernier contrôle.

## Texte des PDF

`extract_pdf_text.py` requiert `pypdf`, déjà utilisé par les outils PDF du dépôt ; ne pas l’installer automatiquement.

```powershell
python -B Skills/biblio-article-review/scripts/extract_pdf_text.py --source "article.pdf" --output "_output/pdf-text/article-text.txt"
```

Le script conserve les repères de pages et refuse un fichier de sortie existant.
Il n’effectue ni OCR ni analyse des figures.
Une extraction vide ou imparfaite exige une inspection du PDF et, si nécessaire, les outils PDF ; elle ne prouve pas l’absence de contenu.

## Recueils de fiches

`split_reviews.py` adapte le découpage du recueil Synesthesia aux sections `### Fiche <numéro> : <titre>`.
Il conserve le contenu scientifique, produit un index et refuse d’écraser des fiches ou l’index existants.
Il ne crée pas de nouvelle analyse. Ses noms numériques sont des sorties de découpage provisoires ; renommer les fiches retenues selon la convention auteur-année-fiche avant intégration dans `_output/fiches/veille`, qui reste exclu de Git.

```powershell
python -B Skills/biblio-article-review/scripts/split_reviews.py --source "review-collection.md" --output "_output/reviews"
```

Les mises à jour datées de `update_outputs.py` et les lots particuliers de `prepare_reviewed_candidates.py` restent dans `_artifacts/scripts` de la veille : leur logique dépend de campagnes et de décisions précises.

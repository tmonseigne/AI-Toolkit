# Contrat des archives

Le script utilise uniquement la bibliothèque standard de Python 3.10 ou ultérieur.
Chaque fichier décrit une séance réelle ; les fichiers d’essai restent dans un autre dossier racine.
Les clés, identifiants, domaines et statuts sont en anglais ; les textes pédagogiques sont en français.

Exemple de structure à adapter, sans le sauvegarder comme séance réelle :

```json
{
  "schema_version": 1,
  "id": "2026-10-21-8a32c147",
  "created_at": "2026-10-21T08:00:00+00:00",
  "domain": "algorithms",
  "concept": "binary-search-invariant",
  "format": "counterexample",
  "level": 3,
  "status": "pending",
  "question": "Énoncé autonome, hypothèses et demande de justification.",
  "expected_answer": "Réponse justifiée et cas limite vérifiés avant présentation.",
  "rubric": ["0 : point essentiel absent ou faux.", "1 : intuition juste mais incomplète.", "2 : conclusion et justification suffisantes."],
  "answer": null,
  "score": null,
  "assisted": false,
  "hints": [],
  "feedback": null,
  "skip_reason": null,
  "duration_seconds": null
}
```

Créer un identifiant avec la date locale et huit caractères aléatoires, par exemple `uuid.uuid4().hex[:8]`, et un horodatage ISO 8601 avec fuseau.
`concept` est une étiquette anglaise stable désignant la notion, pas l’habillage de l’énoncé.
`format` est une étiquette anglaise libre, par exemple `trace`, `counterexample`, `tradeoff` ou `review`.
`duration_seconds` reste nul sauf mesure déclarée par l’utilisateur ; ce champ n’influence pas le niveau.
`assisted` et `hints` consignent les aides effectivement fournies.
Le barème comporte trois critères propres à l’exercice ; remplacer les descriptions génériques de cet exemple.

Pour terminer une séance, conserver ses champs pédagogiques initiaux et remplacer `status`, `answer`, `score`, `feedback` et les champs d’aide dans le fichier d’entrée.
Pour `completed`, `feedback` est obligatoire ; un score impose une réponse non vide.
Une révélation sans tentative utilise `answer: null`, `score: null` et une correction dans `feedback`.
Pour `skipped`, renseigner `skip_reason` et conserver `score: null`.
Une séance close est figée : une réécriture identique est acceptée, une modification est refusée pour préserver l’historique.
Si une erreur de correction est découverte après clôture, la signaler et demander une rectification explicite de cette archive en conservant sa version originale ; ne pas contourner le refus avec une fausse séance.

`context` expose les niveaux calculés, le domaine suggéré, les résumés récents et les séances en attente.
Les scores demeurent propres à chaque domaine ; ne pas calculer un classement général.
Une racine vide donne une première séance au niveau 3 et ne crée aucun fichier.
`save` valide l’entrée et les archives existantes avant écriture, refuse plusieurs séances en attente et produit la fiche Markdown correspondante.
Les écritures utilisent un remplacement atomique par fichier ; les deux fichiers JSON et Markdown ne constituent pas une transaction commune.
En cas d’interruption entre eux, relancer exactement le même `save` régénère la fiche depuis l’archive.
Éviter deux séances simultanées dans le même historique : ce petit outil local ne fournit pas de verrou interprocessus.

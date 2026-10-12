# Composition d'une transcription validée

Le compositeur utilise ReportLab, `pypdf` et Pillow pour les images raster.
Il reprend les cadres et styles des compositeurs Cajochen et Rosenzweig de Veille Zotero, sans leurs textes, tables numériques, numéros de figures ni placements imposés par paragraphe.
Réutiliser un environnement existant, sans installation implicite.

```text
python scripts/compose_article.py /path/to/transcription.json --output /path/to/_output/restored.pdf --scientific-font /path/to/STIXGeneral.ttf
```

Le fichier `source` est obligatoire et reste inchangé.
Le paramètre de police scientifique est nécessaire pour les caractères du texte brut qui ne sont pas représentables en Windows-1252.
Vérifier que la police choisie contient effectivement les glyphes demandés.
L'absence du caractère de remplacement dans le texte extrait ne suffit pas à vérifier les glyphes rendus.

```json
{
  "source": "original.pdf",
  "title": "Titre officiel de l'article",
  "authors": "Auteurs d'origine",
  "layout": {"columns": 2, "margin": 22, "gutter": 18},
  "expected_text": ["0.72", "Figure 1"],
  "blocks": [
    {"kind": "heading", "text": "Introduction"},
    {"kind": "paragraph", "text": "Texte transcrit et relu."},
    {"kind": "paragraph", "markup": "Expression contrôlée : x<super>2</super>."},
    {"kind": "figure", "path": "figure-1.pdf", "caption": "Figure 1. Légende d'origine."},
    {"kind": "table", "caption": "Table 1.", "rows": [["A", "B"], ["0.72", "4.78"]], "column_widths": [100, 100]},
    {"kind": "layout", "mode": "full"},
    {"kind": "figure", "path": "figure-2.png", "width": 500, "caption": "Figure 2."},
    {"kind": "layout", "mode": "columns"},
    {"kind": "reference", "text": "Référence dans sa langue d'origine."}
  ]
}
```

Les chemins des figures sont résolus depuis le JSON.
Les largeurs, marges et dimensions de page sont en points PDF ; `page_size` peut remplacer l'A4 par défaut.
Les types `frame_break` et `page_break` permettent de reprendre une disposition particulière.
Le passage `layout` commence une nouvelle page et utilise `full` ou `columns`.
Un titre pleine largeur en première page demande une page ou un agencement adapté : le helper ne reproduit pas automatiquement l'en-tête partiel des anciens scripts.

Une figure PDF doit avoir une seule page sans rotation ; elle est insérée comme contenu PDF vectoriel, sans rasterisation.
Une image complexe conservée du scan peut être fournie en PNG.
Le rapport HTML nécessite ses propres aperçus raster pour comparer les figures à leur source.
Le balisage `markup` est réservé aux fragments ReportLab explicitement contrôlés ; il ne représente pas du LaTeX et ne valide pas la formule.
Les tableaux complexes avec cellules fusionnées ou les équations nécessitent une préparation adaptée plutôt qu'une approximation silencieuse.
Donner les largeurs des colonnes des tableaux et vérifier les débordements ; conserver tous les chiffres tels qu'imprimés, y compris une anomalie source signalée.

Les figures sont gardées avec leur légende ; les tables longues peuvent se poursuivre avec répétition des lignes d'en-tête (`header_rows`, un par défaut).
Les espacements de blocs suivent le profil du skill ; contrôler les limites de cadres et les ruptures sur les rendus.
Les contrôles `expected_text` vérifient quelques valeurs sensibles mais ne remplacent pas une relecture exhaustive.

Pour le rapport partagé, résoudre le dossier réel de ce skill, puis utiliser `../pdf-size-optimize/scripts/compare_pdf.py`.
Les ressources communes restent dans le skill compagnon pour éviter deux copies divergentes du générateur et du template.
Avec les jonctions recommandées par le dépôt, les deux dossiers sources doivent rester présents et voisins ; conserver cette disposition lors d'une distribution de ces deux skills.

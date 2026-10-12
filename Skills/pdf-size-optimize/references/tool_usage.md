# Utilisation des helpers PDF

Exécuter les commandes depuis le dossier du skill, avec un Python fournissant `pypdf` et Pillow.
Le rapport nécessite aussi `pdftoppm` ; passer son chemin explicitement s'il n'est pas dans `PATH`.
Réutiliser un environnement disponible ; ne pas installer de dépendance sans autorisation.
Les sorties doivent être nouvelles ; les sources sont toujours conservées.

```text
python scripts/pdf_inventory.py /path/to/library --output /path/to/_output/inventory.json
python scripts/optimize_lossless.py /path/to/source.pdf --output /path/to/_output/candidate.pdf --manifest /path/to/_output/candidate.json
python scripts/remove_margin_line_numbers.py /path/to/source.pdf --output /path/to/_output/without-lines.pdf --manifest /path/to/_output/without-lines.json --font-size 4.732 --expected-count 444
python scripts/compare_pdf.py /path/to/comparison.json --output-dir /path/to/_output/review --pdftoppm /path/to/pdftoppm --dpi 130
```

Le retrait des numéros de marge est optionnel et distinct de la réduction du poids.
Mesurer d'abord la police, la position et la suite du document concerné ; les valeurs numériques de l'exemple sont propres à SMLMFlow.
Le script refuse une suite incomplète et contrôle le texte hors marge après réouverture.
La réécriture complète peut augmenter la taille du PDF : conserver alors le candidat allégé séparément.

Le paramètre `--max-image-bytes` borne les images sélectionnées pour la recompression, pas la mémoire totale du lecteur et des contrôles.
Traiter les documents séquentiellement si leur taille est importante.
L'inventaire mesure les flux présents dans les tables d'objets, y compris des objets éventuellement inutilisés ; ce ne sont ni des tailles de fichiers récupérables ni des preuves de visibilité sur une page.
Les erreurs d'inventaire sont consignées par fichier.
Les erreurs de transformation arrêtent le traitement ; une sortie partielle de rapport ne constitue pas une livraison validée.

Les tests synthétiques des deux skills sont regroupés dans `tests/test_pdf_tools.py`.
Ils couvrent le gain réel, les pixels et annotations, l'insertion vectorielle, le refus du chiffrement, les glyphes sans police adaptée et l'appariement après repagination.
Exécuter `python -B tests/test_pdf_tools.py /path/to/pdftoppm -v` pour inclure les contrôles de rendu ; sans Poppler, ces contrôles sont signalés comme ignorés.

## Manifeste du rapport

Tous les chemins relatifs sont résolus depuis le fichier JSON, et non depuis le répertoire courant.
Les numéros de pages commencent à un.

```json
{
  "title": "Comparaison des PDF",
  "summary": "Candidats proposés pour relecture.",
  "documents": [
    {
      "title": "Titre officiel de l'article",
      "before": "source.pdf",
      "after": "candidate.pdf",
      "notes": ["Limites et points à vérifier propres à cet article."],
      "pages": [[1, 1], [2, 3]],
      "images": [
        {
          "kind": "figure",
          "label": "Figure 1",
          "before": "figure-1-before.png",
          "after": "figure-1-after.png"
        }
      ]
    }
  ]
}
```

Omettre `pages` compare toutes les pages une à une, uniquement si les deux paginations sont identiques.
Pour une restauration, déclarer toutes les correspondances utiles, y compris plusieurs paires pour une page redistribuée ; la liste n'est pas une preuve d'exhaustivité.
Les types `figure`, `table` et `image` sont acceptés pour les comparaisons de ressources.
Préparer les recadrages à des échelles comparables ; le générateur n'invente pas leur correspondance.
Le dossier livré contient les copies des PDF, les PNG, `report.html` et `checks.json` ; conserver ce dossier complet pour que les liens restent utilisables.

Le rapport préserve les interactions du dernier comparatif complet `audit-poids-pdf/rapport_perte_negligeable.py` de Veille Zotero : filtres, tri, zoom, défilement, coches et export.
Le stockage des coches dépend du navigateur et de sa politique sur les fichiers locaux ; l'export JSON reste le moyen de conservation explicite.
Les empreintes des PDF et des images distinguent les versions relues.
Une faible erreur moyenne peut masquer la perte d'un petit détail : ne pas transformer les métriques du rendu en seuil d'acceptation automatique.

## Origine et périmètre

Les helpers reprennent les mécanismes d'`inventorier.py`, `tester_sans_perte.py`, `appliquer_sans_perte.py`, `verifier_rendus_sans_perte.py` et `rapport_perte_negligeable.py`.
Les chemins personnels, clés Zotero, exclusions d'articles, installations de pièces jointes et modifications de rapports existants ont été retirés.
Les scripts d'installation et de nettoyage restent propres à la bibliothèque : ils ne sont pas des prérequis de ces helpers.

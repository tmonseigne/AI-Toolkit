---
name: pdf-scan-restore
description: Restaurer un article PDF scanné avec OCR, recomposition du texte, des formules et des tableaux, reconstruction fidèle des figures et comparaison HTML avant/après.
---

# Restauration des PDF scannés

Restaurer à partir d'un original conservé et d'une transcription relue.
Séparer la mécanique de composition des textes, valeurs, relevés graphiques et décisions propres à l'article.

## Opération

1. Conserver le PDF source ; relever la disposition des colonnes, le contenu et les défauts avant de choisir la méthode de restauration.
2. Recomposer le texte, les formules, les tableaux et les légendes sans modifier les données ni traduire l’article ; contrôler les passages issus de l’OCR.
3. Redessiner les graphiques et schémas exploitables en vectoriel, en conservant échelles, marqueurs, incertitudes et styles ; garder une image source lorsque la fidélité du redessin est incertaine.
4. Nettoyer les photographies et images complexes sans supprimer de détail significatif ; identifier les approximations au lieu de les masquer.
5. Rendre et inspecter toutes les pages ; produire un HTML montrant chaque figure, schéma, photo et tableau avant/après, côte à côte à une échelle comparable.
6. Livrer le PDF et le rapport séparément de l’original ; remplacer une pièce jointe Zotero uniquement sur instruction explicite, avec sauvegarde et vérification.

Profil typographique par défaut : Times Roman 12 pt, interligne de 13,1 pt, STIX 12 pt, marges de 22 pt, gouttière de 18 pt, titres espacés de 14 pt avant et 4 pt après.
Les blocs de figures et tableaux ont 6 pt avant/après, supprimés aux limites des pages ou colonnes ; justifier dans le rapport tout écart typographique nécessité par le scan.

## Ressources réutilisables

- [scripts/compose_article.py](scripts/compose_article.py) : composition configurable en une ou deux colonnes, blocs de texte, légendes, tableaux, sauts de cadre et pages pleine largeur ; insertion des figures PDF en conservant le vectoriel.
- Lire [references/composition.md](references/composition.md) pour le format de transcription, les commandes et les limites.
- Pour le rendu et le rapport, utiliser les ressources communes du skill compagnon : [compare_pdf.py](../pdf-size-optimize/scripts/compare_pdf.py), [template HTML](../pdf-size-optimize/assets/comparison_report.html) et [format du manifeste](../pdf-size-optimize/references/tool_usage.md).
  Résoudre ces chemins depuis le dossier source réel du skill lorsque l'installation utilise une jonction.
  Les deux dossiers doivent rester voisins dans le dépôt ; une distribution isolée doit également fournir les ressources du compagnon et adapter ces liens.

Le compositeur ne réalise ni OCR ni relevé de courbes automatiquement.
Conserver dans le dossier de travail de l'article la transcription, les incertitudes, les recadrages et les figures préparées.
Les redessins d'histogrammes et de courbes des anciens scripts contiennent des coordonnées et des valeurs propres aux articles : les reprendre uniquement avec leurs sources, sans en faire des algorithmes génériques de récupération de données.

Ne pas supposer que page 3 de l'original correspond à page 3 de la restauration.
Déclarer l'appariement dans le manifeste HTML, et fournir séparément les comparaisons de toutes les figures et de tous les tableaux.
Vérifier les glyphes scientifiques, les indices, exposants, valeurs, références et ruptures de colonnes sur les rendus, même si l'extraction de texte passe.

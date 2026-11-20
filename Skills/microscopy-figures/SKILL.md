---
name: microscopy-figures
description: Créer ou auditer des figures de microscopie. Contrôler les échelles, canaux et transformations, puis préparer les exports scientifiques.
---

# Figures scientifiques de microscopie

Pour créer une figure à partir de données ou relire une figure existante, identifier le message de chaque panneau, les données sources et le type de sortie demandé.
Vérifier les consignes officielles de la revue si un format de soumission est demandé.

## Construire ou auditer les panneaux

- Retrouver les acquisitions, reconstructions, tables, ROI et réglages ayant produit chaque panneau.
  Conserver les originaux et consigner les recadrages, projections, rééchantillonnages, transformations d’intensité et exclusions qui affectent l’interprétation.
- Calculer les barres d’échelle à partir de la calibration correspondant aux pixels du panneau, après tout rééchantillonnage.
  Identifier les unités, les canaux et leur ordre, ainsi que la position des agrandissements dans la vue d’ensemble.
  Si la calibration manque, demander la donnée ou signaler la limite dans la figure et son bilan.
- Employer une normalisation commune lorsque les intensités doivent être comparées.
  Si des fenêtres différentes répondent à un besoin de lecture, les indiquer et limiter l’interprétation comparative.
  Distinguer les mesures faites sur les données de la mise en forme utilisée pour l’affichage.
- Pour les graphiques, indiquer les unités, la définition des incertitudes et ce que représente une observation.
  Vérifier les échelles et les légendes, ainsi que la lisibilité des groupes par leur forme ou leur annotation lorsque la couleur seule ne suffit pas.

## Exporter et vérifier

Réutiliser les scripts du projet ou produire la figure avec les outils de tracé déjà disponibles, par exemple Matplotlib et Seaborn.
Livrer si demandé le script, les paramètres et les références aux entrées permettant de régénérer la figure.
Garder texte, tracés et annotations en vectoriel lorsque le format le permet et préserver les images de microscopie en raster avec leur résolution documentée.
Inspecter chaque export à la taille de lecture prévue pour repérer les coupures, superpositions, barres d’échelle illisibles et divergences avec la légende.
En mode audit, restituer les constats par panneau, les informations manquantes et les corrections justifiées.

Exemple : pour deux reconstructions SMLM avant/après, reprendre la même ROI et une présentation comparable, puis documenter l’échelle utilisée et tout écart de normalisation.

[Checklists QUAREP-LiMi](https://quarep-limi.github.io/WG12_checklists_for_image_publishing/image_publishing/intro_image_publishing.html) · [Scientific Visualization](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-visualization/SKILL.md)

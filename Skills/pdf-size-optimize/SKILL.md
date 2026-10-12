---
name: pdf-size-optimize
description: Auditer et réduire le poids de PDF scientifiques en conservant leurs données et leur lisibilité, avec mesure des gains et comparaison visuelle avant/après.
---

# Réduction du poids des PDF

Auditer des fichiers PDF ou un dossier sans dépendre de Zotero.
Produire des candidats séparés et des preuves vérifiables ; ne jamais déduire une autorisation de remplacement d'une case cochée dans un rapport.

## Opération

1. Inventorier les PDF et repérer les images ou objets qui expliquent leur poids ; conserver les originaux.
2. Essayer d’abord les optimisations sans perte ; réserver une légère compression avec pertes au cas où elle est visuellement imperceptible.
3. Mesurer les tailles avant/après et les gains ; comparer les rendus, couleurs, petits détails et libellés, notamment les figures scientifiques.
4. Présenter les candidats dans un rapport HTML avec comparaisons visuelles et limites ; écarter les variantes qui altèrent une donnée ou un détail utile.
5. Livrer les versions retenues ; remplacer les fichiers de bibliothèque uniquement dans le périmètre autorisé, après sauvegarde et contrôle des fichiers effectivement installés.

Une conversion de courbes en images moins précises ou une modification des données ne constitue pas une optimisation acceptable.

## Contrôle du vectoriel

Inventorier les figures et distinguer primitives PDF, texte sélectionnable, photographies et schémas intégrés comme images matricielles.
Chercher d'abord si une version vectorielle de la même figure est déjà fournie dans le PDF ou les suppléments ; ne pas redessiner une simple vignette d'une figure déjà disponible en vectoriel.
La recompression des images ne vectorise pas les schémas.
Quand un schéma matriciel se prête à une reconstruction fidèle, appliquer le skill compagnon pdf-scan-restore sur une copie distincte : découper les panneaux si nécessaire, conserver les photographies en fond et replacer formes et textes dans des groupes vectoriels cohérents.
Comparer chaque panneau reconstruit à l'original à une échelle lisible et conserver les données scientifiques inchangées.
Ne pas convertir automatiquement les contours des pixels en chemins, ni reconstruire des courbes, mesures ou incertitudes sans données ou relevé suffisamment fiable.
Mesurer le poids de la version hybride ; la vectorisation n'est retenue dans la bibliothèque que si sa fidélité est vérifiée, même lorsqu'elle ne réduit pas davantage la taille.

## Numéros de ligne des prépublications

Quand un PDF de prépublication présente des numéros de ligne dans la marge, proposer leur retrait dans une copie distincte, en plus de l'optimisation de taille.
Identifier les numéros par leur position répétée dans la marge, leur style et leur suite page à page ; vérifier les cas atypiques avant de modifier le PDF.
Préserver les numéros des références bibliographiques, les appels de citation, les graduations de figures, les tableaux, les numéros de page et les annotations.
Retirer les objets textuels identifiés plutôt que masquer une bande entière de la page lorsque c'est possible.
Comparer ensuite le texte extrait et le rendu de toutes les pages concernées : seule la suite de numéros de ligne doit disparaître, et le reste du contenu, les figures, liens et annotations doivent rester exploitables.
Si la distinction n'est pas fiable ou si le PDF est signé, ne pas modifier le fichier ; documenter la limite dans le rapport.

## Ressources réutilisables

- [scripts/pdf_inventory.py](scripts/pdf_inventory.py) : tailles, empreintes, doublons exacts et flux embarqués ; aucune interrogation de base Zotero.
- [scripts/optimize_lossless.py](scripts/optimize_lossless.py) : recompression Flate RGB/gris 8 bits, avec choix du prédicteur PNG, égalité des pixels décodés et contrôle après réouverture.
- [scripts/remove_margin_line_numbers.py](scripts/remove_margin_line_numbers.py) : retrait ciblé d’une suite de numéros de marge après vérification de la position, de la police et de la continuité ; les références restent conservées.
- [scripts/compare_pdf.py](scripts/compare_pdf.py) et [assets/comparison_report.html](assets/comparison_report.html) : rendu Poppler, appariement explicite des pages, figures et tableaux, zoom, défilement synchronisé, filtres, inventaire triable, coches persistantes et export JSON.
- Lire [references/tool_usage.md](references/tool_usage.md) pour les commandes, le manifeste et les limites des contrôles.

Commencer par l'inventaire, puis traiter les fichiers retenus individuellement.
Un flux allégé ne garantit pas un PDF plus petit : le script sans perte ne livre un candidat que si le fichier complet gagne du poids.
Il refuse les PDF chiffrés ou signés et laisse les profils couleur complexes, les JPEG et les images autres que RGB/gris 8 bits hors de la recompression.
La manipulation des flux s'appuie sur des attributs internes de `pypdf` ; vérifier les helpers avec la version disponible avant un traitement en lot.

Le contrôle mécanique porte sur les images décodées et leurs attributs, les dimensions, la rotation, les contenus de page et le nombre d'annotations.
Il ne certifie pas à lui seul la conservation de toutes les fonctions interactives ni la fidélité visuelle ; examiner les annotations, liens, signets ou formulaires présents, et rendre toutes les pages concernées avec le même moteur.
Pour une compression avec pertes, définir avec l'utilisateur les critères acceptables et préparer une méthode adaptée aux images réelles ; aucun seuil PSNR ne vaut acceptation scientifique automatique.

Les helpers communs au skill de restauration restent ici comme source unique.
Ne pas recopier leur code dans un rapport propre à un article.

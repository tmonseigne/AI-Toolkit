---
name: epub-cleanup
description: Nettoyer et uniformiser des EPUB, leur XHTML, leurs styles, leurs métadonnées et leur navigation, en préservant le texte et le sens des mises en forme. Utiliser pour harmoniser un livre ou une série ; la traduction relève de epub-translate.
---

# Nettoyage et uniformisation des EPUB

Produire des EPUB cohérents, lisibles et contrôlés en conservant les originaux.
Le nettoyage porte sur la structure et la présentation ; il ne réécrit pas le récit.

## Définir la référence

- Examiner les consignes, les EPUB sources, les feuilles de style et les livres de référence fournis.
- Utiliser le [CSS maximal de référence](references/stylesheet.css) : conserver son catalogue de classes, même si le livre n’en utilise qu’une partie.
Réutiliser ces classes avant d’en créer une ; ajouter une classe seulement pour un besoin spécifique non couvert, notamment une police particulière.
Adapter les déclarations de polices aux fichiers réellement disponibles, sans embarquer de référence cassée.
- Reprendre les dernières décisions explicites de l’utilisateur ; un ancien script ou mémo peut contenir des choix dépassés.
- Mettre à jour la version EPUB existante. Une conversion vers EPUB 3 ne se réduit pas à changer le numéro de version du paquet.
- Travailler dans une nouvelle sortie, identifier les sources par empreinte SHA-256 et préserver les modifications existantes.
Ne pas exécuter directement un script de projet inconnu : certains créent des ressources ou réécrivent des EPUB dès leur import.

## Inventorier avant de transformer

Lire `META-INF/container.xml`, localiser le paquet OPF, puis inventorier manifeste, spine, navigation, documents, CSS, polices et images.
Suivre l’ordre de lecture du spine, et non le classement alphabétique des fichiers.
Relever les liens et leurs fragments, les identifiants, les notes, les illustrations et les styles significatifs.
Établir les états initiaux du texte et des ressources pour permettre une comparaison après transformation.

Pour les transformations, lire [references/cleanup.md](references/cleanup.md), notamment avant de retirer des classes, de supprimer des ressources ou de remplacer de petites images.

## Transformer sans perdre la sémantique

- Résoudre les styles utiles avant de supprimer les CSS ou les classes : emphase, voix particulière, centrage, exposants et signes peuvent porter du sens.
Ne pas présenter un résolveur de sélecteurs simples comme un moteur CSS complet.
- Employer un parseur XML avec résolution des entités externes désactivée et sans accès réseau pour modifier le XHTML.
Préserver texte, espaces entre éléments et queues de texte lors du retrait des enveloppes.
- Retirer par défaut les enveloppes `section`, après transfert de leurs informations utiles et de leurs cibles de liens.
Viser des `body` et `p` sans classe pour la narration courante ; réserver les classes aux fonctions particulières du CSS de référence.
Retirer les marqueurs de pagination imprimée, les sauts de page forcés et les résidus de conversion, puis nettoyer les `span`, `div` et `a` devenus inutiles ou vides.
- Regrouper par défaut les lignes d’un même titre dans un seul `h1`, `h2` ou autre niveau approprié, séparées par des `br`.
Ne pas fusionner des titres de sections distinctes.
- Ranger les ressources en sous-dossiers, renommer les fichiers avec des noms simples et explicites et corriger leurs références.
Réduire le `head` courant à un titre exact et un lien vers `styles/stylesheet.css`.
Les couvertures, cartes et illustrations pleine page suivent le [modèle XHTML dédié](references/full-page.xhtml), avec CSS intégré et métadonnée de couverture uniquement si pertinente.
- Appliquer les choix typographiques de la langue du livre et les exceptions de sa mise en scène.
Ne pas franciser la ponctuation d’un ouvrage resté dans une autre langue.
- Centraliser les règles communes à une série avec le CSS maximal, sans effacer les particularités justifiées de chaque tome.
Employer les modèles de [notes, séparateurs et glossaire](references/cleanup.md#notes-séparateurs-et-glossaire).
- Employer des `br` pour les blancs de transition ordinaires, en les ajustant au contexte narratif ; éviter les blancs artificiels à chaque paragraphe.
Les séparateurs, chansons, lettres et autres blocs spéciaux utilisent les marges de leur classe, sans `br` redondants.
- Appliquer par défaut la compression sans perte : ZIP et optimisations d’images disponibles préservant pixels et informations utiles.
Le réencodage avec perte reste soumis à une demande ou un accord.

## Contrôler et livrer

Comparer avant/après le texte de chaque document dans l’ordre de lecture, les liens, les ressources et la couverture des blocs.
Si une normalisation typographique est autorisée, expliciter ses substitutions ; ne pas masquer une perte de texte avec une normalisation trop large.
Vérifier séparément les éléments sémantiques que l’égalité du texte brut ne couvre pas.

Contrôler le ZIP, les documents XML, le manifeste, le spine, les références et les fragments.
Réserver EPUBCheck à la toute fin, sur les EPUB assemblés, s’il est disponible.
Corriger les diagnostics pertinents à cette étape, puis relancer seulement sur les livres corrigés jusqu’à résolution ou limite explicitée.
Pendant le travail, employer les contrôles ciblés de texte, XML et liens ; ne pas lancer EPUBCheck à chaque passe ou chapitre.
Conserver ses diagnostics complets dans les artefacts et ne restituer que le bilan utile ; distinguer les défauts préexistants lorsqu’ils sont établis.
Ne pas installer de validateur sans autorisation ; signaler son absence.
Un contrôle XML seul ne vaut pas validation EPUBCheck.

Inspecter un rendu avant/après sur des passages représentatifs : couverture, titres, dialogue, emphase, notes, séparateurs, illustrations et cas particuliers.
Préciser le moteur utilisé et les limites de compatibilité connues avec la liseuse cible.
Un aperçu de navigateur ou PDF ne suffit pas à prouver le rendu sur cette liseuse.
Ne générer un PDF que s’il fait partie des livrables demandés.

Livrer les EPUB assemblés et un bilan concis des changements, contrôles observés et points restant à vérifier.
Conserver les inventaires, empreintes et diagnostics détaillés dans les artefacts de travail ; ne pas livrer seulement un dossier décompressé.

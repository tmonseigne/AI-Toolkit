# Transformations et points de contrôle

## XHTML et CSS

Construire une correspondance entre les styles sources et leurs rôles avant de simplifier le balisage.
Une classe peut n’avoir aucun nom explicite mais appliquer une italique héritée indispensable.
Conserver les effets utiles avec des balises ou classes cohérentes avec la convention du livre.
Ne pas substituer systématiquement `strong` à `b`, ou `em` à `i`, lorsque leur sens diffère.

Lors du retrait d’un élément, préserver son texte, ses enfants et son texte de fin dans leur ordre exact.
Une ancre sans `href` peut être une cible de navigation : transférer son identifiant sans collision ou conserver un élément porteur.
Retirer par défaut les enveloppes `section`, sans retirer leur contenu.
Elles peuvent servir au découpage sémantique ou porter une langue, un rôle et une cible : transférer ces informations sur un élément approprié avant de les déballer.
Si une information ne peut pas être transférée sans ambiguïté, traiter ce cas explicitement au lieu de la perdre.
Conserver les identifiants utiles aux notes, à la navigation et aux renvois narratifs.

Regrouper numéro, sous-titre et autres lignes d’un même titre dans un seul élément du niveau approprié, avec des `br` :

```xml
<h1>Chapitre 1<br/>Un nouveau départ</h1>
```

Conserver les cibles et la correspondance avec les blocs sources fusionnés.
Préserver la hiérarchie des titres ; des sections distinctes restent des titres distincts.

Supprimer les numéros de page imprimée, leurs liens et identifiants, les marqueurs `pagebreak`, les listes de pages devenues sans objet et les sauts de page forcés hérités de la conversion.
La pagination de lecture est gérée par la liseuse.
Supprimer les références devenues orphelines et adapter les métadonnées de pagination concernées, sans toucher aux liens de notes ou de navigation.
Un renvoi rédigé « voir page… » doit être adapté vers une cible pertinente ou signalé, jamais laissé cassé.

En dernière passe, déballer les `span`, `div` et `a` sans rôle restant et retirer les éléments réellement vides.
Un élément contenant seulement une image, un `br`, un glyphe ou une cible encore utilisée n’est pas vide.
Préserver les espaces de jonction lors du déballage ; ne pas coller les mots autour d’une ancienne balise.

## CSS maximal et blancs narratifs

Employer [stylesheet.css](stylesheet.css) comme feuille commune unique des pages textuelles.
Ce fichier reprend le CSS maximal fourni par l’utilisateur ; les noms de classes existants sont conservés.
Garder l’ensemble des classes disponibles plutôt que réduire la feuille aux seules classes utilisées dans le livre.
Les déclarations `@font-face` du modèle indiquent des ressources propres aux livres d’origine : aucune police binaire n’est livrée avec le skill.
Dans chaque EPUB produit, conserver seulement les déclarations de polices dont les fichiers sont présents, adapter leurs chemins à `fonts/`, et respecter leurs droits d’incorporation.
Ajouter au besoin une police et une classe spécifiques sans réécrire les styles communs.

La narration ordinaire utilise `<body>` et `<p>` sans classe.
Remplacer les variantes de classes générées automatiquement par le style de base ou une classe du catalogue correspondant à un rôle réel.
La mise en forme particulière reste sur le bloc ou le fragment concerné.

Les blancs avant et après une transition narrative ordinaire sont portés par des `br`, sans paragraphes vides servant d’espaceurs.
Employer un blanc sobre comme point de départ, puis ajuster selon les transitions de lieu, de temps, de contexte ou de situation effectivement identifiables.
Ne pas reprendre mécaniquement les espacements sources : certains EPUB en ajoutent après presque chaque paragraphe, d’autres effacent les ruptures utiles.
En cas de doute sur une rupture, conserver le découpage narratif établi et signaler l’incertitude plutôt qu’inventer une transition.
Dans les chansons ou lettres, les `br` internes gardent leur fonction de retour à la ligne ; leurs marges extérieures, comme celles des séparateurs, relèvent de leur classe.
Éviter de cumuler ces marges et des séries de `br` avant ou après le bloc.

Simplifier les règles qui empêchent les réglages de lecture lorsque cela correspond au projet.
Évaluer les polices forcées, tailles fixes, marges et interlignages plutôt que d’appliquer une liste globale de propriétés interdites.
Préserver les besoins des pages de couverture, poèmes, tableaux et illustrations.
Éviter les fonds blancs et couleurs forcées sans nécessité, puis vérifier les éléments sensibles en thème sombre si le moteur le permet.

En français, appliquer les espaces insécables prévues par la convention retenue autour des guillemets et de la ponctuation double.
Traiter les nœuds textuels ; ne pas remplacer aveuglément des caractères dans les URL, attributs, CSS ou scripts.
Conserver les tirets et ponctuations expressives dont le rôle narratif a été vérifié.

## Dossiers, noms et en-têtes

Ranger les ressources selon une structure simple, par défaut relativement au dossier du paquet OPF :

```text
content.opf
nav.xhtml
cover.xhtml
chapter-01.xhtml
map-empire.xhtml
illustration-01.xhtml
notes.xhtml
styles/stylesheet.css
images/cover.jpg
images/map-empire.jpg
fonts/example.ttf
```

Les documents textuels peuvent rester à ce niveau ; images, styles et polices vont dans leurs sous-dossiers respectifs.
Employer des noms anglais, courts et explicites, avec numérotation de largeur cohérente et sans résidus d’outils ou identifiants opaques.
Renommer les documents et les ressources concernés dans le cadre du nettoyage, conserver la correspondance ancien/nouveau et réécrire OPF, spine, navigation, CSS, SVG, liens et fragments associés.
Ne pas modifier l’ordre du spine en fonction des nouveaux noms.

Le `head` d’une page textuelle courante contient uniquement un `title` exact, propre au livre et à la page, et la feuille commune :

```xml
<head>
  <title>Titre du livre — Chapitre 1 : Un nouveau départ</title>
  <link href="styles/stylesheet.css" type="text/css" rel="stylesheet"/>
</head>
```

Adapter le chemin relatif si le document se trouve dans un sous-dossier.
Corriger les titres faux, les noms de fichiers bruts et les intitulés trop génériques.
Retirer les métadonnées de conversion du `head`, les CSS secondaires et les reliquats JavaScript ; transférer auparavant les styles utiles vers la feuille commune.
Ne pas supprimer silencieusement une fonctionnalité interactive réelle : si elle existe, traiter son besoin explicitement.
Les métadonnées bibliographiques restent dans le paquet OPF et les attributs linguistiques utiles sur `html`.

Pour une couverture, carte ou illustration pleine page, utiliser [full-page.xhtml](full-page.xhtml), adapté du XHTML fourni et des cartes de référence.
Le CSS est intégré à cette page, sans lien vers la feuille commune.
Conserver la métadonnée `calibre:cover` pour la couverture seulement ; la retirer sur une carte ou une illustration.
Adapter le titre et le chemin de l’image ; renseigner les dimensions natives dans le `viewBox` et dans `image` pour préserver les proportions avec `xMidYMid meet`.
Ce modèle vise une image contenue dans la page, sans étirement ni découpe ; il ne transforme pas tout le livre en mise en page fixe.
Vérifier le rendu dans le lecteur disponible, notamment le support de la hauteur de page et du SVG.

## Notes, séparateurs et glossaire

Regrouper par défaut les notes dans `notes.xhtml`, à la fin du spine, pour éviter de les accumuler en fin de chaque chapitre.
Employer des identifiants uniques à l’échelle du fichier de notes et un lien aller-retour pour chaque appel.
Ce schéma reprend le principe observé dans les références Fils des brumes, avec les sémantiques EPUB 3 :

```xml
<!-- Dans chapter-01.xhtml ; déclarer xmlns:epub sur html. -->
<p>Texte avec un appel<sup><a href="notes.xhtml#note-01" id="note-ref-01" epub:type="noteref">(1)</a></sup>.</p>

<!-- Dans notes.xhtml, en fin de livre. -->
<aside id="note-01" epub:type="footnote">
  <p><a href="chapter-01.xhtml#note-ref-01">1</a> <i>Texte de la note.</i></p>
</aside>
```

Pour une même note appelée à plusieurs endroits, prévoir un retour distinct pour chaque appel.
Vérifier les deux sens de navigation après tout renommage.
Les annotations éditoriales ajoutées restent distinguables des notes de l’auteur.

Utiliser les classes du CSS pour les séparateurs, sans blancs `br` supplémentaires autour :

```xml
<div class="Separateur"><img src="images/separator.svg" height="15" alt="Séparateur"/></div>
<p class="Asterisque">***</p>
```

Adapter la hauteur à la fonction et aux proportions du motif ; distinguer un séparateur d’un symbole intégré à une réplique.
Conserver l’un ou l’autre type selon le livre et uniformiser ses occurrences équivalentes.

Une entrée de glossaire utilise un paragraphe `Glossaire`, le terme en gras puis sa définition :

```xml
<p class="Glossaire"><b>Terme</b> : définition du terme.</p>
```

Appliquer à ces exemples la langue et la typographie du livre produit.

## Images, symboles et ressources

Classer les petites images par fonction à l’aide de planches de contact : séparateur, glyphe, titre, diagramme ou illustration.
Les dimensions et le nom du fichier sont des indices, pas une preuve suffisante pour remplacer l’image.
Employer du texte pour un titre lisible si la transcription est vérifiée ; garder une trace de sa correspondance source.
Un SVG simple peut remplacer un motif géométrique après comparaison visuelle, en conservant forme, proportions et distinction plein/creux.
Ne pas redessiner approximativement une illustration complexe au titre du nettoyage.

Dédupliquer les ressources identiques par empreinte et réécrire toutes les références concernées.
Avant de retirer une ressource, examiner aussi les références CSS, SVG, OPF et de navigation.
Conserver les fichiers inconnus tant que leur inutilité n’est pas établie.
Appliquer par défaut la compression ZIP sans perte et les optimisations d’images sans perte accessibles avec les outils déjà disponibles.
Vérifier qu’elles conservent pixels décodés, dimensions, transparence, orientation et informations colorimétriques utiles ; ne pas retirer aveuglément des métadonnées nécessaires au rendu.
Conserver la variante la plus légère parmi celles dont l’équivalence est établie ; ne pas remplacer un fichier par une version plus lourde.
Ne pas installer un nouvel optimiseur sans autorisation ; signaler une optimisation indisponible sans bloquer le nettoyage.
Le réencodage avec perte, le redimensionnement et la réduction de palette altérant les pixels nécessitent une demande ou un accord.
Conserver le rapport d’aspect et contrôler le cadrage des couvertures et des pages pleine image.

## Paquet et validation

Lire les chemins relatifs depuis le document qui les porte, en tenant compte des fragments, de l’encodage des URL et de la casse.
Préserver les espaces de noms XML et les relations de couverture, de navigation et de notes.
Adapter manifeste, spine et navigation à la version EPUB réellement produite.
Pour EPUB 3, contrôler notamment la navigation et les propriétés des ressources concernées, ainsi que la date de modification du paquet.

Réassembler avec `mimetype` en première entrée ZIP, non compressée, contenant exactement `application/epub+zip`.
Vérifier l’intégrité ZIP, l’absence de doublons d’entrées et les cibles du paquet.
Ne pas extraire de chemins qui sortent du dossier de travail.

Conserver un relevé par livre : empreintes sources et sorties, transformations, documents modifiés, différences de texte attendues, intégrité des ressources, liens et diagnostics du validateur.
La préservation du texte brut ne prouve ni la conservation des emphases ni celle des illustrations ; les vérifier séparément.
Le nettoyage peut être considéré terminé seulement dans le périmètre effectivement contrôlé.
Lancer EPUBCheck une fois les transformations et l’assemblage achevés, puis uniquement après correction de ses diagnostics sur les livres concernés.
Ne pas le lancer systématiquement sur les originaux ou à chaque étape intermédiaire ; les contrôles ciblés assurent le suivi pendant le nettoyage.
Conserver les sorties détaillées sur disque et présenter les comptes et diagnostics actionnables plutôt que recopier les journaux complets dans la conversation.

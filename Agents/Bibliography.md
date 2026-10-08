# Variante bibliographie

Complète les [consignes générales](../AGENTS.md) pour la veille, les métadonnées Zotero et la restauration des articles.

## Rapports HTML

### Comparaison avant/après des PDF

- Montrer chaque figure, graphique, schéma, photographie, image et tableau avant et après restauration, côte à côte à une échelle comparable, avec les repères de page et de figure ; inclure aussi les éléments conservés sous forme raster, nettoyés ou compressés.
- Indiquer les corrections, approximations, écarts typographiques et points à vérifier ; enregistrer le rapport et ses images dans `_output/` ou `_artifacts/` et fournir le lien dans la conversation.

### Audit des métadonnées

- Présenter le rapport sous forme de tableau HTML, avec tri ascendant et descendant par clic sur chaque en-tête de colonne et des filtres pour retrouver rapidement les notices et les anomalies.
- Rendre visibles la notice concernée, le champ, la valeur actuelle, la correction proposée, le motif, les sources et le statut ; actualiser ce rapport dans `audit-metadonnees` plutôt que multiplier les versions.
- Vérifier le fonctionnement du tri, des filtres et des liens, puis fournir le lien du rapport dans la conversation.

## Langue, fidélité et conventions existantes

- Rédiger en français les synthèses, rapports, commentaires et documents de suivi nouvellement produits.
- Conserver dans leur langue d’origine les titres officiels, noms d’auteurs, citations, métadonnées et contenus des articles restaurés.
- Une reconstruction typographique ne constitue pas une traduction et ne doit pas modifier le sens scientifique.
- Pour les nouveaux scripts, identifiants, clés techniques et chemins, appliquer les noms anglais du socle ; les messages d’exécution restent en anglais.
- Les noms français des fichiers et dossiers de suivi cités ci-dessous sont des conventions existantes à préserver.
  Leur éventuelle migration vers des noms anglais nécessiterait une demande explicite et la mise à jour des scripts, chemins et liens.
- Les autorisations d’application et les validations restent propres à la bibliothèque concernée ; ce modèle n’autorise pas à modifier une nouvelle bibliothèque par simple réutilisation.

## Restauration des PDF scannés

- Conserver le format de l’article, notamment les deux colonnes lorsqu’elles sont présentes ; privilégier une typographie uniforme entre les documents restaurés.
- Employer Times Roman pour le texte, avec ses variantes grasses et italiques, et STIX pour les formules et les symboles scientifiques absents de Times Roman ; éviter DejaVu pour ces reconstructions.
- Préférer des marges étroites ; le nombre de pages peut varier légèrement pour garder une composition lisible.
- Reprendre la configuration approuvée : marges de 22 pt (environ 8 mm), gouttière de 18 pt entre colonnes, espace de 14 pt avant les titres de section et de 4 pt après.
- Utiliser par défaut Times Roman 12 pt avec un interligne de 13,1 pt et des formules STIX 12 pt, pour garder une typographie uniforme entre les documents ; ne modifier ces valeurs que si la taille ou les caractéristiques de la police du scan le justifient, et signaler cet écart dans le rapport de comparaison.
- Espacer les figures, tableaux et schémas de 6 pt avant et après le bloc complet, légende et notes comprises ; supprimer l’espace avant en tête de page ou de colonne et l’espace après en pied de page ou de colonne, sans le reporter sur la page suivante ni ajouter d’espaceur fixe.
- Lors de chaque nettoyage, recomposer uniformément la typographie du corps du texte, des citations, des légendes et des notes ; corriger les mots collés par l’OCR. Une simple suppression des fonds raster ne suffit pas si la composition existante varie entre paragraphes.
- Recomposer tous les tableaux, y compris ceux déjà partiellement retapés. Redessiner les schémas et graphiques en vectoriel avec des traits droits, des libellés uniformes, des axes et des marqueurs nets. Relever fidèlement les courbes, points, incertitudes, légendes, relations et échelles visibles ; ne pas inventer de données ni lisser une courbe de façon à modifier son sens. Comparer les figures redessinées au scan et signaler ici les éléments illisibles ou approximativement relevés.
- Les photographies et images trop complexes peuvent être conservées sous forme raster nettoyée ; les graphiques et schémas exploitables doivent être redessinés fidèlement. Une conversion des contours de pixels en polygones ne constitue pas une reconstruction propre. Employer des primitives géométriques pour les barres, repères, marqueurs, boîtes et flèches, et des lignes régulières pour les courbes relevées. Recomposer toutes les légendes ; conserver les pointillés, les symboles pleins ou vides, les incertitudes et les repères non numérotés. Vérifier visuellement chaque figure face au scan, au-delà du seul contrôle de présence d’images raster.
- Mettre les en-têtes de tableaux en gras sur fond `#edf0f3`, et alterner les lignes blanches et `#f7f8fa`. Adapter la taille des tableaux au document source pour préserver la lisibilité et la disposition.
- Garder les figures et tableaux près de leur emplacement d'origine, en autorisant de légers transferts de texte vers une colonne ou une page précédente lorsqu'elle a de la place.
- Lorsque l'original présente des marges excessives, des sauts initiaux inutiles ou une mise en page défectueuse, recomposer librement le contenu avec une taille normale (Times Roman 12 pt comme référence), sans chercher à préserver le nombre de pages ni à agrandir le texte pour remplir la page.
- Retirer les numéros de page propres au volume complet et les mentions de téléchargement, d'utilisateur, de date d'accès ou de copyright accessoires ; les métadonnées et références sont conservées dans Zotero. Préserver les références bibliographiques du corps de l'article.
- Retirer les poussières et les en-têtes répétitifs ; réunir le titre du support et la date uniquement sur la première page. Ne pas corriger silencieusement les données ou les formules : signaler dans la conversation les corrections et les valeurs douteuses.
- Ne pas ajouter de commentaires sur la reconstruction ni de notes éditoriales dans le PDF ; signaler les corrections et les points importants à vérifier dans la conversation.
- Conserver l'original et les versions produites séparément ; attendre une instruction explicite avant de remplacer la pièce jointe dans Zotero.

Pour les panneaux successifs partageant la même échelle, éviter les libellés d’axes répétés qui se chevauchent : un libellé commun au bas de chaque colonne peut suffire, en conservant les repères nécessaires. Reconnaître les titres de section même lorsque leur casse est mixte ; conserver leur style et leur espacement.

Avant tout redessin, identifier le type et le but de la figure : courbe continue, tirets ou pointillés, barres d’erreur, histogramme, signal temporel ou schéma. Les interruptions régulières appartiennent au style du tracé ; les lacunes isolées du scan ne doivent pas fragmenter une courbe continue. Ne pas relier des signaux indépendants ni transformer des barres d’erreur en courbes. Relever les points et contrôler chaque tracé face à l’original ; conserver l’image originale lorsque la fidélité du redessin est incertaine.

Pour alléger les pièces jointes, privilégier la compression sans perte. L’utilisateur accepte aussi une légère compression avec pertes lorsque la différence est imperceptible à l’œil et que le gain de poids est utile. Vérifier le rendu, les petits détails, les couleurs et les libellés avant application ; conserver un original accessible pour retour arrière. Cette tolérance concerne l’apparence des figures et ne permet pas de modifier les données ou le sens des graphiques.

## Mise en forme Markdown pour la veille

Dans les longs paragraphes des documents Markdown de veille, placer chaque phrase sur une nouvelle ligne dans le fichier source.
Utiliser un simple retour à la ligne, sans deux espaces finaux ni balise `<br>`, pour améliorer la lecture du Markdown brut sans imposer de saut de ligne dans le rendu.
Conserver les lignes vides entre les paragraphes et respecter cette mise en forme lors des prochaines mises à jour, notamment dans les documents déjà reformattés par l’utilisateur.

## Noms des auteurs

- Préférer le nom de famille et le prénom complet, dans les champs Zotero correspondants. Respecter les accents, traits d’union, particules et noms composés ; corriger les inversions ou mauvais découpages lorsque l’identité est confirmée.
- Un prénom complet suivi d’une ou plusieurs initiales de prénoms intermédiaires est conforme, par exemple « Charles M. ». Ne pas développer ces initiales systématiquement. Le prénom complet seul est également conforme : ne pas considérer l’absence d’une initiale intermédiaire comme un problème, notamment si elle est absente du site ou du profil officiel de l’auteur.
- Une initiale de premier prénom suivie d’un prénom complet est également conforme lorsqu’il s’agit de la forme sous laquelle l’auteur s’identifie officiellement. Conserver cette forme publiée ou d’usage, sans imposer un développement.
- Le prénom présent dans le texte de l’article est une source sûre pour son développement, dès lors que la notice et l’auteur correspondent bien. Appliquer les corrections ainsi vérifiées dans le périmètre autorisé, sans redemander une validation déjà donnée.
- Pour les initiales restantes, rechercher des prénoms plausibles dans les sources bibliographiques et les profils institutionnels. Présenter les pistes dans le motif du tableau, avec la source et le niveau de preuve. Une correspondance de domaine est un indice, pas une preuve d’identité à elle seule.
- Les identités et pistes explicitement validées par l’utilisateur sont acceptées. Conserver ces validations dans `audit-metadonnees/auteurs-reference.json` et les réutiliser après contrôle de l’identité ; ne pas les soumettre à nouveau comme problèmes.
- Une homonymie ou une initiale commune ne suffit pas à propager un prénom à toutes les notices. Respecter l’ordre des auteurs et conserver les auteurs collectifs. Une correction locale ne doit pas modifier involontairement un créateur partagé par d’autres notices.

## Champs bibliographiques et versions

- Inventorier les champs manquants et repérer les valeurs manifestement mal placées ou suspectes, notamment « Zotero », un identifiant à la place d’une revue, ou un nombre total de pages à la place de la pagination. Vérifier ces anomalies dans une source concordante ; une vérification exhaustive de chaque champ n’est pas nécessaire.
- Utiliser le titre officiel de la revue pour uniformiser les variantes de casse, de ponctuation ou d’article initial, par exemple « The ». Conserver le nom historique applicable à la publication. Ne pas remplacer aveuglément l’abréviation de la revue par son titre complet.
- Adapter les champs au type réel du document : article, communication, prépublication, chapitre, présentation ou support de formation. Une référence arXiv ne constitue pas un titre de revue.
- Comparer DOI, titre, auteurs, année et version avant application. Ne pas mélanger les métadonnées d’un préprint, d’une communication, d’une republication ou d’un article de revue. Si le lien fourni désigne une autre version et que le choix n’est pas établi, demander laquelle conserver ; respecter ensuite la décision de l’utilisateur.
- Distinguer publication en ligne et date du fascicule. Ne pas ajouter une précision de date non confirmée. Les dates brutes de Zotero peuvent combiner une composante de tri et le texte saisi : les valeurs `00` et les répétitions internes ne sont pas en elles-mêmes des erreurs.
- Ne pas inventer de DOI, ISSN, numéro, pagination ou abréviation. Un champ peut être légitimement vide, notamment pour un volume sans fascicule ou un article sans DOI indiqué. Enregistrer les absences contrôlées dans `champs-valides-sans-valeur.json` pour éviter de les signaler indéfiniment.
- Retirer uniquement les occurrences réellement répétées d’un identifiant ; conserver les ISSN papier et électronique distincts. Si un DOI éditeur renvoie à une notice générique ou supprimée chez Crossref, conserver la provenance et signaler cette particularité sans importer les métadonnées génériques.

- Distinguer la nature du contenu du support de publication : des recommandations de bonnes pratiques ou un guide publié dans une revue restent un article de revue, avec les coordonnées du fascicule. Ne passer au type rapport ou document autonome que si la version conservée correspond effectivement à ce support. Une abréviation de revue non confirmée peut rester vide lorsque le titre officiel est renseigné ; ce champ facultatif ne justifie pas un changement de type.

## Sources bibliographiques

Pour les identités douteuses et les champs manquants, PubMed, Crossref/DataCite, HAL et HAL-Inria, Elsevier/EM-Consulte/ScienceDirect, Nature et ResearchGate sont les sources utilisées pour cette bibliothèque.

Privilégier les notices éditeur, les textes des articles et les dépôts institutionnels. Sur ResearchGate, distinguer le texte de l’article déposé par ses auteurs des métadonnées agrégées. Consulter les profils officiels ou institutionnels pour confirmer les noms d’usage. Une absence dans PubMed ne remet pas en cause une identité confirmée par une autre source concordante.

Conserver une source explicite et un motif pour chaque correction ; ne pas présenter un rapprochement incertain comme une valeur vérifiée.

## Synthèses françaises

Le champ `abstractNote` contient une synthèse concise en français, y compris pour les notices dont le résumé original est déjà présent.

- Ne pas ajouter de préfixe tel que « Synthèse en français du résumé PubMed ».
- Utiliser les PDF joints comme sources pour les synthèses, notamment lorsque les sources bibliographiques externes ne fournissent pas de résumé. Vérifier que le titre, les auteurs et la version du PDF correspondent à la notice, puis lire la section Abstract ou Résumé. Pour une thèse, choisir le résumé général et non celui d’un article annexé. Si le document ne comporte pas de résumé distinct, synthétiser les passages pertinents effectivement lus (introduction, méthodes, résultats, conclusion, ou contenu d’un poster ou support pédagogique), en consignant cette base et ses limites dans la provenance. Ne pas laisser un résumé vide au seul motif qu’il n’existe pas de résumé original séparé.
- Reformuler fidèlement l’objectif, la méthode, les principaux résultats et les limites utiles à partir du contenu disponible. Ne pas déduire des résultats du titre ni présenter une hypothèse comme un résultat démontré.
- Lorsque le texte est incomplet ou dégradé, rechercher une source plus complète et propre. À défaut, limiter la synthèse au contenu accessible et signaler cette limite dans le texte. Une synthèse du plan ne doit pas inventer les résultats ou consignes du texte intégral.
- Replacer les conclusions dans la date et le contexte de l’article, notamment pour les revues médicales anciennes.
- Conserver la provenance dans `provenance-syntheses-fr.json` et le journal ; garder les textes remplacés dans une sauvegarde avant application. Utiliser `syntheses-fr.json` comme fichier courant unique des synthèses.

## Application et vérification

Appliquer les corrections autorisées en tenant compte des validations déjà données. Les écritures Zotero hors application se font uniquement lorsque Zotero est fermé, après sauvegarde et contrôle sur une copie, puis vérification des valeurs appliquées, de l’intégrité et des clés étrangères. Ne pas fermer de force l’application. Préserver les pièces jointes, annotations et autres données hors du périmètre de la correction.

Pour contrôler les mises à jour, comparer la bibliothèque actuelle aux dernières valeurs applicables du journal cumulatif. Tenir compte des corrections qui en remplacent d’autres et des notices supprimées ; ne pas comparer toutes les anciennes valeurs comme si elles devaient encore être présentes.

## Audit permanent et fichiers de suivi

Utiliser le dossier `audit-metadonnees`, sans date dans son nom ni dans le titre du rapport. Actualiser en place l’inventaire, le plan et le rapport HTML défini ci-dessus.

- Retirer les lignes résolues après vérification de leur application. Les manques restants ne signifient pas que la notice n’a jamais été traitée.
- Garder `modifications-appliquees.json` comme journal cumulatif des changements et sauvegardes. Conserver les sauvegardes horodatées dans `historique` pour permettre un retour en arrière.
- Archiver les anciens lots dans `historique` après application, sans multiplier les fichiers `lot-*.json` à la racine. Regrouper les alias et pistes dans `auteurs-reference.json`, et les preuves particulières dans `sources-complementaires.json`.
- Mettre à jour les scripts, chemins et liens lors d’une réorganisation. Vérifier que le tableau conserve le tri et que les sauvegardes restent accessibles.

## Langue des documents

Compléter un champ `language` vide par `en` ou `fr` lorsque le titre permet une déduction non ambiguë, conformément à la préférence explicite de l’utilisateur ; ne pas laisser ce champ vide uniquement faute de métadonnée externe. Consigner qu’il s’agit d’une déduction lorsqu’aucune source ne confirme la langue. Une langue explicitement indiquée dans le texte ou une source fiable prime sur le titre : PubMed peut afficher un titre traduit en anglais pour un article français. Ne pas modifier une langue déjà renseignée sur la seule base du titre.

## Publications anticipées et discussions

Une publication en ligne n’exclut pas, à elle seule, un volume ou un numéro d’article. Lorsque l’éditeur confirme une publication anticipée avant la Version of Record et que ces coordonnées ne sont pas attribuées, accepter temporairement leur absence et garder le statut et la source dans le suivi. Recontrôler les coordonnées et le statut lors des prochains audits ; ne pas considérer cette absence comme définitive.

Une mention bibliographique telle que « discussion 1643 » peut désigner les échanges publiés après une communication. Contrôler le texte avant de changer le type du document. Conserver la pagination numérique dans `pages` et, si nécessaire, déplacer l’indication de discussion et de séance dans `extra`, avec sa provenance.

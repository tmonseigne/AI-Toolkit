---
name: epub-translate
description: Traduire un EPUB ou une série en conservant la structure, les voix, les noms contextuels, les jeux de mots et la cohérence terminologique, avec suivi des textes et images restant à traiter. Utiliser pour une traduction éditoriale assemblée en EPUB, pas pour le seul nettoyage des styles.
---

# Traduction éditoriale des EPUB

Produire une traduction fidèle, lisible et cohérente dans la langue cible, puis l’assembler dans des EPUB contrôlés.
Traduire le texte fourni sans résumer, ajouter des actions ou lisser les singularités de voix.

## Préparer le corpus et les décisions

- Déterminer les langues source et cible à partir de la demande et des fichiers.
Identifier une éventuelle traduction intermédiaire ; ne pas annoncer une traduction directe de l’original si seul un texte relais est disponible.
- Examiner le paquet, le spine, la navigation, les documents textuels et les inscriptions dans les images.
Distinguer les limites d’un corpus lexical préparatoire du périmètre demandé pour la traduction : une postface absente du lexique n’est pas automatiquement exclue du livre à traduire.
- Préserver les EPUB sources et consigner leurs empreintes.
Travailler dans des fichiers cibles distincts avec des correspondances stables vers les documents et blocs sources.
- Lire les dernières consignes et les décisions validées avant les notes anciennes ou les scripts.
Ne pas importer les choix de noms, coupures, livrables ou automatisations d’un autre projet.

Tenir un lexique et un registre de décisions selon [references/translation.md](references/translation.md).
Réutiliser les registres existants plutôt que créer une seconde source concurrente.

## Traduire avec cohérence

Traduire dans l’ordre de lecture par unités de sens complètes, en gardant assez de contexte pour identifier locuteur, destinataire, registre et références.
Conserver l’emphase, les symboles, les indications de voix, les notes et les liens utiles.
Préserver les incohérences de la fiction ; signaler une incertitude plutôt que corriger silencieusement le récit ou valider ses affirmations scientifiques.

Respecter les noms validés tout en distinguant identité canonique, surnom, titre et appellation selon le locuteur.
Ne pas anticiper une révélation pour rendre toutes les occurrences uniformes.
Réutiliser une formulation de référence pour les règles ou textes récurrents, en vérifiant les différences contextuelles.

Préserver le mécanisme des jeux de mots et jeux de lettres, pas seulement le sens de chaque mot isolé.
Ne pas reconstruire des kana, une étymologie ou un original absent à partir d’une adaptation intermédiaire.
Lorsque l’incertitude empêche une solution fiable, consigner le bloc concerné et demander la décision nécessaire tout en poursuivant les passages indépendants.

Pour une cible française, suivre la convention validée des dialogues et citations, avec les espaces insécables adaptées.
Ne pas ajouter un tiret à chaque paragraphe de continuation d’une même réplique.
Les notes de traduction restent courtes, utiles, sans doublon ni révélation anticipée ; conserver d’abord les explications déjà présentes dans le récit.

## Traiter les images et suivre l’avancement

Inventorier les titres graphiques, encarts, bulles, cartes, règles et onomatopées utiles ; vérifier le périmètre demandé pour leur localisation.
Réemployer une traduction commune lorsque l’inscription se répète, sans supposer que les fonds ou les images sont interchangeables.
Pour une page essentiellement typographique, envisager une recomposition XHTML ou SVG ; pour une retouche raster, suivre le skill `imagegen` s’il est disponible.
Inspecter les résultats et tenir un registre des ressources remplacées.
Une transcription sans dessin est une alternative explicite, pas une image localisée équivalente.

Suivre séparément première passe, relecture littéraire, cohérence de série, images, assemblage et validation.
Ne pas déduire d’un nombre de fichiers un pourcentage de mots traduits.
Exclure les brouillons incomplets de l’assemblage ; ne pas écraser un document complet avec un ancien fragment.
À chaque reprise, confronter les registres aux fichiers réellement présents et consigner le prochain passage précis.
La création d’une programmation ou le recours à plusieurs agents dépend de la demande actuelle, pas de ce skill.

## Vérifier et livrer

Contrôler la couverture ordonnée des blocs sources, les fusions ou divisions explicites, les ajouts éditoriaux identifiés, les liens et les ressources.
Le comptage des paragraphes et la validité XML ne prouvent pas la fidélité d’une traduction : effectuer aussi une relecture source/cible.
Rechercher les passages restés dans la langue source, en distinguant les noms et expressions volontairement conservés.

Mettre à jour les métadonnées linguistiques, les titres de navigation et les textes alternatifs pertinents dans la langue cible.
Préserver les crédits et l’attribution de l’édition source ; ne pas attribuer la traduction nouvelle à son traducteur précédent.
Assembler des EPUB avec un paquet cohérent, contrôler les liens et inspecter un rendu représentatif.
Réserver EPUBCheck à la toute fin, sur les livrables assemblés, s’il est disponible ; corriger alors ses diagnostics pertinents et relancer seulement sur les EPUB corrigés.
Ne pas exécuter EPUBCheck à chaque chapitre, reprise ou assemblage provisoire ; pendant la traduction, utiliser les contrôles ciblés de XML, liens et couverture des blocs.
Conserver les diagnostics complets dans les artefacts et restituer un bilan concis.
Signaler les outils indisponibles et les contrôles non réalisés.
Ne produire de PDF ou d’autres formats que s’ils sont demandés.

Étiqueter clairement extrait, première passe, édition partielle ou version avec omissions.
Une validation technique réussie ne rend pas une traduction terminée tant que la relecture ou les images demandées restent à traiter.
Livrer les EPUB assemblés, les limites restantes et l’emplacement du suivi utile à la reprise.

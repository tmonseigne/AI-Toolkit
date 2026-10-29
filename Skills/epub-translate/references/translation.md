# Lexique, traçabilité et cas éditoriaux

## Registres de travail

Adapter ces informations aux fichiers existants ; les noms ci-dessous sont des propositions pour un nouveau projet.
Ne pas imposer une migration des registres déjà utilisés.

| Ressource | Informations utiles |
| --------- | ------------------- |
| `glossary.json` | `source`, `target`, `status`, `context`, `evidence` ; variantes, pluriels et capitalisation utiles. |
| `decisions.json` | Choix validés ou provisoires, origine de la décision et ancienne décision remplacée. |
| `reference_texts.json` | Textes récurrents, variantes contextualisées et documents concernés. |
| `progress.json` | Empreintes sources, état par document, images restantes, relecture et assemblage. |
| `image_registry.json` | Image source, document, mode de localisation, sortie et état de relecture. |
| `omissions.json` | Si nécessaire seulement : source, blocs, étendue, motif et marqueur visible. |
| `resume.md` | Prochaine unité à traduire, décisions en attente et liens vers les registres faisant autorité. |

Ces fichiers appartiennent au projet traduit, pas au dossier du skill.
Éviter d’y recopier inutilement de longs extraits du livre.
Conserver un statut provisoire tant qu’un choix n’est pas établi ; une occurrence calculée ne démontre pas une première apparition ou une identité.
Distinguer les préférences de l’utilisateur, les sources réellement consultées et les souvenirs rapportés.
Ne pas qualifier une forme d’« officielle » sur la seule base d’un souvenir.

## Noms, voix et jeux de mots

Une même personne peut être désignée différemment en narration, par un proche ou par un adversaire.
Ne pas effectuer de remplacement global avant d’avoir compris ces relations.
Préserver les variations de registre, archaïsmes, mélanges de langues et graphies expressives lorsqu’ils participent à la caractérisation.
En cas de traduction par langue relais, consigner qu’une adaptation repose sur cette édition, sans prétendre avoir vérifié l’original.

Pour un jeu de lettres ou de syllabes, identifier les unités effectivement jouées et vérifier leur chaîne, les comptes, les règles et les conséquences narratives.
Une traduction mot à mot peut détruire le mécanisme ; une adaptation locale peut aussi contredire l’illustration ou une règle ultérieure.
Selon le choix éditorial, conserver les unités originales vérifiées avec romanisation et glose, ou construire une adaptation cohérente en mettant à jour tous les éléments dépendants.
Ne jamais présenter des unités inventées depuis l’anglais comme le japonais original.
Lorsque les sources nécessaires manquent, garder la solution explicitement provisoire et localiser le problème dans le suivi.

Pour une note utile, conserver l’explication déjà donnée par le récit et ajouter seulement ce qui manque à la compréhension.
Créer une cible et un appel cohérents, avec retour ; en EPUB 3, utiliser les sémantiques `noteref` et `footnote` appropriées.
Identifier les notes ajoutées afin qu’elles ne soient pas prises pour des blocs narratifs sources dans les contrôles.

## Correspondance des blocs et omissions

Utiliser des identifiants stables ou une numérotation documentée des blocs sources, associée à l’empreinte du document.
Une possibilité est la numérotation en base 1 des enfants directs de `body` ; distinguer ce choix d’une numérotation de tous les descendants.
Consigner les fusions et divisions pour vérifier une couverture complète, sans chevauchement, dans l’ordre de lecture.
Un attribut tel que `data-source-blocks` peut tracer une fusion ; son interprétation doit être définie dans le projet.
Ne pas modifier les blocs sources pour faire artificiellement réussir la comparaison.

Si un passage ne peut pas être traité, ne pas le retirer silencieusement ni inventer un remplacement.
Délimiter le passage, indiquer la limite et poursuivre les parties indépendantes autorisées.
Une acceptation de coupures dans un projet précédent n’autorise pas celles d’un nouveau livre.
Si une omission est retenue, employer un marqueur visible dans le livre, enregistrer son étendue exacte et qualifier honnêtement l’édition livrée.
Ne pas reproduire le passage problématique dans le registre.

Vérifier les faits qui conditionnent une décision éditoriale dans les sources disponibles ; distinguer notamment un âge déclaré d’une estimation d’apparence.
Limiter une restriction à son périmètre réel au lieu d’écarter automatiquement tout le chapitre.

## Relecture et images

Comparer source et cible pour les négations, nombres, unités, relations entre personnages, locuteurs et liens logiques.
Vérifier que les choix terminologiques restent cohérents sans gommer les différences de contexte.
Une recherche automatique ou un inventaire de blocs complète cette relecture sans la remplacer.

Examiner les inscriptions des illustrations à une résolution lisible ; une planche de contact sert au repérage, pas à garantir la transcription.
Relire les textes après retouche et vérifier débordements, ordre des bulles, cadrage et cohérence avec le récit.
Conserver la correspondance entre original et ressource localisée, sans écraser les originaux.
Ne pas annoncer toutes les images traitées lorsqu’une page commune seulement a été recomposée.

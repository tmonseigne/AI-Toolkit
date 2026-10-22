# Skills

Lors de l’installation d’un skill, privilégier un lien vers son dossier dans ce dépôt : lien symbolique sous Unix/macOS, lien symbolique ou jonction de dossier sous Windows.
Le skill installé et sa source doivent ainsi utiliser les mêmes fichiers, pour que les modifications réalisées depuis l’un ou l’autre emplacement se répercutent directement.

- Pour une installation dans `.codex/skills/<skill>`, créer également `.codex/Config` et `.codex/Agents` comme liens vers les dossiers correspondants d’AI-Toolkit : les références `../../Config/...` et `../../Agents/...` restent ainsi utilisables sans modifier les Markdown. Avec un autre dossier d’installation, conserver cette disposition relative ou adapter les liens nécessaires.
- Vérifier que l’application découvre le skill et que ses scripts et références Markdown sont accessibles directement depuis l’emplacement installé.
- Conserver les règles de `Config/` et les consignes de `Agents/` comme sources uniques ; privilégier des liens symboliques pour les fichiers partagés plutôt que des copies ou des liens physiques, qui peuvent être dissociés lorsqu’un outil remplace le fichier.
- Si les liens ne fonctionnent pas dans l’environnement cible, signaler la limite et prévoir une synchronisation explicite des copies ; ne pas présenter une simple copie comme une installation liée. Ne pas écraser une installation existante sans examiner son contenu.

| Skill | Usage |
|---|---|
| [biblio-article-review](biblio-article-review/SKILL.md) | Veille, fiches, registre et extraction des textes. |
| [biblio-metadata-audit](biblio-metadata-audit/SKILL.md) | Métadonnées, synthèses et tableau HTML d’audit. |
| [code-doc-fix](code-doc-fix/SKILL.md) | Corrections de documentation Python et traductions ; branche ou projet complet. |
| [code-style-fix](code-style-fix/SKILL.md) | Corrections de style et d’organisation ; branche ou projet complet. |
| [code-inspection-fix](code-inspection-fix/SKILL.md) | Analyse statique, corrections et revue des faux positifs Python et C++ ; branche ou projet complet. |
| [daily-dev-test](daily-dev-test/SKILL.md) | Microtests de cinq minutes, correction du raisonnement et progression adaptée à l’historique local. |
| [pdf-scan-restore](pdf-scan-restore/SKILL.md) | OCR, recomposition et comparaison avant/après. |
| [pdf-size-optimize](pdf-size-optimize/SKILL.md) | Poids des PDF et contrôle visuel. |

Les rapports HTML font partie des livrables des opérations concernées, sans skill séparé.
Les deux skills PDF utilisent le générateur de comparaison et le template HTML de `pdf-size-optimize` comme source unique ; conserver leurs dossiers voisins dans le dépôt, y compris lorsque leur installation utilise des jonctions.
Les skills fournis par les plugins restent gérés par leurs plugins.

Les skills bibliographiques conservent leurs dossiers voisins : la veille réutilise l’inventaire de `biblio-metadata-audit`.
Leurs ressources sont décrites dans les références de chaque skill ; les données et validations propres aux bibliothèques restent dans leurs dossiers de travail.

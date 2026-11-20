---
name: obsidian-note-edit
description: Éditer une note Obsidian existante ou demandée. Préserver les propriétés, wikiliens, inclusions, ancres et conventions du coffre.
---

# Édition ciblée de notes Obsidian

Identifier le coffre, les fichiers désignés et le changement demandé.
Lire les consignes locales et le contenu des notes concernées avant d’écrire.
Dans AI-Toolkit, suivre les [consignes du coffre](../../Obsidian/AGENTS.md) et son [index](../../Obsidian/Index.md).
Depuis une installation par lien ou jonction, résoudre d’abord le dossier source réel du skill pour ces références.
Si plusieurs notes portent le même titre, utiliser le chemin et le contexte pour identifier la cible.

## Modifier la note

- Réutiliser la note qui fait référence sur le sujet et appliquer une modification ciblée.
  Préserver les propriétés YAML, leurs types, les alias, les identifiants de blocs, les inclusions et les pièces jointes qui servent déjà.
  Lorsqu’un titre de section doit changer, rechercher les liens qui ciblent son ancre et contrôler leur résolution dans le périmètre autorisé.
- Suivre la convention de liens du coffre.
  Lever une ambiguïté de nom avec un chemin dans le wikilien et vérifier le fichier, la section ou le bloc visé.
  Dans un tableau Markdown, échapper la barre verticale d’un wikilien avec libellé, par exemple `[[Projets/Projet|Projet]]` devient `[[Projets/Projet\|Projet]]` dans la cellule.
- Pour une inclusion, conserver le préfixe `!` et le fragment utile, puis vérifier le fichier référencé.
  Garder les propriétés facultatives lorsqu’elles servent réellement à la note ou à une vue existante.
- Pour une demande qui part d’une conversation à dépouiller, appliquer [conversation-to-vault](../conversation-to-vault/SKILL.md) pour décider des apports à conserver.
  Pour une édition directe, suivre le périmètre demandé et les consignes du coffre.
  Les renommages, déplacements, suppressions et modifications de réglages exigent une instruction couvrant l’action.

Après écriture, relire le diff et vérifier les cibles des liens modifiés, les propriétés affectées et le format de fichier.
Si un aperçu Obsidian est disponible et pertinent, vérifier le rendu des éléments modifiés.
Indiquer une cible ou une ancre non vérifiée si elle reste inaccessible.

[Aide Obsidian sur les liens internes](https://obsidian.md/help/links) · [Skill Obsidian Markdown](https://github.com/obsidianmd/obsidian-skills/tree/main/plugins/obsidian/skills/obsidian-markdown)

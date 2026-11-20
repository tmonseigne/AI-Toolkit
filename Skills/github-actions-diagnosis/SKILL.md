---
name: github-actions-diagnosis
description: Diagnostiquer un échec GitHub Actions. Relier le job et l’étape en échec aux journaux, au commit analysé et au diff local.
---

# Diagnostic GitHub Actions

Identifier l’exécution à partir du lien, du numéro de run ou de la PR fournie.
À défaut, partir de la PR associée à la branche et vérifier que l’exécution retenue correspond au commit et au workflow pertinents.
Utiliser un outil GitHub déjà connecté s’il expose les jobs et leurs journaux, ou le CLI `gh` déjà authentifié sur l’hôte concerné.
Si aucun accès ne permet de lire les journaux, exploiter les extraits fournis et identifier le job, la tentative et les lignes qui manquent pour conclure.

## Examiner l’échec

1. Relever le SHA effectivement testé, le workflow, le déclencheur, la tentative, le job, la cellule de matrice et l’étape en échec.
   Si GitHub teste un commit de fusion généré, identifier la révision et le workflow exécutés avant de comparer aux fichiers locaux.
2. Lire le journal de ce job et remonter au premier message qui explique l’échec.
   Distinguer une erreur de source, une étape de préparation, un artefact absent, une incompatibilité d’environnement et une annulation en cascade.
   Comparer, si disponible, la même étape sur une cellule voisine ou une exécution réussie comparable.
3. Rapprocher le message du YAML et du code de la révision testée.
   Pour les builds Python/C++, relever le runner, l’architecture, les versions de Python et du compilateur et la configuration de build lorsqu’ils éclairent l’écart.
   Si une reproduction locale est autorisée, reprendre la commande minimale pertinente du job et noter les différences de plateforme.

Avec le CLI, utiliser par exemple `gh run view RUN_ID --attempt ATTEMPT --json headSha,event,workflowName,jobs,url`, puis `gh run view --job JOB_ID --log-failed`.
Confirmer que le journal correspond au job exact, surtout si plusieurs cellules portent un nom voisin.
En l’absence de sortie pour l’étape fautive, consulter le journal complet du job ou qualifier la preuve manquante.

## Restituer et vérifier

Donner le lien du run, le job et l’étape concernés, puis citer le passage utile du journal sans reproduire de secrets.
Indiquer la cause observée ou l’hypothèse à confirmer, le correctif minimal et la vérification disponible.
Une demande de diagnostic autorise la lecture et l’analyse.
Appliquer un correctif local si la demande couvre la modification, et relancer un job distant, commenter, publier ou pousser uniquement sur instruction couvrant cette action.
Rapporter le statut du run réellement vérifié et le SHA correspondant.

[Référence de `gh run view`](https://cli.github.com/manual/gh_run_view)

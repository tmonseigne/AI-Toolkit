---
name: conversation-to-vault
description: Extraire d’un chat les décisions utiles au coffre. Retenir les justifications, contraintes et essais qui éclairent un choix futur.
---

# Mémoire décisionnelle d’une conversation

## Objectif et filtre d’admission

Le coffre doit réduire le travail à refaire et les mauvaises orientations.
Avant toute intégration ou copie de preuve, répondre concrètement : **quelle prochaine décision cette information accélère-t-elle, quel essai évite-t-elle ou quelle erreur prévient-elle ?**
Si le bénéfice est vague, ne rien conserver.

Retenir seulement un apport significatif de l’un de ces types :
- une expérience déjà menée, avec hypothèse, conditions, résultats, limites et raison du choix final, pour éviter de la refaire sans élément nouveau ;
- une contrainte ou préférence durable non évidente, susceptible d’écarter une direction inadaptée ;
- une justification utile : alternatives réellement examinées, compromis déterminants ou connaissance coûteuse à reconstruire dans les sources du projet.

Une demande explicite, une modification d’architecture ou un résultat vérifié ne suffisent pas à rendre l’information utile au coffre.
Exclure par défaut journaux de correctifs, listes de fichiers ou fonctionnalités, choix isolés, état d’avancement, inventaire de tests et comportement directement retrouvable dans le code, les tests, Git ou la documentation.
Une justification banale ou facilement déductible ne justifie pas une note supplémentaire.
Ne pas inventer un « pourquoi » absent de la conversation ; distinguer justification exprimée, preuve observée et hypothèse non validée.

| Cas | Filtre à appliquer |
|---|---|
| Correctif de filtrage des plans | Rien à ajouter si l’échange porte seulement sur le comportement implémenté ; retenir uniquement un piège ou une contrainte réutilisable réellement dégagés. |
| Choix d’extraits audio | Garder les objectifs et critères d’essai non évidents si utiles ensuite ; pas une liste des fichiers choisis. |
| Essai Cholesky abandonné | Garder l’hypothèse, la comparaison, les résultats qui motivent l’abandon et ce qui justifierait de réexaminer la piste. |

**Ne rien ajouter est un résultat normal**, y compris pour une conversation longue ou une modification importante du logiciel.

## Périmètre et comparaison

Utiliser la conversation désignée, pas d’autres chats par défaut.
Lire le contexte disponible ; si l’historique est incomplet ou doit être vérifié, utiliser l’outil de lecture avec pagination sur le périmètre demandé.
Un résumé de liste ou un dernier tour seul ne vaut pas lecture complète.
Signaler les parties inaccessibles ou tronquées sans reconstituer leur contenu ; une extraction partielle ne permet pas de conclure sur tout le chat.

Identifier le coffre et lire ses consignes, son index puis les seules notes pertinentes.
Dans AI-Toolkit : [index](../../Obsidian/Index.md) et [consignes du coffre](../../Obsidian/AGENTS.md).
Résoudre l’emplacement source réel du skill s’il est installé par lien ou jonction avant de suivre ces chemins relatifs.
Si le coffre n’est pas identifiable ou accessible, demander l’information manquante, sans créer un second coffre.

Comparer les candidats admis par leur sens et leur périmètre :
- distinguer décisions explicites, propositions, hypothèses et constats seulement rapportés ; ne pas convertir une suggestion de l’agent en choix validé ;
- conserver l’information à son emplacement de référence, compléter ou corriger une note existante avant d’en créer une ;
- une correction ou annulation ultérieure prime sur le choix précédent, sans devenir une interdiction générale non exprimée ;
- une décision ne prouve pas son exécution ; un résultat local ne vaut pas règle universelle ;
- si le code, une spécification, un skill ou AGENTS.md porte déjà l’information utile, y renvoyer plutôt que la recopier ;
- ne pas créer de note de consolidation par chat ; la seconde lecture du même périmètre sans élément nouveau ne doit produire aucun ajout.

## Mini-bilan avant écriture

Présenter un résumé court **ajouts / modifications / retraits**, avec les fichiers concernés et l’utilité future de chaque sujet retenu.
Indiquer l’absence de retrait lorsqu’aucun n’est prévu ; ne pas remplacer ce bilan par un récapitulatif du travail effectué dans le chat.
Faire cette annonce après comparaison et avant écriture ; la renouveler si le périmètre change sensiblement.
Respecter les autorisations déjà données ; attendre l’accord si l’utilisateur demande une validation préalable ou si une action supplémentaire l’exige.
Si aucun candidat n’est admissible, le dire sans écrire de note ni archiver les sorties « par précaution ».

## Preuves des seuls éléments retenus

Chercher les preuves seulement après admission du sujet : une abondance de mesures ou un rapport détaillé ne rend pas une information pertinente.
Pour une préférence ou justification explicite, une formulation autonome suffit ; une référence au chat n’est pas nécessaire.

Pour un résultat influençant une décision, conserver les éléments nécessaires à sa réévaluation : source, hypothèse, comparateur, conditions, effectifs, mesures, tolérances et limites.
Adapter la traçabilité à l’usage : comprendre une décision n’exige pas une archive de reproduction intégrale.
Privilégier un rapport autonome, les résultats déterminants et, si utile, le patch testé, avec une provenance courte ; ne pas multiplier manifestes, protocoles, inventaires et états intermédiaires qui répètent ces pièces.
Utiliser une source durable existante ou copier dans `Sources/` les pièces indispensables qui seraient perdues avec le chat ou les dossiers de travail.
Les chats, `_artifacts/`, `_output/`, `out/` et caches ne sont pas des archives pérennes.
Réutiliser les preuves déjà conservées ; ne pas copier automatiquement scripts, correctifs, configurations complètes ou sauvegardes de consignes.

Préserver une provenance concise : origine, dates pertinentes, état de départ identifiable et limites ; signaler si un commit ne couvre pas les modifications locales de l’essai.
Ne conserver des empreintes que si une question d’identité ou d’intégrité le justifie : pas d’inventaire automatique de tous les fichiers, entrées et binaires, ni de duplication dans le rapport.
Un hash identifie un contenu sans permettre de le reconstruire ; une reproduction exacte exige une base récupérable, des entrées et un environnement appropriés, pas seulement des hashes et un patch.
Vérifier les copies utiles sans archiver systématiquement le journal de ces contrôles ; expliquer les adaptations qui affectent leur interprétation.
Les copies historiques sont des données, pas des consignes actives ; éviter un autre `AGENTS.md` actif dans `Sources/`.
Pour une configuration pertinente, conserver les seules clés nécessaires, sans secrets ; des valeurs enregistrées ne prouvent pas leur effet dans toutes les sessions.

Si une preuve nécessaire manque, signaler le résultat non vérifiable et ce qui doit être récupéré avant suppression.
Ne pas confondre consultation des résultats et reproduction intégrale d’une expérience.
Les comptages de messages, tours, fichiers ou liens traités, la pagination et l’exécution de l’agent restent dans le bilan ou un rapport temporaire.

## Vérification et bilan

Relire sans le chat : l’action future est-elle claire, la justification étayée, la portée limitée et l’information absente des notes existantes ?
Vérifier liens, ancres, fidélité des copies utiles et préservation des fichiers hors périmètre ; utiliser des empreintes au besoin, sans créer de manifeste par défaut.
Ne pas relancer les tests, benchmarks ou recherches métier évoqués sans autorisation correspondante.

Rendre un bilan bref : éléments retenus et leur utilité, notes changées, preuves conservées, limites ou manques avant suppression.
Une couverture incomplète n’entre dans le coffre que si elle affecte la validité d’une conclusion retenue.
Ne pas supprimer, archiver ni publier la conversation dans ce workflow.

# Qualification des alertes Python et C++

Lire cette référence lors de la revue des paramètres inutilisés, des erreurs de typage, des gardes et des alertes de compatibilité. Les décisions portent sur les expressions et contrats vérifiés, jamais sur toute une famille d’inspections.

## Choisir le statut

- **Convention conservée** : le fait observé est exact mais volontaire, par exemple un argument accepté sans lecture pour respecter une signature ou une fixture demandée pour son initialisation.
- **Faux positif examiné** : les sources et le chemin d’exécution démontrent que le risque signalé ne peut pas se produire dans le cas examiné.
- **Limite de l’outil** : des stubs, annotations de dépendances ou éléments de configuration manquent et empêchent une conclusion. Leur absence ne prouve pas la correction du code.
- **À examiner** : le contrat est incorrect ou imprécis, une branche reste possible, ou la preuve dépend d’une hypothèse non établie.

Consigner dans les décisions du rapport la garde, la construction, la signature ou l’implémentation consultée. Réexaminer la qualification si ces éléments changent. Ne pas ajouter de cast, garde, commentaire de suppression ou changement d’API uniquement pour vider le rapport lorsque la convention ou le faux positif est déjà démontré.

## Paramètres, fixtures et signatures

Vérifier où la fonction est appelée ou enregistrée, et quel contrat elle reproduit. L’héritage seul ne justifie pas tous les paramètres inutilisés de toutes les méthodes d’une classe.

- Python : redéfinitions, callbacks Qt/Napari, hooks Pytest/Sphinx et doubles installés par monkeypatch peuvent devoir accepter des valeurs non exploitées. Par exemple, un substitut de `QFileDialog` accepte `parent`, `caption`, `directory` et les arguments supplémentaires ; un callback peut accepter `event` ; une méthode substituée sur une classe conserve `self` pour sa liaison. Vérifier aussi les appels par mot-clé avant tout renommage.
- Pytest : `qtbot` dépend de `qapp` et assure l’existence de l’application Qt même sans appel à `qtbot.addWidget` ou `waitSignal`. Examiner les widgets créés directement, les helpers et les fixtures dépendantes ; conserver le paramètre lorsque cette initialisation sert au scénario. Ne pas prétendre que les widgets non enregistrés sont automatiquement nettoyés par `qtbot`. Ne pas renommer la fixture en `_qtbot`, ni imposer `usefixtures` pour supprimer une alerte.
- C++ : pour une méthode `override`, un slot Qt ou une fonction passée à une API de callback, vérifier la déclaration de base, le type du pointeur de fonction ou l’enregistrement. Un argument imposé mais ignoré est une convention conservée. Ne pas ajouter systématiquement `[[maybe_unused]]`, `Q_UNUSED` ou une suppression ; suivre le besoin réel du compilateur et les conventions du projet. Un argument d’une surcharge librement définie peut révéler un oubli et reste à examiner.

## Types concrets et unions Python

Un retour `BaseSettingGroup | BaseSettingType` ou `BaseUIGroup | BaseUIType` peut perdre l’information portée par une clé de dictionnaire. Pour qualifier un accès comme `filters["Plane"].limits`, retrouver la classe concrète dans le schéma ou la fabrique, suivre sa construction et son héritage, puis vérifier qu’aucun remplacement incompatible n’intervient avant l’accès. Pour `get_ui`, contrôler le retour de la classe concrète et les membres effectivement fournis (`boxes`, `label`, etc.). Un nom de clé évocateur ne suffit pas.

Ne pas masquer les annotations réellement inexactes qui produisent ces diagnostics : une liste annotée comme contenant des instances alors qu’elle contient des classes appelables nécessite une correction de typage. Distinguer aussi le réemploi d’une variable avec plusieurs types incompatibles d’une simple perte de précision de l’analyseur.

Dans les tests, un `ViewerModel`, `_DummyLayer` ou autre double peut reproduire volontairement le contrat utilisé sans avoir le type nominal de production. Vérifier les membres nécessaires au scénario, puis conserver la convention ; ne pas élargir l’API de production uniquement pour accepter un double.

Pour une dépendance dynamique (Plotly, NumPy, Qt, etc.), consulter les stubs ou l’implémentation pertinents. Une union retournée par un conteneur peut être trop générale pour un accès particulier : démontrer le type de cet élément dans l’implémentation utilisée, sans généraliser aux autres indices ou versions.

## Gardes et conséquences d’un état antérieur

- Pour un accès sur un type optionnel ou une classe mère, vérifier que la garde établit bien le type de l’objet utilisé : `isinstance`, retour anticipé, assertion, invariant d’initialisation ou contrôle déjà effectué par l’appelant. Suivre les mutations, alias et appels susceptibles d’invalider cet état. Un retour non optionnel de la fonction ne prouve pas qu’un argument ne peut pas être `None`.
- Pour un tuple de taille fixe, une vérification effective `len(shape) == 3` peut démontrer le contrat malgré une annotation `tuple[int, ...]`. Vérifier la branche empruntée et la stabilité de la valeur ; ne pas imposer `shape[0], shape[1], shape[2]` uniquement pour l’analyseur.
- Pour une variable dite non initialisée, suivre toutes les branches. Deux `if` identiques peuvent assurer son existence seulement si la condition et ses dépendances n’ont pas changé entre eux ; tenir compte des exceptions, courts-circuits et appels intermédiaires.
- Examiner la cause initiale avant les diagnostics en cascade. Une garde prouvée peut justifier plusieurs faux positifs ; une annotation erronée ou une initialisation manquante doit rester visible avec ses conséquences utiles à la revue.

## Transposition au C++

Appliquer les mêmes exigences de preuve aux gardes, invariants, classes concrètes et callbacks, en tenant compte de la sémantique C++ :

- Un `dynamic_cast<T*>` suivi d’une vérification de non-nullité peut affiner le type ; vérifier aussi la durée de vie de l’objet. Un `static_cast`, `reinterpret_cast`, cast C ou simple annotation n’est pas une vérification du type dynamique. Un `dynamic_cast<T&>` peut lever `std::bad_cast`.
- Un test sur un pointeur, une taille ou un discriminant ne suffit que si aucune mutation, invalidation, réallocation ou concurrence ne peut rendre l’état caduc avant l’usage. Ne pas transposer le comportement des collections Python aux itérateurs et références C++.
- Pour `std::variant` ou `std::optional`, vérifier l’alternative ou l’engagement de la valeur et sa stabilité avant `get`, déréférencement ou `value`. Conserver les alertes de durée de vie, aliasing, concurrence et comportement indéfini tant que leur impossibilité n’est pas démontrée.
- Une interface mère ne possède pas automatiquement les membres d’une classe dérivée. Vérifier le type statique de l’expression et les conversions réellement effectuées ; la connaissance du type dynamique ne rend pas valide un accès qui ne compile pas.

## Compatibilité, API et conventions locales

Vérifier les versions et plateformes réellement prises en charge avant de qualifier une alerte visant une ancienne version. Ne pas réduire la compatibilité déclarée pour supprimer un diagnostic. En C++, contrôler les macros, options de compilation et cibles concernées avant de conclure qu’une branche est inactive ; distinguer le diagnostic réel du compilateur d’une limite de configuration de l’IDE.

Pour une dépréciation conditionnelle, lire le cas précis : une alerte sur `ctypes.POINTER` avec argument chaîne ne s’applique pas à un appel dont l’argument est effectivement un type ctypes. Ne pas masquer une dépréciation réellement applicable.

Une méthode ou un attribut nommé comme un builtin Python ne masque pas automatiquement le builtin dans la portée locale ; examiner la résolution du nom aux usages concernés. En C++, vérifier séparément les règles de recherche de noms et le masquage éventuel de surcharges héritées.

Pour les imports génériques d’utilitaires de tests, vérifier les symboles effectivement exportés avant de qualifier une référence comme résolue. Ne pas masquer un vrai nom absent. Les choix de projet (par exemple conserver certains imports `*`, ignorer Ruff B905 pour `zip`, ou une convention de fabrique Qt) ne deviennent pas des exceptions universelles du skill ; relire la configuration et les instructions du projet.

3# Rapport d'analyse comparative — Outils IA générative

## Contexte

J'ai développé ce projet avec l'assistance d'IA générative à chaque étape
(architecture, code, tests), conformément à la consigne du
sujet. Ce rapport présente mon analyse des forces et limites des outils que
j'ai utilisés.

## Outil n°1 — Claude (Sonnet 5, Anthropic)

**Usage** : j'ai utilisé Claude pour concevoir l'architecture, générer
l'intégralité du code (back-end FastAPI, nettoyage des données, front-end) et 
les tests unitaires , en l'exécutant et en le déboguant  
directement dans un environnement bac à sable (bash, édition de fichiers).

**Forces que j'ai observées**
- Une cohérence sur l'ensemble du projet : les conventions de nommage, la
  structure des modules et le style de code sont restés homogènes sur toute
  la session, y compris entre des fichiers générés à plusieurs échanges
  d'intervalle.
- La capacité à exécuter et corriger son propre code immédiatement
  (installer les dépendances, lancer les tests, constater un échec,
  corriger) plutôt que de me livrer du code non vérifié.
- Une bonne gestion des cas limites dès la première génération quand j'ai
  été précis dans ma consigne (ex : valeurs manquantes vs aberrantes
  traitées différemment dans `cleaner.py`).
- Une vérification active des faits techniques externes (recherche web pour
  confirmer le format exact de l'API Open-Meteo) plutôt qu'une simple
  confiance en une mémoire d'entraînement potentiellement datée.

**Limites que j'ai rencontrées**
- Une commande bash a échoué silencieusement (expansion d'accolades non
  supportée par le shell d'exécution), produisant un dossier au nom erroné ;
  je n'ai détecté l'erreur qu'à l'étape suivante. Ce n'est pas une
  « hallucination » au sens strict (aucune information fausse n'a été
  affirmée), mais une erreur d'environnement non anticipée — corrigée en un
  cycle.
- Une contrainte d'environnement (accès réseau restreint à une liste
  blanche de domaines) m'a empêché de démontrer la collecte réelle en
  conditions live : j'ai dû mettre en place une solution de contournement
  (jeu de données de démo) plutôt qu'une correction de code.
- Un CDN externe (Chart.js) était bloqué par mon propre réseau, ce qui a
  provoqué un message d'erreur trompeur dans le dashboard ; j'ai fait
  héberger la librairie localement pour résoudre le problème durablement.
- Je n'ai pas constaté d'hallucination factuelle caractérisée sur ce projet
  — ce que j'attribue au fait d'avoir fixé explicitement les contraintes
  (bornes de valeurs, contrat d'API) avant chaque génération, ce qui réduit
  l'espace d'invention du modèle.

**Confidentialité** : le code et les données que j'ai traités (mesures de
qualité de l'air, publiques) ne présentent pas de sensibilité particulière.
Pour un projet réel avec des données clients, je vérifierais la politique
de rétention des données de l'outil utilisé (offre entreprise avec « zero
data retention » si nécessaire) avant d'y soumettre du code ou des données
propriétaires.

**Pertinence du code généré** : directement exploitable après ma relecture ;
je n'ai eu besoin d'aucune réécriture structurelle, seulement des
corrections ponctuelles (cf. journal de bord).

## Outil n°2 — Gemini (Google)

**Usage** : j'ai utilisé Gemini pour générer les tests unitaires du module
`storage.py` (en lui envoyant le fichier seul, sans le reste du projet),
puis pour tester différentes formulations (français/anglais,
vague/précis) sur la fonction de nettoyage `cleaner.py`.

**Forces que j'ai observées**
- Sur un prompt précis, Gemini produit une structure très proche de mon
  code réel (mêmes choix : `set()` pour la déduplication, bornes de
  valeurs, liste de dictionnaires plutôt que pandas quand je l'ai demandé
  explicitement).
- Une bonne gestion spontanée des cas limites classiques (conversion de
  types ratée, valeurs non numériques) via des blocs `try/except`.
- Sur ma version anglaise vague, Gemini a deviné une étape de déduplication
  que je n'avais pas demandée explicitement — preuve d'une inférence
  correcte de mon besoin réel dans certains cas, même sans consigne
  précise.

**Limites que j'ai observées**
- Sur un prompt vague, Gemini suppose par défaut un DataFrame pandas avec
  interpolation des valeurs manquantes, ce qui ne correspond pas du tout à
  l'architecture réelle de mon projet (liste de dictionnaires, valeurs
  manquantes conservées à `None` plutôt qu'interpolées). J'en conclus qu'un
  prompt vague produit du code plausible en apparence mais structurellement
  inadapté à mon cas.
- Même sur un prompt précis, une règle métier de mon projet que je n'avais
  pas explicitement redemandée (supprimer une ligne si toutes ses valeurs
  sont invalides) n'a jamais été reproduite spontanément — j'en déduis
  qu'un prompt précis ne récupère que ce qui est explicitement spécifié,
  jamais les règles implicites déjà présentes ailleurs dans mon code.
- J'ai identifié un bug de fond dans les tests générés pour `storage.py` :
  la fixture utilisait `db_path = ":memory:"`, ce qui échoue silencieusement
  avec l'architecture de mon projet (chaque fonction ouvre sa propre
  connexion SQLite via `get_connection()`, donc une base en mémoire ne
  persiste pas entre deux appels). J'ai aussi relevé un import placeholder
  jamais remplacé (`from ton_module import ...`), et une assertion de test
  cassée qui ne vérifiait en réalité rien (`assert ... else True`).

**Confidentialité** : mêmes remarques que pour Claude — les données
utilisées ici sont publiques et sans sensibilité particulière, mais je
vérifierais au cas par cas la politique de rétention pour un projet avec
des données propriétaires.

**Pertinence du code généré** : correcte sur ma version précise, mais
nécessitant tout de même une relecture attentive puisque le bug n'était pas
visible sans exécution des tests ; peu exploitable telle quelle sur ma
version vague (mauvaise hypothèse de structure de données).

**Cas d'hallucination que j'ai rencontré** : je considère la fixture de
test `:memory:` comme une hallucination discrète — le code est
syntaxiquement correct et plausible, mais repose sur une hypothèse fausse
sur le comportement de SQLite avec l'architecture réelle de mon projet
(persistance d'une connexion en mémoire entre plusieurs appels distincts à
`get_connection()`, ce qui n'est pas le cas). Je ne l'ai détectée qu'à
l'exécution (`no such table`), pas à la lecture. Je l'ai corrigée en
remplaçant `:memory:` par un fichier temporaire réel (`tempfile.mkstemp`)
partagé entre les appels.

## Synthèse comparative

| Critère | Claude (Sonnet 5) | Gemini |
|---|---|---|
| Cohérence sur un projet multi-fichiers | Élevée (a suivi tout le projet en continu dans notre échange) | Non testée sur l'ensemble ; correcte sur un fichier isolé que j'ai transmis avec contexte |
| Autonomie (exécution/test du code généré) | Élevée (bac à sable intégré, corrige lui-même ses erreurs) | Aucune (pas d'exécution ; je n'ai découvert les bugs qu'en testant le code moi-même) |
| Hallucinations que j'ai constatées | Aucune sur ce périmètre | Une (fixture `:memory:`), plus une hypothèse structurelle erronée sur mon prompt vague (pandas au lieu de liste de dicts) |
| Sensibilité à la précision de mon prompt | Moins marquée (le contexte de mon projet était déjà connu dans l'échange) | Très marquée : écart de qualité important entre mon prompt vague et mon prompt précis |
| Confidentialité / données envoyées | À vérifier selon l'offre utilisée | À vérifier selon l'offre utilisée |

## Conclusion

L'IA générative m'a permis de couvrir l'ensemble des étapes du cahier des
charges (collecte, nettoyage, stockage, restitution, tests, documentation)
dans un délai resserré, à condition de garder une relecture systématique.
J'ai détecté chacun des points de friction rencontrés (erreur de shell,
restriction réseau de mon environnement, CDN bloqué, bugs des tests Gemini)
parce que j'ai exécuté et vérifié chaque étape immédiatement plutôt que de
produire « en aveugle ». Ce que je retiens surtout, c'est que la vigilance
est nécessaire non pas tant sur des hallucinations de contenu que sur les
hypothèses implicites — d'environnement (réseau, shell, versions) ou de
structure de données — que l'IA ne peut pas toujours anticiper sans que je
les précise moi-même.

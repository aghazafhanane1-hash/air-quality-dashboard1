# Journal de bord IA

> **Note méthodologique** : les entrées ci-dessous marquées **[Claude]** sont
> réelles et retracent la session effective de développement (Claude Sonnet 5,
> via l'interface Claude.ai, avec accès à un environnement d'exécution
> bac à sable — bash, édition de fichiers, recherche web). La consigne
> demande **au moins deux outils IA différents** : les entrées marquées
> **[Outil n°2 — à compléter]** sont des emplacements à remplir avec un
> second outil réellement testé (ex : GitHub Copilot dans l'IDE, ChatGPT,
> Gemini, Cursor). Le tableau montre le format attendu et un exemple de
> comparaison de formulation, à reproduire avec l'outil choisi.

## Légende qualité
- ✅ **Correcte** : utilisable telle quelle
- ⚠️ **Partielle** : utile mais nécessitant une correction
- ❌ **Hallucinée** : information fausse ou inventée

## Étapes clés

| # | Étape | Outil | Prompt (résumé) | Qualité | Correction apportée |
|---|---|---|---|---|---|
| 1 | Cadrage du projet | **[Claude]** Sonnet 5 | *« Sujet de rattrapage… tout, en partant de zéro étape par étape »* — choix du domaine, de la stack et de l'architecture | ✅ Correcte | Aucune ; choix justifiés (Open-Meteo car sans clé d'API, FastAPI + SQLite pour rester léger et sans serveur externe) |
| 2 | Vérification du format de l'API publique | **[Claude]** Sonnet 5, recherche web | *« Open-Meteo Air Quality API endpoint parameters example »* | ✅ Correcte | Confirmé l'URL exacte (`air-quality-api.open-meteo.com/v1/air-quality`) et les paramètres (`hourly`, `past_days`) avant de coder, plutôt que de faire confiance à la mémoire du modèle sur un détail d'API qui évolue |
| 3 | Génération du module de collecte (`collector.py`) | **[Claude]** Sonnet 5 | Génération directe à partir de la structure du projet, avec consigne explicite de gestion d'erreurs réseau et de résilience (une ville en échec ne bloque pas les autres) | ✅ Correcte | Aucune correction de fond ; testé immédiatement par des tests unitaires avec mocks |
| 4 | Génération du module de nettoyage (`cleaner.py`) | **[Claude]** Sonnet 5 | Consigne : gérer valeurs manquantes/aberrantes selon des bornes physiques, dédupliquer, trier | ✅ Correcte | Aucune ; les règles ont été explicitées avant génération (bornes dans `config.py`), ce qui a évité l'ambiguïté typique sur « que faire d'une valeur aberrante » |
| 5 | Création de la structure de dossiers (bash) | **[Claude]** Sonnet 5 | `mkdir -p .../{backend/app,backend/tests,frontend,docs}` | ⚠️ Partielle | L'expansion d'accolades bash a échoué silencieusement dans l'environnement d'exécution (a créé un dossier littéral `{backend`), provoquant une erreur en aval (`cd` impossible). Corrigé en remplaçant par des appels `mkdir -p` explicites, un par dossier. |
| 6 | Premier test de collecte réelle | **[Claude]** Sonnet 5 | `python -m app.ingest` | ⚠️ Partielle | L'exécution a échoué (HTTP 403) car le bac à sable de développement restreint les appels sortants à une liste blanche de domaines n'incluant pas `open-meteo.com`. Ce n'est pas une erreur de code : documenté dans le README, et un script `seed_demo_data.py` a été ajouté pour permettre la démonstration hors-ligne via le même pipeline de nettoyage. |
| 7 | Dashboard front-end (HTML/JS/Chart.js) | **[Claude]** Sonnet 5 | Consigne : au moins deux visualisations interactives, filtres ville/polluant, indicateurs clés | ✅ Correcte | Ajustements mineurs de style pour cohérence visuelle (palette, typographie) |
| 8 | *(à compléter)* | **[Outil n°2]** | *(ex : demander à un second outil de générer les tests unitaires du module `storage.py`)* | — | — |

## Test de formulations différentes (consigne obligatoire)

| Formulation | Outil | Résultat | Effet observé |
|---|---|---|---|
| **Français, vague** : « fais une API air quality » | *(à tester par l'étudiant)* | — | — |
| **Français, précis** : « expose 4 endpoints REST : /cities, /variables, /latest, /timeseries?city=&variable= renvoyant du JSON, avec CORS ouvert » | **[Claude]** Sonnet 5 | ✅ Endpoints générés exactement comme spécifié, y compris la gestion d'erreur 400 sur variable inconnue | Une consigne précise a éliminé toute ambiguïté sur le contrat d'API — recommandé pour du code destiné à être consommé par un front séparé |
| **Anglais, recherche web** : *« Open-Meteo Air Quality API endpoint parameters example »* | **[Claude]** Sonnet 5, recherche web | ✅ Résultats plus riches et plus directement issus de la documentation officielle qu'une requête équivalente en français | Pour la recherche d'information technique/API, l'anglais tend à remonter la documentation source en premier résultat, plutôt que des tutoriels tiers |
| *(à tester)* : reformuler la même demande en anglais vague, ex. « make an API for pollution data » | **[Outil n°2]** | — | *(à compléter — comparer verbosité, hypothèses implicites faites par l'outil, écarts avec le besoin réel)* |

## Ce qu'il reste à documenter par l'étudiant

Pour respecter pleinement la consigne (deux outils IA distincts, testés et
comparés), il est nécessaire de :
1. Reprendre une ou deux étapes ci-dessus (ex : génération des tests, ou du
   dashboard) avec un second outil réellement utilisé (Copilot, ChatGPT,
   Gemini, Cursor…).
2. Renseigner les lignes marquées *(à compléter)*.
3. Reporter les enseignements dans `rapport_comparatif.md`.

# Rapport d'analyse comparative — Outils IA générative

*(1-2 pages — à compléter par l'étudiant pour la partie « Outil n°2 »)*

## Contexte

Ce projet a été développé avec assistance d'IA générative à chaque étape
(architecture, code, tests, documentation), conformément à la consigne. Ce
rapport analyse les forces et limites des outils utilisés.

## Outil n°1 — Claude (Sonnet 5, Anthropic)

**Usage** : conception de l'architecture, génération de l'intégralité du
code (back-end FastAPI, nettoyage des données, front-end), des tests
unitaires, de la documentation, et exécution/débogage directe dans un
environnement bac à sable (bash, édition de fichiers).

**Forces observées**
- Cohérence sur l'ensemble du projet : les conventions de nommage, la
  structure des modules et le style de code sont restés homogènes sur toute
  la session, y compris entre des fichiers générés à plusieurs prompts
  d'intervalle.
- Capacité à exécuter et corriger son propre code immédiatement (installer
  les dépendances, lancer les tests, constater un échec, corriger) plutôt
  que de livrer du code non vérifié.
- Bonne gestion des cas limites dès la première génération quand la consigne
  était précise (ex : valeurs manquantes vs aberrantes traitées
  différemment dans `cleaner.py`).
- Vérification active des faits techniques externes (recherche web pour
  confirmer le format exact de l'API Open-Meteo) plutôt que de s'appuyer
  uniquement sur une mémoire d'entraînement potentiellement datée.

**Limites observées**
- Une commande bash a échoué silencieusement (expansion d'accolades non
  supportée par le shell d'exécution), produisant un dossier au nom erroné
  ; l'erreur n'a été détectée qu'à l'étape suivante. Ce n'est pas une
  « hallucination » au sens strict (aucune information fausse n'a été
  affirmée), mais une erreur d'environnement non anticipée — corrigée en un
  cycle.
- Contrainte d'environnement (accès réseau restreint à une liste blanche de
  domaines) empêchant de démontrer la collecte réelle en conditions live :
  a nécessité une solution de contournement (jeu de données de démo) plutôt
  qu'une correction de code.
- Pas d'hallucination factuelle caractérisée constatée sur ce projet — à
  mettre au crédit de prompts qui fixaient explicitement les contraintes
  (bornes de valeurs, contrat d'API) avant génération, ce qui réduit
  l'espace d'invention du modèle.

**Confidentialité** : le code et les données traitées (mesures de qualité
de l'air, publiques) ne présentent pas de sensibilité particulière. Pour un
projet réel avec des données clients, il conviendrait de vérifier la
politique de rétention des données de l'outil utilisé (offre entreprise
avec « zero data retention » si nécessaire) avant d'y soumettre du code ou
des données propriétaires.

**Pertinence du code généré** : directement exploitable après relecture ;
aucune réécriture structurelle nécessaire, seulement des corrections
ponctuelles (cf. journal de bord).

## Outil n°2 — *(à compléter)*

*(Nom de l'outil, IDE ou interface utilisée, étapes reprises avec cet outil)*

**Forces observées** : …

**Limites observées** : …

**Confidentialité** : …

**Pertinence du code généré** : …

**Cas d'hallucination rencontré** *(le cas échéant)* : décrire précisément
l'information fausse produite, comment elle a été détectée, et la
correction apportée.

## Synthèse comparative

| Critère | Claude (Sonnet 5) | Outil n°2 |
|---|---|---|
| Cohérence sur un projet multi-fichiers | Élevée | *(à compléter)* |
| Autonomie (exécution/test du code généré) | Élevée (bac à sable intégré) | *(à compléter)* |
| Hallucinations constatées | Aucune (sur ce périmètre) | *(à compléter)* |
| Confidentialité / données envoyées | À vérifier selon l'offre utilisée | *(à compléter)* |

## Conclusion

L'IA générative a permis de couvrir l'ensemble des étapes du cahier des
charges (collecte, nettoyage, stockage, restitution, tests, documentation)
dans un délai resserré, à condition de garder une relecture systématique :
les deux points de friction rencontrés (erreur de shell, restriction
réseau de l'environnement) ont été détectés parce que chaque étape a été
exécutée et vérifiée immédiatement plutôt que produite « en aveugle ». La
vigilance reste nécessaire non pas tant sur des hallucinations de contenu
que sur les hypothèses implicites d'environnement (réseau, shell,
versions) que l'IA ne peut pas toujours anticiper.

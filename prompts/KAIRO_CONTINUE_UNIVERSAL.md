# Prompt Universel Kairo

Copie-colle ce prompt dans Codex, Cursor ou GitHub Copilot Chat pour reprendre le projet sans dépendre de l’IDE.

```text
Tu travailles sur le projet Kairo.

Avant toute action, lis et considère comme source de vérité, dans cet ordre :
1. constitution/KAIRO_CONSTITUTION.md
2. IMPLEMENTATION_ROADMAP.md
3. PROJECT_STATUS.md
4. prompts/CODEX_AUTOPILOT.md
5. orgmind_prompt_pack/ si nécessaire pour l’architecture, la sécurité, la gouvernance ou la vision produit

Ensuite, inspecte le code réel du dépôt avant de décider quoi que ce soit.

Mission :
- déterminer automatiquement le sprint courant ou, si aucun sprint actif n’est explicitement en cours, identifier le prochain sprint non terminé à partir de la roadmap
- si la roadmap est partielle ou ambiguë, déduire le sprint le plus pertinent à partir de l’état réel du code, des dépendances architecturales, des risques techniques et de la maturité produit
- exécuter uniquement ce sprint, pas plusieurs à la fois
- garder les changements petits, cohérents et vérifiables
- préserver strictement l’isolation multi-tenant et la sécurité backend
- ne jamais laisser le LLM décider des droits d’accès
- ne jamais envoyer de données non autorisées au LLM, à une vue, à un export ou à un log
- implémenter la fonctionnalité de bout en bout si le sprint le demande : backend, frontend, contrats API, migrations, tests et documentation
- privilégier des tests autonomes et reproductibles, sans dépendre d’un PostgreSQL local si le dépôt propose déjà SQLite, des fakes ou un mode de test isolé
- exécuter les vérifications pertinentes, corriger les échecs, puis relancer jusqu’à validation
- mettre à jour PROJECT_STATUS.md et IMPLEMENTATION_ROADMAP.md dès que l’état du sprint change
- mettre à jour toute documentation de handoff utile pour qu’un autre agent reprenne immédiatement sans mémoire implicite

Règles de travail :
1. Commence par comprendre l’architecture, les modules existants et les points de fragilité.
2. Lis ensuite les modules ou docs utiles au sprint courant.
3. Implémente uniquement le sprint identifié.
4. Lance les tests et vérifications pertinentes pour la zone touchée.
5. Corrige les régressions avant de conclure.
6. Si la valeur du sprint n’est pas claire, rends le raisonnement explicite puis choisis la suite la plus utile.
7. Si le sprint est terminé, documenté et validé, indique clairement le prochain sprint ou précise qu’un nouveau cadrage est nécessaire.

Critère d’arrêt :
- le sprint choisi est effectivement terminé
- les tests pertinents ont été lancés et réussis
- la documentation a été mise à jour
- le prochain sprint est clairement identifié, ou l’absence d’un prochain sprint officiel est explicitement signalée

Format de sortie attendu :
- sprint exécuté
- pourquoi ce sprint a été choisi
- objectif du sprint
- changements réalisés
- fichiers modifiés
- tests lancés
- résultats des tests
- risques restants
- prochain sprint à exécuter
```

# Kairo Universal Compact Prompt

Use this prompt when you want a compact but high-signal continuation prompt for
Codex, Cursor, or Copilot.

```text
Tu travailles sur le projet Kairo.

Lis d’abord, dans cet ordre :
1. README.md
2. AGENTS.md
3. constitution/KAIRO_CONSTITUTION.md
4. IMPLEMENTATION_ROADMAP.md
5. PROJECT_STATUS.md
6. docs/ai/PROJECT_STATE.md
7. docs/ai/NEXT_SPRINT.md
8. prompts/CODEX_AUTOPILOT.md
9. prompts/KAIRO_CONTINUE_UNIVERSAL.md
10. orgmind_prompt_pack/ si nécessaire pour l’architecture, la sécurité, la gouvernance ou la vision produit

Ensuite, inspecte le code réel avant toute décision.

Règles non négociables :
- backend-only pour l’autorisation
- aucune fuite inter-tenant
- aucune donnée non autorisée envoyée au LLM, au frontend, aux exports ou aux logs
- membre ordinaire en lecture simple sauf actions personnelles explicitement autorisées
- rôles de bureau limités à leurs vraies prérogatives
- petits changements verticaux, testables, sans refactor global inutile
- docs et tests à jour si le comportement change

Mission par défaut :
- identifier le sprint actif ou le prochain sprint non terminé
- exécuter uniquement ce sprint
- vérifier les dépendances architecturales avant d’implémenter
- coder de bout en bout si nécessaire : backend, frontend, schémas, services, migrations, seed, tests, docs
- lancer les validations pertinentes, corriger, puis relancer jusqu’au vert
- mettre à jour PROJECT_STATUS.md, IMPLEMENTATION_ROADMAP.md, docs/ai/NEXT_SPRINT.md et docs/ai/PROJECT_STATE.md si l’état du sprint change

Ordre de priorité :
1. ce que dit explicitement PROJECT_STATUS.md ou docs/ai/NEXT_SPRINT.md
2. sinon le premier sprint non terminé dans IMPLEMENTATION_ROADMAP.md
3. sinon la suite la plus logique selon le code, les risques sécurité, les dépendances et la maturité produit

Format de sortie attendu :
- sprint exécuté
- pourquoi ce sprint
- objectif
- analyse rapide de l’existant
- changements réalisés
- fichiers modifiés
- tests lancés
- résultats
- risques restants
- prochain sprint
```

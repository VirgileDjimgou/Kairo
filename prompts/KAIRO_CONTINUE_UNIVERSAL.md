# Prompt Universel Kairo

Copie-colle ce prompt dans Codex, Cursor ou GitHub Copilot Chat pour reprendre le projet sans dépendre de l’IDE.

```text
Tu travailles sur le projet Kairo.

Avant toute action, lis et considère comme source de vérité :
- constitution/KAIRO_CONSTITUTION.md
- IMPLEMENTATION_ROADMAP.md
- PROJECT_STATUS.md
- prompts/CODEX_AUTOPILOT.md
- orgmind_prompt_pack/ si nécessaire pour l’architecture et la sécurité

Ensuite, inspecte le codebase réel.

Objectif :
- déterminer le sprint courant ou, si aucun sprint n’est explicitement indiqué, identifier de manière autonome le prochain sprint pertinent en fonction de l’état d’avancement, de la maturité du produit et des dépendances architecturales
- exécuter uniquement ce sprint
- ne pas partir sur plusieurs sprints à la fois

Règles de travail :
- Commence par comprendre l’architecture, les modules existants et les points de fragilité.
- Si le prochain sprint n’est pas écrit ou si la feuille de route est partielle, déduis la priorité la plus logique à partir de l’état du produit, des risques techniques, et des objectifs commerciaux.
- Quand c’est utile, fais d’abord une lecture module par module du backend, puis du frontend, puis des tests et de la documentation.
- Implémente la fonctionnalité de bout en bout : backend, frontend, contrats API, migration si nécessaire, tests, et documentation.
- Préfère une stratégie de tests totalement autonome. Ne dépends pas d’un PostgreSQL local si le dépôt propose déjà un mode SQLite ou des fakes pour les tests.
- Ajoute ou mets à jour des tests pour toute logique touchée. Fais des tests réalistes et approfondis : unitaires, intégration, et si pertinent vérification navigateur / environnement virtuel.
- Vérifie les cas limites, les permissions, l’isolation multi-tenant, et les régressions probables.
- Les permissions sont toujours garanties par le backend. Le LLM ou le frontend ne doivent jamais décider de l’accès.
- Ne fais jamais fuiter des données non autorisées vers le LLM ou vers une vue qui ne devrait pas les voir.
- Garde les changements petits, explicites et cohérents avec l’architecture existante.
- Si une valeur de sprint n’est pas claire, rends-la explicite dans ton raisonnement, puis choisis la suite la plus utile.
- Si un test ou un build échoue, analyse, corrige, relance, puis continue jusqu’à validation.
- Mets à jour PROJECT_STATUS.md et IMPLEMENTATION_ROADMAP.md dès que le sprint progresse ou se termine.
- Si une doc de handoff existe ou doit être créée, mets-la à jour pour que Cursor, Copilot ou Codex puissent continuer sans perte de contexte.

Critère d’arrêt :
- tu t’arrêtes seulement quand le sprint en cours est terminé, testé, documenté, et que le prochain sprint est clairement identifié.

Format de sortie attendu :
- sprint exécuté
- objectif du sprint
- changements réalisés
- fichiers modifiés
- tests lancés et résultats
- risques restants
- prochain sprint à exécuter
```

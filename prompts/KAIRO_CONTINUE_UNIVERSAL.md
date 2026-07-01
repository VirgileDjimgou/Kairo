# Prompt Universel Kairo

Copie-colle ce prompt dans Codex, Cursor ou GitHub Copilot Chat pour reprendre Kairo sans dépendre de l'IDE.

```text
Tu travailles sur le projet Kairo.

Avant toute action, lis et considère comme source de vérité, dans cet ordre :
1. README.md
2. AGENTS.md
3. constitution/KAIRO_CONSTITUTION.md
4. IMPLEMENTATION_ROADMAP.md
5. PROJECT_STATUS.md
6. prompts/CODEX_AUTOPILOT.md
7. prompts/KAIRO_CONTINUE_UNIVERSAL.md
8. orgmind_prompt_pack/ si nécessaire pour l'architecture, la sécurité, la gouvernance ou la vision produit

Ensuite, inspecte le code réel du dépôt avant de décider quoi que ce soit.

Contexte produit à respecter :
- Kairo doit évoluer vers un produit associatif professionnel, stable, clair, sobre, élégant et mature
- les membres ordinaires doivent rester sur une expérience simple, surtout en lecture, avec accès rapide à leurs informations personnelles et à leurs cotisations
- les membres ordinaires ne doivent jamais voir les données d'un autre adhérent
- les rôles de bureau doivent disposer d'espaces ciblés selon leurs prérogatives
- le chatbot doit être opérationnel pour chaque rôle, mais toujours limité aux données réellement autorisées

Rôles cibles du track courant :
- principal_admin
- president
- vice_president
- secretary_general
- treasurer
- auditor
- censor
- sports_manager
- member

Mission :
- déterminer automatiquement le sprint courant ou, si aucun sprint actif n'est explicitement en cours, identifier le prochain sprint non terminé à partir de la roadmap
- si la roadmap est partielle ou ambiguë, déduire le sprint le plus pertinent à partir de l'état réel du code, des dépendances architecturales, des risques techniques et de la maturité produit
- exécuter uniquement ce sprint, jamais plusieurs à la fois
- garder les changements petits, cohérents, testables et compatibles avec l'architecture existante
- préserver strictement l'isolation multi-tenant et la sécurité backend
- ne jamais laisser le frontend ou le LLM décider seuls des droits d'accès
- ne jamais envoyer de données non autorisées au LLM, à une vue, à un export ou à un log
- implémenter réellement le sprint choisi de bout en bout si nécessaire : backend, frontend, schémas, services, migrations, tests, seed et documentation
- privilégier des tests autonomes et reproductibles, sans dépendre d'un PostgreSQL local si le dépôt propose déjà SQLite, des fakes ou une configuration de test isolée
- exécuter les vérifications pertinentes, corriger les échecs, puis relancer jusqu'à validation
- mettre à jour PROJECT_STATUS.md et IMPLEMENTATION_ROADMAP.md dès que l'état du sprint change
- mettre à jour docs/ai/NEXT_SPRINT.md, docs/ai/PROJECT_STATE.md et toute documentation de handoff utile

Règles de priorité :
1. Si PROJECT_STATUS.md ou docs/ai/NEXT_SPRINT.md désigne explicitement le prochain sprint, exécute ce sprint.
2. Sinon, prends dans IMPLEMENTATION_ROADMAP.md le premier sprint non terminé.
3. Si la roadmap ne suffit pas, choisis la suite la plus logique selon :
   - l'état réel du code
   - les dépendances architecturales
   - les risques de sécurité
   - la cohérence avec le produit associatif cible
4. Rends le choix du sprint explicite.

Règles produit non négociables :
- un membre ordinaire reste en lecture simple sauf pour ses actions personnelles autorisées
- le bureau dispose d'écritures ciblées selon le rôle, pas d'un accès global implicite
- le principal_admin garde l'accès le plus étendu dans le tenant, sans jamais casser l'isolation multi-tenant
- le chatbot ne révèle jamais les cotisations, sanctions, documents privés ou informations personnelles d'un autre membre
- la sécurité doit être garantie par le backend avant toute génération LLM

Critère d'arrêt :
- le sprint choisi est effectivement implémenté
- les tests pertinents ont été lancés et réussis
- la documentation a été mise à jour
- le prochain sprint est clairement identifié

Format de sortie attendu :
- sprint exécuté
- pourquoi ce sprint a été choisi
- objectif du sprint
- analyse rapide de l'existant pertinent
- changements réalisés
- fichiers modifiés
- tests lancés
- résultats des tests
- risques restants
- prochain sprint à exécuter
```

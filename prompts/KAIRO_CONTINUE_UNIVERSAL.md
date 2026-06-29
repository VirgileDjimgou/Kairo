# Prompt Universel Kairo

Copie-colle ce prompt dans Codex, Cursor ou GitHub Copilot Chat pour reprendre le projet sans dépendre de l’IDE.

```text
Tu travailles sur le projet Kairo.

Avant toute action, lis et considère comme source de vérité, dans cet ordre :
1. constitution/KAIRO_CONSTITUTION.md
2. IMPLEMENTATION_ROADMAP.md
3. PROJECT_STATUS.md
4. prompts/CODEX_AUTOPILOT.md
5. prompts/KAIRO_CONTINUE_UNIVERSAL.md si présent
6. docs/ai/NEXT_SPRINT.md
7. docs/ai/PROJECT_STATE.md
8. orgmind_prompt_pack/ si nécessaire pour l’architecture, la sécurité, la gouvernance ou la vision produit

Ensuite, inspecte le code réel du dépôt avant de décider quoi que ce soit.

Mission générale :
- déterminer automatiquement le sprint courant ou, si aucun sprint actif n’est explicitement en cours, identifier le prochain sprint officiel à exécuter à partir de la roadmap
- exécuter uniquement ce sprint
- ne jamais partir sur plusieurs sprints à la fois
- poursuivre le projet vers une version commerciale, professionnelle et mûre
- agir comme un agent produit + architecture + implémentation + QA + documentation

Règle de priorité pour choisir le sprint :
1. si PROJECT_STATUS.md ou docs/ai/NEXT_SPRINT.md indique explicitement un prochain sprint, exécuter celui-là
2. sinon, identifier dans IMPLEMENTATION_ROADMAP.md le premier sprint non terminé
3. si la roadmap est incomplète ou ambiguë, déduis le sprint le plus pertinent selon :
   - l’état réel du code
   - les dépendances architecturales
   - les risques techniques
   - les besoins de robustesse produit
   - la cohérence avec une trajectoire commerciale réaliste
4. rendre explicite le sprint choisi et pourquoi

Mode opératoire obligatoire :
- commencer par comprendre l’architecture existante
- lire les modules backend, frontend, tests, scripts, docs et configurations utiles
- identifier les écarts entre roadmap, état réel du code et statut déclaré
- implémenter le sprint de bout en bout
- garder les changements petits, cohérents, explicites et compatibles avec l’architecture existante
- ne pas réécrire inutilement ce qui fonctionne déjà
- préserver strictement l’isolation multi-tenant, la sécurité et les permissions backend

Exigences d’implémentation :
- implémenter réellement le sprint choisi, pas seulement proposer un plan
- couvrir si nécessaire :
  - backend
  - frontend
  - contrats API
  - schémas
  - modèles
  - services
  - migrations
  - tests
  - documentation
  - seed ou fixtures si utile
- si un point du sprint exige une décision de conception non triviale, choisir l’option la plus simple, maintenable et cohérente avec le dépôt
- ne pas dériver vers le sprint suivant tant que le sprint courant n’est pas terminé

Règles de sécurité et de gouvernance :
- les permissions sont toujours garanties par le backend
- le frontend et tout composant IA ne doivent jamais décider seuls de l’accès
- ne jamais exposer de données d’un tenant à un autre
- ne jamais fuiter de données non autorisées vers le LLM, vers une vue, vers un export ou vers un log
- vérifier les cas limites, les rôles, les accès croisés, les IDs invalides, les ressources absentes et les états partiels

Règles de test :
- privilégier une suite de tests autonome
- ne pas dépendre d’un PostgreSQL local si le dépôt permet SQLite, des fakes, des mocks ou une configuration de test isolée
- ajouter ou mettre à jour les tests pour toute logique touchée
- exécuter autant que pertinent :
  - tests unitaires
  - tests d’intégration
  - tests API
  - tests de régression
  - tests navigateur / E2E si adaptés au sprint
- si le projet permet une vérification navigateur ou environnement virtuel, l’utiliser pour valider les parcours critiques
- si un test échoue, analyser, corriger, relancer, puis continuer jusqu’à obtenir un état valide

Règles de qualité :
- traiter la dette technique utile à corriger seulement si elle bloque ou fragilise directement le sprint
- signaler clairement les risques restants
- éviter les hacks cachés, les valeurs magiques et les duplications évitables
- documenter les arbitrages quand ils impactent les futures sessions
- préparer le projet pour une continuité fluide dans Codex, Cursor ou Copilot

Mise à jour documentaire obligatoire :
à la fin du sprint, mettre à jour si nécessaire :
- PROJECT_STATUS.md
- IMPLEMENTATION_ROADMAP.md
- docs/ai/NEXT_SPRINT.md
- docs/ai/PROJECT_STATE.md
- toute documentation de handoff utile

Règle de continuité inter-IDE :
- faire en sorte qu’un autre agent puisse reprendre immédiatement sans mémoire implicite
- écrire l’état final du sprint de manière exploitable
- identifier explicitement le prochain sprint à exécuter après celui terminé
- si la roadmap doit être raffinée à la marge pour refléter la réalité du code, la mettre à jour proprement

Critère d’arrêt :
tu t’arrêtes seulement quand :
- le sprint choisi est effectivement implémenté
- les tests pertinents ont été lancés
- les échecs ont été corrigés ou explicitement documentés
- la documentation a été mise à jour
- le prochain sprint est clairement identifié

Format de sortie attendu en fin d’exécution :
- sprint exécuté
- pourquoi ce sprint a été choisi
- objectif du sprint
- analyse rapide de l’existant pertinent
- changements réalisés
- fichiers modifiés
- tests lancés
- résultats des tests
- risques restants
- dette technique restante pertinente
- mises à jour documentaires effectuées
- prochain sprint à exécuter

Comportement attendu :
- sois autonome, rigoureux et concret
- n’attends pas une validation intermédiaire pour avancer
- exécute
- vérifie
- corrige
- documente
- passe la main proprement au sprint suivant
```

# Prompt Universel - Kairo

À coller tel quel dans Codex, Cursor, GitHub Copilot Chat ou tout autre IDE agentique.

```text
Continue Kairo.

Avant de modifier quoi que ce soit, lis exactement:
- constitution/KAIRO_CONSTITUTION.md
- IMPLEMENTATION_ROADMAP.md
- PROJECT_STATUS.md
- prompts/CODEX_AUTOPILOT.md

Ensuite, inspecte le code courant pour confirmer l’état réel du projet.

Ta mission:
- déterminer de façon autonome le sprint en cours ou le prochain sprint non terminé
- exécuter uniquement ce sprint, pas toute la plateforme
- si le sprint n’est pas clairement écrit, déduis les priorités à partir de l’état d’avancement, de la maturité du produit et des risques techniques
- avancer par petites étapes verticales, cohérentes, testables
- conserver l’isolation tenant et la sécurité backend comme priorités absolues
- ne jamais laisser le LLM décider des droits d’accès
- ne jamais envoyer de données non autorisées au LLM
- utiliser les abstractions de providers existantes
- ajouter ou mettre à jour les tests pour toute logique touchée
- lancer les vérifications pertinentes, corriger les échecs, puis relancer
- mettre à jour la documentation si l’architecture, les contrats, la sécurité ou le comportement changent
- mettre à jour PROJECT_STATUS.md et IMPLEMENTATION_ROADMAP.md avant de t’arrêter si l’état du sprint a changé

Règles d’exécution:
1. Commence par identifier le sprint à exécuter.
2. Implémente le plus petit slice utile du sprint.
3. Valide avec des tests ciblés, et si possible par un flux réaliste de bout en bout.
4. Si un test échoue, diagnostique, corrige, puis revalide.
5. Si une décision métier ou d’architecture bloque, explique le tradeoff et propose l’option la plus sûre.
6. Quand le sprint est terminé et vérifié, arrête-toi proprement et résume:
   - ce qui a été fait
   - ce qui a été vérifié
   - les risques restants
   - le prochain sprint recommandé

Contraintes:
- ne fais pas un gros refactor global si un sprint plus petit suffit
- ne saute pas la vérification
- ne suppose pas que les docs sont à jour
- ne continue jamais “par mémoire”

Commence maintenant.
```

Version courte:

```text
Continue Kairo. Lis KAIRO_CONSTITUTION.md, IMPLEMENTATION_ROADMAP.md, PROJECT_STATUS.md et prompts/CODEX_AUTOPILOT.md, identifie le sprint en cours ou le prochain sprint non terminé, implémente seulement ce sprint, teste, corrige, mets à jour les docs, puis arrête-toi avec un résumé clair.
```

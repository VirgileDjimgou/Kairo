#!/usr/bin/env node
/**
 * Kairo session brief.
 *
 * A new agent session has no memory of previous sessions: the repository is the
 * only memory. Reading the whole documentation set to "get oriented" costs more
 * than a full context window, so orientation lives on one page that stays true.
 *
 * This script prints that page together with live, non-persisted state:
 *   - roadmap program metadata from docs/roadmap/KAIRO_V2_ROADMAP.json;
 *   - sprint progress and batch state from .kairo/sprint-batch/ (untracked);
 *   - git position, so a resumed session sees what the last one left behind.
 *
 * `docs/ai/SESSION_BRIEF.md` is the checked-in static snapshot. It deliberately
 * excludes untracked batch state so that `--check` stays deterministic in CI.
 *
 * Usage:
 *   node scripts/session-brief.mjs            print the brief (static + live)
 *   node scripts/session-brief.mjs --write    regenerate docs/ai/SESSION_BRIEF.md
 *   node scripts/session-brief.mjs --check    fail when the snapshot is stale
 *   node scripts/session-brief.mjs --json     machine-readable brief
 */
import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import path from 'node:path';

import { findRoot, loadRoadmap } from './sprint-batch/roadmap.mjs';
import { TERMINAL_BATCH_STATES } from './sprint-batch/state.mjs';

const BRIEF_RELATIVE_PATH = 'docs/ai/SESSION_BRIEF.md';
const STATE_RELATIVE_PATH = path.join('.kairo', 'sprint-batch', 'state.json');
const HANDOFF_DIRECTORY = path.join('.kairo', 'sprint-batch', 'handoffs');

const COMMANDS = [
  ['Warm-up (static + live)', 'npm run session:brief'],
  ['Regenerate this snapshot', 'npm run session:brief -- --write'],
  ['Next unfinished sprint', 'npm run sprint:next'],
  ['Batch status', 'npm run sprint:batch:status'],
  ['Resume an incomplete batch', 'npm run sprint:batch:resume'],
  ['Backend tests', 'python -m pytest services/api/tests -q'],
  ['Web type check', 'cd apps/web && npm run type-check'],
  ['OpenAPI + client contracts', 'npm run contracts:check'],
  ['FR/EN/DE catalog parity', 'node scripts/check-i18n-parity.mjs'],
  ['Hardcoded string scan', 'node scripts/check-i18n-coverage.mjs'],
  ['PWA service worker guard', 'npm run pwa:check'],
];

const ROUTING = [
  ['Tenant isolation, roles, authorization', 'constitution/KAIRO_CONSTITUTION.md, services/api/app'],
  ['Architecture, module boundaries, ADRs', 'docs/architecture/CURRENT_ARCHITECTURE.md, docs/architecture/decisions/'],
  ['API contract or endpoint change', 'services/api/app, services/api/tests, npm run contracts:check'],
  ['Vue PWA screen or i18n copy', 'apps/web/src/i18n/messages.ts, translation governance in AGENTS.md'],
  ['Sprint execution policy', 'docs/automation/SPRINT_BATCH_AUTOPILOT.md, prompts/KAIRO_SPRINT_EXECUTOR.md'],
  ['Product narrative or release history', 'PROJECT_STATUS.md (grep the section, do not read in full)'],
  ['Historical rationale before Sprint 100', 'IMPLEMENTATION_ROADMAP.md (grep a sprint section only)'],
  ['Frozen Flutter behaviour reference', 'apps/flutter_kairo/AGENTS.md, docs/pwa/FLUTTER_TO_PWA_PARITY.md'],
];

const AVOID_AT_START = [
  ['IMPLEMENTATION_ROADMAP.md', 'Historical Sprint 0-99 record. Grep one section; never read it in full.'],
  ['docs/flutter/**', 'Frozen legacy client (ADR-014). Not part of the active program.'],
  ['orgmind_prompt_pack/**', 'Historical prompt pack superseded by constitution/ and docs/architecture/.'],
  ['PROJECT_STATUS.md', 'Long product narrative. Read the section a task names, not the file.'],
  ['.kairo/sprint-batch/handoffs/**', 'Read only the handoff of the sprint being resumed.'],
  ['.kairo/sprint-batch/reports/**', 'Audit trail. Read a report only when investigating a past failure.'],
];

const GUARD_RAILS = [
  'Every tenant-scoped query filters by `tenant_id`; the backend is the only policy enforcement point.',
  'LLMs never decide access control; retrieval filtering happens before prompt assembly.',
  'The frontend consumes API contracts only and duplicates no business rule.',
  'Never weaken a test, tolerance, security or authorization check to pass a gate.',
  'COMBIS is a demo tenant, never product logic.',
  'Roadmap V2 sprints are sequential: a blocked sprint blocks the batch; never skip ahead.',
];

function formatBytes(bytes) {
  return `${Math.round(bytes / 1024)} KB`;
}

function git(rootDir, args) {
  try {
    return execFileSync('git', args, { cwd: rootDir, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
  } catch {
    return null;
  }
}

function liveGit(rootDir) {
  const sha = git(rootDir, ['rev-parse', '--short', 'HEAD']);
  if (!sha) {
    return { available: false };
  }
  const branch = git(rootDir, ['rev-parse', '--abbrev-ref', 'HEAD']) ?? 'detached';
  const subject = git(rootDir, ['log', '-1', '--pretty=%s']) ?? '';
  const committedAt = git(rootDir, ['log', '-1', '--pretty=%cI']) ?? '';
  const status = git(rootDir, ['status', '--porcelain']);
  const dirtyFiles = status ? status.split('\n').filter(Boolean).length : 0;
  return { available: true, sha, branch, subject, committedAt, dirtyFiles };
}

function liveBatch(rootDir) {
  const statePath = path.join(rootDir, STATE_RELATIVE_PATH);
  if (!existsSync(statePath)) {
    return { available: false };
  }
  let state;
  try {
    state = JSON.parse(readFileSync(statePath, 'utf8'));
  } catch {
    return { available: false, unreadable: true };
  }
  const sprints = Array.isArray(state.sprints) ? state.sprints : [];
  const byStatus = (status) => sprints.filter((sprint) => sprint.status === status);
  return {
    available: true,
    batchId: state.batch_id ?? null,
    status: state.status ?? null,
    runnerStatus: state.runner_status ?? null,
    currentSprint: state.current_sprint ?? null,
    currentPhase: state.current_phase ?? null,
    requestedCount: state.requested_count ?? null,
    completedCount: state.completed_count ?? null,
    remaining: state.batch_remaining ?? null,
    queueAvailable: state.queue_available ?? null,
    stopRequested: state.stop_requested ?? null,
    blockers: Array.isArray(state.blockers) ? state.blockers : [],
    pauseReason: state.pause_reason ?? null,
    lastSuccessfulGate: state.last_successful_gate ?? null,
    completedSprints: byStatus('completed').map((sprint) => sprint.id),
    inProgressSprints: byStatus('in_progress').map((sprint) => sprint.id),
    sprints,
  };
}

function latestHandoff(rootDir) {
  const directory = path.join(rootDir, HANDOFF_DIRECTORY);
  if (!existsSync(directory)) {
    return null;
  }
  const handoffs = readdirSync(directory)
    .filter((name) => name.endsWith('.json'))
    .map((name) => {
      const match = /^sprint-(\d+)\.json$/.exec(name);
      return match ? { id: Number(match[1]), file: path.join(HANDOFF_DIRECTORY, name) } : null;
    })
    .filter(Boolean)
    .sort((left, right) => left.id - right.id);
  return handoffs.length > 0 ? handoffs[handoffs.length - 1] : null;
}

function progress(roadmap, batch) {
  const declared = roadmap.sprints.map((sprint) => sprint.id);
  const completed = new Set(batch.available ? batch.completedSprints : []);
  const unfinished = declared.filter((id) => !completed.has(id));
  const lastDelivered = batch.available
    ? roadmap.sprints.filter((sprint) => completed.has(sprint.id)).slice(-1)[0] ?? null
    : null;
  return { declared, unfinished, lastDelivered };
}

function nextAction(roadmap, batch) {
  const { unfinished, lastDelivered } = progress(roadmap, batch);
  if (!batch.available) {
    return {
      headline: 'No batch state on disk.',
      body: 'Run `npm run sprint:batch:status` before assuming any sprint is unfinished.',
    };
  }
  if (batch.inProgressSprints.length > 0) {
    const sprint = roadmap.sprints.find((entry) => entry.id === batch.inProgressSprints[0]);
    return {
      headline: `Resume sprint S${sprint.id} (${sprint.title}) from its real state.`,
      body: 'Inspect the working tree and continue the existing implementation; never restart a partially implemented sprint.',
    };
  }
  if (unfinished.length > 0) {
    const sprint = roadmap.sprints.find((entry) => entry.id === unfinished[0]);
    return {
      headline: `Execute the next unfinished sprint: S${sprint.id} (${sprint.title}).`,
      body: 'Use `Start Next Sprint`, record every transition through the sprint batch CLI, and do not skip ahead.',
    };
  }
  if (batch.status === 'running') {
    return {
      headline: `All ${declaredCount(roadmap)} roadmap sprints are completed, but batch ${batch.batchId} is still \`${batch.status}\`.`,
      body: 'Close the orphaned batch with `npm run sprint:batch:reset -- --reason "<why>"` before starting work, otherwise every new session re-derives that nothing is executable.',
    };
  }
  return {
    headline: `All ${declaredCount(roadmap)} roadmap sprints are completed; batch ${batch.batchId} is \`${batch.status}\`.`,
    body: [
      'The next actions are operator-owned, not agent-owned:',
      'run the manual pilot steps in `docs/pwa/COMBIS_PILOT_CHECKLIST.md`, then decide on Roadmap V3 (`docs/roadmap/KAIRO_V3_ROADMAP.md`) as a separate planning decision.',
      lastDelivered ? `Last delivered sprint: S${lastDelivered.id} ${lastDelivered.title}.` : '',
    ].filter(Boolean).join(' '),
  };
}

function declaredCount(roadmap) {
  return roadmap.sprints.length;
}

function renderStatic(roadmap) {
  const lines = [];
  lines.push('<!-- GENERATED FILE - do not edit by hand. -->');
  lines.push('<!-- Regenerate: npm run session:brief -- --write -->');
  lines.push('<!-- Drift guard: npm run session:brief:check (CI) -->');
  lines.push('');
  lines.push('# Kairo Session Brief');
  lines.push('');
  lines.push('Orientation only. Sprint progress, batch state and git position are printed by');
  lines.push('`npm run session:brief`; they are untracked runtime state and are never stored here.');
  lines.push('');
  lines.push('## Start here');
  lines.push('');
  lines.push('1. Run `npm run session:brief` (one command: this page plus live state).');
  lines.push('2. Read only the documents named by the task routing table below.');
  lines.push('3. Never read the whole documentation set to "get oriented".');
  lines.push('');
  lines.push('## Canonical program');
  lines.push('');
  lines.push('| Field | Value |');
  lines.push('| --- | --- |');
  lines.push(`| Roadmap | \`${roadmap.roadmap}\` version ${roadmap.version} |`);
  lines.push(`| Active program | \`${roadmap.active_program}\` |`);
  lines.push(`| Program range | ${roadmap.program_range} |`);
  lines.push(`| Declared sprints | ${declaredCount(roadmap)} (S${roadmap.sprints[0].id}-S${roadmap.sprints[roadmap.sprints.length - 1].id}) |`);
  lines.push(`| Sprint file | \`docs/roadmap/KAIRO_V2_ROADMAP.json\` |`);
  lines.push(`| Historical record | \`${roadmap.historical_roadmap}\` (read-only) |`);
  lines.push('');
  lines.push(`Objective: ${roadmap.objective}`);
  lines.push('');
  lines.push('Sprint completion has exactly two sources of truth: the roadmap JSON plus');
  lines.push('`.kairo/sprint-batch/state.json` (untracked) and the handoff in');
  lines.push('`.kairo/sprint-batch/handoffs/`. Never infer completion from prose, file dates or');
  lines.push('`PROJECT_STATUS.md` narratives.');
  lines.push('');
  lines.push('## Task routing');
  lines.push('');
  lines.push('| If the task touches | Read only this |');
  lines.push('| --- | --- |');
  for (const [task, source] of ROUTING) {
    lines.push(`| ${task} | ${source} |`);
  }
  lines.push('');
  lines.push('## Do not read at session start');
  lines.push('');
  lines.push('| Path | Why |');
  lines.push('| --- | --- |');
  for (const [file, reason] of AVOID_AT_START) {
    lines.push(`| \`${file}\` | ${reason} |`);
  }
  lines.push('');
  lines.push('## Guard rails');
  lines.push('');
  lines.push('The complete rules live in `AGENTS.md`. Non-negotiable subset:');
  lines.push('');
  for (const rule of GUARD_RAILS) {
    lines.push(`- ${rule}`);
  }
  lines.push('');
  lines.push('## Commands');
  lines.push('');
  lines.push('| Intent | Command |');
  lines.push('| --- | --- |');
  for (const [intent, command] of COMMANDS) {
    lines.push(`| ${intent} | \`${command}\` |`);
  }
  lines.push('');
  return `${lines.join('\n')}`;
}

function renderLive(rootDir, roadmap) {
  const batch = liveBatch(rootDir);
  const handoff = latestHandoff(rootDir);
  const lines = [];

  lines.push('## Live state');
  lines.push('');
  lines.push('### Git');
  lines.push('');
  const position = liveGit(rootDir);
  if (!position.available) {
    lines.push('- git unavailable in this environment.');
  } else {
    lines.push(`- branch \`${position.branch}\` at \`${position.sha}\` (${position.committedAt})`);
    lines.push(`- last commit: ${position.subject}`);
    lines.push(`- uncommitted files: ${position.dirtyFiles}${position.dirtyFiles > 0 ? ' (preserve unrelated user changes)' : ''}`);
  }
  lines.push('');

  lines.push('### Sprint batch');
  lines.push('');
  if (!batch.available) {
    lines.push(batch.unreadable
      ? '- `.kairo/sprint-batch/state.json` exists but is unreadable; run `npm run sprint:batch:doctor`.'
      : '- no `.kairo/sprint-batch/state.json`; run `npm run sprint:batch:status` before assuming progress.');
  } else {
    const { declared, unfinished, lastDelivered } = progress(roadmap, batch);
    const completed = declared.filter((id) => batch.completedSprints.includes(id));
    lines.push(`- batch \`${batch.batchId}\`: status \`${batch.status}\`, runner \`${batch.runnerStatus}\``);
    lines.push(`- current sprint: ${batch.currentSprint ? `S${batch.currentSprint} (phase \`${batch.currentPhase}\`)` : 'none'}`);
    lines.push(`- progress: ${completed.length}/${declared.length} roadmap sprints completed`);
    lines.push(`- last delivered: ${lastDelivered ? `S${lastDelivered.id} ${lastDelivered.title}` : 'none recorded'}`);
    if (lastDelivered && handoff && handoff.id === lastDelivered.id) {
      lines.push(`- last handoff: \`${handoff.file.replace(/\\/g, '/')}\` (${formatBytes(readFileSync(path.join(rootDir, handoff.file)).length)})`);
    }
    if (TERMINAL_BATCH_STATES.has(batch.status)) {
      lines.push('- batch closed: no sprint is executable from this batch.');
    } else {
      lines.push(`- requested: ${batch.requestedCount}, completed: ${batch.completedCount}, remaining: ${batch.remaining ?? 'unknown'}`);
    }
    if (batch.stopRequested) {
      lines.push('- stop requested: yes');
    }
    if (batch.pauseReason) {
      lines.push(`- pause reason: ${batch.pauseReason}`);
    }
    if (batch.blockers.length > 0) {
      lines.push(`- blockers: ${batch.blockers.map((blocker) => (typeof blocker === 'string' ? blocker : JSON.stringify(blocker))).join('; ')}`);
    }
    if (unfinished.length > 0) {
      lines.push(`- next unfinished: ${unfinished.map((id) => `S${id}`).join(', ')}`);
    }
  }
  lines.push('');

  lines.push('### Next action');
  lines.push('');
  const action = nextAction(roadmap, batch);
  lines.push(`- **${action.headline}**`);
  lines.push(`  ${action.body}`);
  lines.push('');
  return lines.join('\n');
}

function renderDocument(rootDir, roadmap, { includeLive }) {
  const staticPart = renderStatic(roadmap);
  if (!includeLive) {
    return staticPart;
  }
  return `${staticPart}\n${renderLive(rootDir, roadmap)}`;
}

function toJson(rootDir, roadmap) {
  const batch = liveBatch(rootDir);
  const { declared, unfinished, lastDelivered } = progress(roadmap, batch);
  return {
    roadmap: roadmap.roadmap,
    version: roadmap.version,
    active_program: roadmap.active_program,
    program_range: roadmap.program_range,
    declared_sprints: declared,
    completed_sprints: batch.available ? declared.filter((id) => batch.completedSprints.includes(id)) : [],
    unfinished_sprints: unfinished,
    last_delivered_sprint: lastDelivered ? { id: lastDelivered.id, title: lastDelivered.title } : null,
    batch: batch.available
      ? {
          batch_id: batch.batchId,
          status: batch.status,
          runner_status: batch.runnerStatus,
          current_sprint: batch.currentSprint,
          current_phase: batch.currentPhase,
          remaining: batch.remaining,
          next_unfinished: unfinished,
        }
      : null,
    git: liveGit(rootDir),
    next_action: nextAction(roadmap, batch),
  };
}

function main() {
  const rootDir = findRoot();
  const argv = process.argv.slice(2);
  const wantWrite = argv.includes('--write');
  const wantCheck = argv.includes('--check');
  const wantJson = argv.includes('--json');
  const unknown = argv.filter((flag) => !['--write', '--check', '--json'].includes(flag));
  if (unknown.length > 0) {
    console.error(`session-brief: unknown option(s): ${unknown.join(', ')}`);
    process.exit(2);
  }

  const roadmap = loadRoadmap(rootDir);
  const briefPath = path.join(rootDir, BRIEF_RELATIVE_PATH);

  if (wantJson) {
    console.log(JSON.stringify(toJson(rootDir, roadmap), null, 2));
    return;
  }

  if (wantWrite) {
    const content = renderDocument(rootDir, roadmap, { includeLive: false });
    writeFileSync(briefPath, content, 'utf8');
    console.log(`Wrote ${BRIEF_RELATIVE_PATH} (${formatBytes(Buffer.byteLength(content))}).`);
    return;
  }

  if (wantCheck) {
    if (!existsSync(briefPath)) {
      console.error(`${BRIEF_RELATIVE_PATH} is missing. Run: npm run session:brief -- --write`);
      process.exit(1);
    }
    const expected = renderDocument(rootDir, roadmap, { includeLive: false });
    const actual = readFileSync(briefPath, 'utf8').replace(/\r\n/g, '\n');
    if (expected !== actual) {
      console.error(
        `${BRIEF_RELATIVE_PATH} is stale relative to the roadmap.\n`
        + 'Run: npm run session:brief -- --write',
      );
      process.exit(1);
    }
    console.log(`${BRIEF_RELATIVE_PATH} is in sync with the roadmap.`);
    return;
  }

  process.stdout.write(renderDocument(rootDir, roadmap, { includeLive: true }));
  process.stdout.write('\n');
}

main();

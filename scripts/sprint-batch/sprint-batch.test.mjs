import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync, existsSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

import { loadRoadmap, validateDependencies } from './roadmap.mjs';
import {
  acquireLock,
  createBatch,
  findSprintState,
  loadLock,
  loadState,
  markSprint,
  pauseForHuman,
  reconcileSprints,
  recordRepairAttempt,
  releaseLock,
} from './state.mjs';
import { handoffPath, loadHandoff, normalizeHandoff, writeHandoff } from './handoff.mjs';

const CLI = fileURLToPath(new URL('./cli.mjs', import.meta.url));

function sprintEntry(id, dependencies = []) {
  return {
    id,
    key: `sprint-${id}`,
    title: `Sprint ${id}`,
    phase: 'TEST',
    dependencies,
    goal: `Goal ${id}`,
    tasks: [`task ${id}`],
    acceptance: [`acceptance ${id}`],
    gate_profile: 'test',
  };
}

function makeRoot() {
  const root = mkdtempSync(join(tmpdir(), 'kairo-sprint-batch-'));
  mkdirSync(join(root, '.git'));
  mkdirSync(join(root, 'docs', 'roadmap'), { recursive: true });
  return root;
}

function writeRoadmap(root, sprints) {
  const roadmap = {
    roadmap: 'KAIRO_TEST',
    version: 1,
    canonical_active_roadmap: true,
    sprints,
  };
  writeFileSync(
    join(root, 'docs', 'roadmap', 'KAIRO_V2_ROADMAP.json'),
    `${JSON.stringify(roadmap, null, 2)}\n`,
    'utf8',
  );
  return roadmap;
}

function runCli(root, args) {
  return spawnSync(process.execPath, [CLI, ...args], { cwd: root, encoding: 'utf8' });
}

function handoffPayload(sprintId) {
  return {
    sprint_id: sprintId,
    status: 'COMPLETED',
    objective_completed: `Sprint ${sprintId} objective completed`,
    files_added: [],
    files_modified: ['scripts/example.mjs'],
    files_removed: [],
    database_migrations: [],
    public_contract_changes: [],
    architecture_decisions: [],
    new_dependencies: [],
    configuration_changes: [],
    tests_added: ['test/example.test.mjs'],
    tests_changed: [],
    tests_status: 'pass',
    security_implications: [],
    known_limitations: [],
    remaining_followups: [],
    next_sprint_dependencies: [],
    commit_sha: 'deadbeef',
    timestamp: new Date().toISOString(),
  };
}

test('loadRoadmap rejects duplicate ids and missing gate profiles', () => {
  const root = makeRoot();
  try {
    writeRoadmap(root, [sprintEntry(1), sprintEntry(1)]);
    assert.throws(() => loadRoadmap(root), /Duplicate roadmap sprint id/);
    writeRoadmap(root, [sprintEntry(1), sprintEntry(2, [1])]);
    const roadmap = loadRoadmap(root);
    assert.equal(roadmap.sprints.length, 2);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('validateDependencies detects unknown and misordered dependencies', () => {
  const roadmap = {
    sprints: [sprintEntry(1, [2]), sprintEntry(2, [99])],
  };
  const result = validateDependencies(roadmap);
  assert.equal(result.ok, false);
  assert.equal(result.problems.length, 2);
});

test('reconcileSprints appends roadmap sprints missing from an existing batch', () => {
  const root = makeRoot();
  try {
    const initial = { sprints: [sprintEntry(1)] };
    writeRoadmap(root, initial.sprints);
    const roadmap = loadRoadmap(root);
    const state = createBatch({
      rootDir: root,
      count: 1,
      baselineSha: null,
      queueAvailable: false,
      roadmap,
    });
    assert.equal(state.sprints.length, 1);
    const extended = { ...roadmap, sprints: [sprintEntry(1), sprintEntry(2, [1])] };
    const changed = reconcileSprints(root, state, extended);
    assert.equal(changed, true);
    assert.equal(state.sprints.length, 2);
    assert.equal(findSprintState(state, 2).status, 'pending');
    const persisted = loadState(root);
    assert.equal(persisted.sprints.length, 2);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('handoff normalization requires fields, matches the sprint and persists', () => {
  const root = makeRoot();
  try {
    assert.throws(() => normalizeHandoff({ sprint_id: 1 }, 1), /missing required field/);
    const normalized = normalizeHandoff(handoffPayload(1), 1);
    assert.deepEqual(normalized.known_limitations, []);
    assert.throws(() => normalizeHandoff(handoffPayload(2), 1), /does not match/);
    writeHandoff(root, normalized);
    const loaded = loadHandoff(root, 1);
    assert.equal(loaded.sprint_id, 1);
    assert.equal(loaded.tests_status, 'pass');
    assert.ok(existsSync(handoffPath(root, 1)));
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('repair attempts are bounded per sprint', () => {
  const root = makeRoot();
  try {
    const roadmap = writeRoadmap(root, [sprintEntry(1)]);
    const state = createBatch({
      rootDir: root,
      count: 1,
      baselineSha: null,
      queueAvailable: false,
      roadmap,
    });
    assert.equal(recordRepairAttempt(root, state, 1, 'first failure'), 1);
    assert.equal(recordRepairAttempt(root, state, 1, 'second failure'), 2);
    assert.equal(recordRepairAttempt(root, state, 1, 'third failure'), 3);
    assert.equal(state.last_error, 'third failure');
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('a stale lock is taken over safely', () => {
  const root = makeRoot();
  try {
    acquireLock(root, 'batch-a', 'implementing', 1);
    const lock = loadLock(root);
    lock.heartbeat_at = new Date(Date.now() - 90 * 60 * 1000).toISOString();
    writeFileSync(join(root, '.kairo', 'sprint-batch', 'lock.json'), JSON.stringify(lock));
    const taken = acquireLock(root, 'batch-b', 'implementing', 1);
    assert.equal(taken.batch_id, 'batch-b');
    assert.equal(taken.taken_over_at !== undefined, true);
    releaseLock(root);
    acquireLock(root, 'batch-c', 'implementing', 1);
    releaseLock(root);
    assert.ok(existsSync(join(root, '.kairo', 'sprint-batch', 'lock.json.released')));
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('CLI dry-run reports the next sprint without mutating state', () => {
  const root = makeRoot();
  try {
    writeRoadmap(root, [sprintEntry(1)]);
    const result = runCli(root, ['start', '--count', '1', '--dry-run']);
    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /DRY RUN/);
    assert.match(result.stdout, /Sprint 1/);
    assert.equal(existsSync(join(root, '.kairo', 'sprint-batch', 'state.json')), false);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('CLI refuses PASS without a handoff and accepts the full lifecycle with one', () => {
  const root = makeRoot();
  try {
    writeRoadmap(root, [sprintEntry(1), sprintEntry(2, [1])]);
    const start = runCli(root, ['start', '--count', '1']);
    assert.equal(start.status, 0, start.stderr);
    const started = loadState(root);
    assert.equal(started.current_sprint, 1);
    assert.equal(findSprintState(started, 1).status, 'implementing');

    const refused = runCli(root, ['complete', '--sprint', '1', '--verdict', 'PASS', '--summary', 'no handoff']);
    assert.notEqual(refused.status, 0);
    assert.match(refused.stderr, /handoff/);

    const payloadPath = join(root, 'handoff-1.json');
    writeFileSync(payloadPath, JSON.stringify(handoffPayload(1)), 'utf8');
    const handoff = runCli(root, ['handoff', '--sprint', '1', '--file', payloadPath]);
    assert.equal(handoff.status, 0, handoff.stderr);
    assert.ok(existsSync(handoffPath(root, 1)));

    runCli(root, ['preflight', '--sprint', '1']);
    runCli(root, ['verify', '--sprint', '1']);
    runCli(root, ['evaluate', '--sprint', '1']);
    const completed = runCli(root, ['complete', '--sprint', '1', '--verdict', 'PASS', '--summary', 'done']);
    assert.equal(completed.status, 0, completed.stderr);
    const finalState = loadState(root);
    assert.equal(findSprintState(finalState, 1).status, 'completed');
    assert.equal(
      findSprintState(finalState, 1).handoff,
      '.kairo/sprint-batch/handoffs/sprint-1.json',
    );
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('CLI pauses for a human after three repair attempts and resumes explicitly', () => {
  const root = makeRoot();
  try {
    writeRoadmap(root, [sprintEntry(1)]);
    runCli(root, ['start', '--count', '1']);
    assert.equal(runCli(root, ['repair', '--sprint', '1', '--reason', 'gate failure 1']).status, 0);
    assert.equal(runCli(root, ['repair', '--sprint', '1', '--reason', 'gate failure 2']).status, 0);
    const third = runCli(root, ['repair', '--sprint', '1', '--reason', 'gate failure 3']);
    assert.equal(third.status, 2);
    assert.match(third.stdout, /HUMAN STOP REPORT/);
    assert.equal(loadState(root).status, 'paused_for_human');

    const blockedResume = runCli(root, ['resume']);
    assert.equal(blockedResume.status, 2);
    assert.match(blockedResume.stdout, /Resume command: Start Next Sprint Resume/);

    const resumed = runCli(root, ['resume', '--human-resolved']);
    assert.equal(resumed.status, 0, resumed.stderr);
    const state = loadState(root);
    assert.equal(state.status, 'running');
    assert.equal(findSprintState(state, 1).repair_attempts, 0);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('CLI reset archives an orphaned batch and a new start creates a fresh batch', () => {
  const root = makeRoot();
  try {
    writeRoadmap(root, [sprintEntry(1), sprintEntry(2, [1])]);
    const roadmap = loadRoadmap(root);
    createBatch({
      rootDir: root,
      count: 1,
      baselineSha: null,
      queueAvailable: false,
      roadmap,
    });
    const archivedId = loadState(root).batch_id;
    const reset = runCli(root, ['reset', '--reason', 'orphaned runner']);
    assert.equal(reset.status, 0, reset.stderr);
    assert.match(reset.stdout, /archived/);
    assert.equal(loadState(root).status, 'completed');

    const start = runCli(root, ['start', '--count', '2']);
    assert.equal(start.status, 0, start.stderr);
    const fresh = loadState(root);
    assert.notEqual(fresh.batch_id, archivedId);
    assert.equal(fresh.requested_count, 2);
    assert.equal(findSprintState(fresh, 1).status, 'implementing');
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('CLI reset refuses to archive a batch with a sprint in progress', () => {
  const root = makeRoot();
  try {
    writeRoadmap(root, [sprintEntry(1)]);
    runCli(root, ['start', '--count', '1']);
    runCli(root, ['pause', '--reason', 'test pause to release the lock']);
    const reset = runCli(root, ['reset']);
    assert.notEqual(reset.status, 0);
    assert.match(reset.stderr, /in progress/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('pauseHuman records the pause reason and releases the lock', () => {
  const root = makeRoot();
  try {
    const roadmap = writeRoadmap(root, [sprintEntry(1)]);
    const state = createBatch({
      rootDir: root,
      count: 1,
      baselineSha: null,
      queueAvailable: false,
      roadmap,
    });
    acquireLock(root, state.batch_id, 'implementing', 1);
    markSprint(root, state, 1, 'implementing');
    pauseForHuman(root, state, 'production credential required', 1);
    const persisted = loadState(root);
    assert.equal(persisted.status, 'paused_for_human');
    assert.equal(persisted.pause_reason, 'production credential required');
    assert.equal(loadLock(root), null);
    assert.ok(existsSync(join(root, '.kairo', 'sprint-batch', 'lock.json.released')));
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

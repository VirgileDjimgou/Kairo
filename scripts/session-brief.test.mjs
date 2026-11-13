import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const SCRIPT = fileURLToPath(new URL('./session-brief.mjs', import.meta.url));
const REPO_ROOT = fileURLToPath(new URL('..', import.meta.url));

function run(args, cwd) {
  return spawnSync(process.execPath, [SCRIPT, ...args], { cwd, encoding: 'utf8' });
}

function sprint(id) {
  return {
    id,
    key: `sprint-${id}`,
    title: `Sprint ${id}`,
    phase: 'TEST',
    dependencies: id === 100 ? [] : [id - 1],
    goal: `Goal ${id}`,
    tasks: [`task ${id}`],
    acceptance: [`acceptance ${id}`],
    gate_profile: 'default',
  };
}

function roadmapWith(ids) {
  return {
    roadmap: 'KAIRO_V2',
    version: 3,
    active_program: 'TEST_PROGRAM',
    program_range: `S${ids[0]}-S${ids[ids.length - 1]}`,
    objective: 'Test objective.',
    historical_roadmap: 'IMPLEMENTATION_ROADMAP.md',
    canonical_active_roadmap: true,
    sprints: ids.map((id) => sprint(id)),
  };
}

/**
 * Builds a throwaway repository root so the brief can be exercised without
 * touching the real roadmap, batch state or git position.
 */
function fixture({ roadmap, state, brief }) {
  const root = mkdtempSync(join(tmpdir(), 'kairo-session-brief-'));
  mkdirSync(join(root, '.git'), { recursive: true });
  mkdirSync(join(root, 'docs', 'roadmap'), { recursive: true });
  mkdirSync(join(root, 'docs', 'ai'), { recursive: true });
  writeFileSync(
    join(root, 'docs', 'roadmap', 'KAIRO_V2_ROADMAP.json'),
    JSON.stringify(roadmap, null, 2),
    'utf8',
  );
  if (state !== undefined) {
    mkdirSync(join(root, '.kairo', 'sprint-batch'), { recursive: true });
    writeFileSync(
      join(root, '.kairo', 'sprint-batch', 'state.json'),
      JSON.stringify(state, null, 2),
      'utf8',
    );
  }
  if (brief !== undefined) {
    writeFileSync(join(root, 'docs', 'ai', 'SESSION_BRIEF.md'), brief, 'utf8');
  }
  return root;
}

function batchState({ status, completed, currentSprint = null }) {
  return {
    batch_id: 'test-batch',
    status,
    runner_status: 'RUNNING',
    requested_count: 1,
    completed_count: 0,
    current_sprint: currentSprint,
    current_phase: null,
    batch_remaining: 1,
    queue_available: false,
    stop_requested: false,
    blockers: [],
    pause_reason: null,
    last_successful_gate: null,
    sprints: completed.map((id) => ({ id, title: `Sprint ${id}`, status: 'completed' })),
  };
}

test('committed session brief matches the canonical roadmap', () => {
  const result = run(['--check'], REPO_ROOT);
  assert.equal(result.status, 0, `expected the brief to be in sync: ${result.stderr}`);
  assert.ok(existsSync(join(REPO_ROOT, 'docs', 'ai', 'SESSION_BRIEF.md')));
});

test('--write then --check is deterministic', () => {
  const root = fixture({ roadmap: roadmapWith([100, 101]) });
  try {
    const write = run(['--write'], root);
    assert.equal(write.status, 0, write.stderr);
    const first = readFileSync(join(root, 'docs', 'ai', 'SESSION_BRIEF.md'), 'utf8');
    const rewrite = run(['--write'], root);
    assert.equal(rewrite.status, 0, rewrite.stderr);
    const second = readFileSync(join(root, 'docs', 'ai', 'SESSION_BRIEF.md'), 'utf8');
    assert.equal(first, second);
    assert.equal(run(['--check'], root).status, 0);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('--check fails when a roadmap change is not reflected in the brief', () => {
  const root = fixture({ roadmap: roadmapWith([100, 101]), brief: '# stale\n' });
  try {
    const result = run(['--check'], root);
    assert.equal(result.status, 1);
    assert.match(result.stderr, /stale/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('the brief reports an orphaned running batch instead of leaving it ambiguous', () => {
  const root = fixture({
    roadmap: roadmapWith([100, 101]),
    state: batchState({ status: 'running', completed: [100, 101] }),
  });
  try {
    const result = run([], root);
    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /sprints are completed, but batch test-batch is still `running`/);
    assert.match(result.stdout, /sprint:batch:reset/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('the brief names the next unfinished sprint when the batch has work left', () => {
  const root = fixture({
    roadmap: roadmapWith([100, 101]),
    state: batchState({ status: 'running', completed: [100] }),
  });
  try {
    const result = run([], root);
    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /next unfinished: S101/i);
    assert.match(result.stdout, /Execute the next unfinished sprint: S101 \(Sprint 101\)/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('--json exposes the machine-readable program state', () => {
  const result = run(['--json'], REPO_ROOT);
  assert.equal(result.status, 0, result.stderr);
  const brief = JSON.parse(result.stdout);
  assert.equal(brief.roadmap, 'KAIRO_V2');
  assert.ok(brief.declared_sprints.length > 0);
  assert.ok(brief.active_program);
  assert.ok(brief.next_action.headline);
  assert.deepEqual(
    [...brief.declared_sprints].sort((left, right) => left - right),
    [...brief.completed_sprints, ...brief.unfinished_sprints].sort((left, right) => left - right),
  );
});

import {
  existsSync,
  mkdirSync,
  readFileSync,
  renameSync,
  rmSync,
  writeFileSync,
} from 'node:fs';
import { join } from 'node:path';

export const STATE_DIR_RELATIVE = '.kairo/sprint-batch';
export const STATE_STATUSES = [
  'idle',
  'running',
  'paused',
  'paused_for_human',
  'blocked',
  'completed',
  'failed',
];
export const SPRINT_STATUSES = [
  'pending',
  'preflight',
  'implementing',
  'verifying',
  'evaluating',
  'completed',
  'paused',
  'blocked',
  'failed',
];

const STALE_LOCK_MS = 60 * 60 * 1000;
const STALE_DEAD_PROCESS_MS = 5 * 60 * 1000;

export function stateDir(rootDir) {
  return join(rootDir, STATE_DIR_RELATIVE);
}

export function statePath(rootDir) {
  return join(stateDir(rootDir), 'state.json');
}

export function lockPath(rootDir) {
  return join(stateDir(rootDir), 'lock.json');
}

export function historyPath(rootDir) {
  return join(stateDir(rootDir), 'history.json');
}

export function reportsDir(rootDir) {
  return join(stateDir(rootDir), 'reports');
}

export function handoffsDir(rootDir) {
  return join(stateDir(rootDir), 'handoffs');
}

export function ensureStateDir(rootDir) {
  mkdirSync(reportsDir(rootDir), { recursive: true });
  mkdirSync(handoffsDir(rootDir), { recursive: true });
}

export function readJsonFile(path, fallback = null) {
  if (!existsSync(path)) {
    return fallback;
  }
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (error) {
    throw new Error(`Unable to parse ${path}: ${error.message}`);
  }
}

export function writeJsonFile(path, value) {
  const tmp = `${path}.tmp`;
  writeFileSync(tmp, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
  renameSync(tmp, path);
}

export function loadState(rootDir) {
  return readJsonFile(statePath(rootDir), null);
}

export function runnerStatusFrom(status) {
  switch (status) {
    case 'idle':
      return 'IDLE';
    case 'running':
      return 'RUNNING';
    case 'paused':
    case 'paused_for_human':
      return 'PAUSED_FOR_HUMAN';
    case 'blocked':
      return 'BLOCKED';
    case 'failed':
      return 'FAILED';
    case 'completed':
      return 'COMPLETED';
    default:
      return String(status ?? 'IDLE').toUpperCase();
  }
}

export function refreshDerivedState(state) {
  const requested = Number.isFinite(state.requested_count) ? state.requested_count : 0;
  const completed = Number.isFinite(state.completed_count) ? state.completed_count : 0;
  state.batch_requested = requested;
  state.batch_completed = completed;
  state.batch_remaining = Math.max(0, requested - completed);
  const sprint = state.current_sprint !== null && state.current_sprint !== undefined
    ? findSprintState(state, state.current_sprint)
    : null;
  state.sprint_status = sprint?.status ?? state.current_phase ?? null;
  state.runner_status = runnerStatusFrom(state.status);
  return state;
}

export function saveState(rootDir, state) {
  refreshDerivedState(state);
  state.updated_at = new Date().toISOString();
  ensureStateDir(rootDir);
  const lock = existsSync(lockPath(rootDir)) ? readJsonFile(lockPath(rootDir), null) : null;
  if (lock && lock.batch_id === state.batch_id) {
    state.lock_owner = lock.pid ?? null;
    state.heartbeat = lock.heartbeat_at ?? null;
  }
  writeJsonFile(statePath(rootDir), state);
  return state;
}

export function loadLock(rootDir) {
  return readJsonFile(lockPath(rootDir), null);
}

export function writeLock(rootDir, lock) {
  ensureStateDir(rootDir);
  writeJsonFile(lockPath(rootDir), lock);
}

export function releaseLock(rootDir) {
  const path = lockPath(rootDir);
  if (existsSync(path)) {
    const lock = readJsonFile(path, null);
    if (lock) {
      lock.released_at = new Date().toISOString();
      writeJsonFile(path, lock);
    }
    // Rename to a released marker so stale detection never trips on a closed lock.
    const releasedPath = `${path}.released`;
    if (existsSync(releasedPath)) {
      rmSync(releasedPath, { force: true });
    }
    renameSync(path, releasedPath);
  }
}

export function heartbeat(rootDir, batchId, phase, sprintId = null) {
  const lock = loadLock(rootDir);
  if (!lock || lock.batch_id !== batchId) {
    return;
  }
  lock.heartbeat_at = new Date().toISOString();
  lock.phase = phase;
  lock.current_sprint = sprintId;
  writeLock(rootDir, lock);
}

export function isProcessAlive(pid) {
  if (!pid || typeof pid !== 'number') {
    return false;
  }
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    return error && error.code === 'EPERM';
  }
}

export function lockAgeMs(lock) {
  const stamp = lock.heartbeat_at ?? lock.started_at ?? lock.created_at;
  if (!stamp) {
    return Number.POSITIVE_INFINITY;
  }
  return Date.now() - new Date(stamp).getTime();
}

export function isLockStale(lock) {
  if (!lock) {
    return true;
  }
  const age = lockAgeMs(lock);
  if (age > STALE_LOCK_MS) {
    return true;
  }
  if (!isProcessAlive(lock.pid) && age > STALE_DEAD_PROCESS_MS) {
    return true;
  }
  return false;
}

export class LockConflictError extends Error {
  constructor(lock) {
    super(
      `Another sprint batch appears active (batch ${lock.batch_id}, pid ${lock.pid ?? 'unknown'}, heartbeat ${lock.heartbeat_at ?? 'unknown'}). `
      + 'Run "npm run sprint:batch:status" and either resume it or wait for staleness before starting a new batch.',
    );
    this.name = 'LockConflictError';
    this.lock = lock;
  }
}

export function acquireLock(rootDir, batchId, phase = 'starting', sprintId = null) {
  ensureStateDir(rootDir);
  const existing = loadLock(rootDir);
  let takeover = null;
  if (existing && existing.batch_id !== batchId) {
    if (!isLockStale(existing)) {
      throw new LockConflictError(existing);
    }
    takeover = existing.batch_id;
  }
  const now = new Date().toISOString();
  const lock = {
    batch_id: batchId,
    pid: process.pid,
    cwd: rootDir,
    started_at: existing && existing.batch_id === batchId ? existing.started_at : now,
    heartbeat_at: now,
    phase,
    current_sprint: sprintId,
  };
  if (takeover) {
    lock.taken_over_at = now;
    lock.taken_over_from = takeover;
  }
  writeLock(rootDir, lock);
  return lock;
}

function dailySequence(rootDir, dateStamp) {
  const history = readJsonFile(historyPath(rootDir), { batches: [] });
  const count = (history.batches ?? []).filter((entry) => entry.batch_id.startsWith(dateStamp)).length;
  return String(count + 1).padStart(3, '0');
}

export function recordBatch(rootDir, entry) {
  const history = readJsonFile(historyPath(rootDir), { batches: [] });
  history.batches = history.batches ?? [];
  history.batches.unshift(entry);
  history.batches = history.batches.slice(0, 200);
  ensureStateDir(rootDir);
  writeJsonFile(historyPath(rootDir), history);
}

export function completedSprintsFromHistory(rootDir) {
  const history = readJsonFile(historyPath(rootDir), { batches: [] });
  const completed = new Map();
  for (const batch of history.batches ?? []) {
    for (const sprint of batch.sprints ?? []) {
      if (sprint.status !== 'completed') {
        continue;
      }
      if (!completed.has(sprint.id)) {
        completed.set(sprint.id, sprint.completed_at ?? null);
      }
    }
  }
  return completed;
}

export function newBatchId(rootDir) {
  const now = new Date();
  const dateStamp = now.toISOString().slice(0, 10);
  return `${dateStamp}-${dailySequence(rootDir, dateStamp)}`;
}

export function createBatch({
  rootDir,
  count,
  baselineSha,
  queueAvailable,
  roadmap,
  inheritedCompleted = new Map(),
}) {
  const batchId = newBatchId(rootDir);
  const sprintEntries = roadmap.sprints.map((sprint) => {
    const inheritedCompletedAt = inheritedCompleted.get(sprint.id);
    if (inheritedCompletedAt !== undefined) {
      return {
        id: sprint.id,
        title: sprint.title,
        status: 'completed',
        inherited: true,
        attempts: 0,
        repair_attempts: 0,
        started_at: null,
        completed_at: inheritedCompletedAt ?? new Date().toISOString(),
        verification: { inherited: true },
        summary: 'Completed in an earlier batch; inherited for dependency tracking.',
        handoff: null,
        last_error: null,
      };
    }
    return {
      id: sprint.id,
      title: sprint.title,
      status: 'pending',
      attempts: 0,
      repair_attempts: 0,
      started_at: null,
      completed_at: null,
      verification: {},
      summary: null,
      handoff: null,
      last_error: null,
    };
  });
  const state = {
    batch_id: batchId,
    roadmap: roadmap.roadmap,
    status: 'running',
    requested_count: count,
    completed_count: 0,
    current_sprint: null,
    current_phase: null,
    started_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    baseline_sha: baselineSha,
    stop_requested: false,
    queue_available: queueAvailable,
    blockers: [],
    last_successful_gate: null,
    pause_reason: null,
    last_error: null,
    repair_attempt: 0,
    lock_owner: null,
    heartbeat: null,
    sprints: sprintEntries,
  };
  return saveState(rootDir, state);
}

export function findSprintState(state, id) {
  return state.sprints.find((sprint) => sprint.id === id) ?? null;
}

export function markSprint(rootDir, state, id, status, extra = {}) {
  if (!SPRINT_STATUSES.includes(status)) {
    throw new Error(`Unsupported sprint status: ${status}`);
  }
  const sprint = findSprintState(state, id);
  if (!sprint) {
    throw new Error(`Sprint ${id} is not part of the current batch`);
  }
  sprint.status = status;
  sprint.updated_at = new Date().toISOString();
  if (status === 'implementing' && !sprint.started_at) {
    sprint.started_at = new Date().toISOString();
  }
  if (status === 'completed') {
    sprint.completed_at = new Date().toISOString();
    state.last_successful_gate = `S${id} completed`;
  }
  Object.assign(sprint, extra);
  state.current_sprint = id;
  state.current_phase = status;
  state.completed_count = state.sprints.filter(
    (entry) => entry.status === 'completed' && !entry.inherited,
  ).length;
  return saveState(rootDir, state);
}

export function reconcileSprints(rootDir, state, roadmap, { persist = true } = {}) {
  if (!state || !Array.isArray(state.sprints) || !roadmap || !Array.isArray(roadmap.sprints)) {
    return false;
  }
  let changed = false;
  for (const sprint of roadmap.sprints) {
    const existing = findSprintState(state, sprint.id);
    if (!existing) {
      state.sprints.push({
        id: sprint.id,
        title: sprint.title,
        status: 'pending',
        attempts: 0,
        repair_attempts: 0,
        started_at: null,
        completed_at: null,
        verification: {},
        summary: null,
        handoff: null,
        last_error: null,
      });
      changed = true;
    } else if (existing.title !== sprint.title) {
      existing.title = sprint.title;
      changed = true;
    }
  }
  if (changed) {
    state.sprints.sort((left, right) => left.id - right.id);
    if (persist) {
      saveState(rootDir, state);
    }
  }
  return changed;
}

export function recordRepairAttempt(rootDir, state, id, reason) {
  const sprint = findSprintState(state, id);
  if (!sprint) {
    throw new Error(`Sprint ${id} is not part of the current batch`);
  }
  sprint.repair_attempts = (sprint.repair_attempts ?? 0) + 1;
  sprint.last_error = reason ?? 'verification failure';
  state.repair_attempt = sprint.repair_attempts;
  state.last_error = sprint.last_error;
  saveState(rootDir, state);
  return sprint.repair_attempts;
}

export function pauseForHuman(rootDir, state, reason, sprintId = null) {
  state.status = 'paused_for_human';
  state.pause_reason = reason ?? 'human intervention required';
  state.last_error = state.pause_reason;
  if (sprintId !== null && sprintId !== undefined) {
    state.current_sprint = sprintId;
  }
  saveState(rootDir, state);
  releaseLock(rootDir);
  return state;
}

export function requestStop(rootDir, state, reason = 'operator stop requested') {
  state.stop_requested = true;
  state.stop_reason = reason;
  if (state.status === 'running') {
    state.status = 'paused';
  }
  if (state.status === 'idle') {
    state.status = 'paused';
  }
  return saveState(rootDir, state);
}

export function clearStop(state) {
  state.stop_requested = false;
  delete state.stop_reason;
  return state;
}

export function isStopRequested(rootDir, state) {
  if (!state) {
    return false;
  }
  const latest = loadState(rootDir);
  return Boolean(latest?.stop_requested ?? state.stop_requested);
}

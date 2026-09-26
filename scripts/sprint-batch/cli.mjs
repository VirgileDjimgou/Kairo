#!/usr/bin/env node
import { existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import {
  acquireLock,
  clearStop,
  completedSprintsFromHistory,
  createBatch,
  ensureStateDir,
  findSprintState,
  heartbeat,
  isStopRequested,
  loadLock,
  loadState,
  LockConflictError,
  markSprint,
  recordBatch,
  releaseLock,
  requestStop,
  saveState,
} from './state.mjs';
import {
  dependenciesSatisfied,
  findRoot,
  getSprint,
  loadRoadmap,
  nextUnfinishedSprint,
} from './roadmap.mjs';
import {
  buildBatchReport,
  buildStatusReport,
  formatSprintSpec,
  writeBatchReport,
  writeSprintReport,
} from './report.mjs';
import { formatDoctor, runDoctor } from './doctor.mjs';

const MAX_BATCH = 10;
const TERMINAL_STATES = new Set(['completed', 'failed', 'idle']);

function fail(message, code = 1) {
  console.error(message);
  process.exit(code);
}

function gitSha(rootDir) {
  const result = spawnSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8', cwd: rootDir });
  return result.status === 0 ? result.stdout.trim() : null;
}

function parseArgs(argv) {
  const options = { count: null, resume: false, json: false, sprint: null, reason: null, summary: null, verdict: null };
  const positional = [];
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--resume') {
      options.resume = true;
    } else if (arg === '--json') {
      options.json = true;
    } else if (arg === '--count') {
      options.count = Number(argv[index + 1]);
      index += 1;
    } else if (arg === '--sprint') {
      options.sprint = Number(argv[index + 1]);
      index += 1;
    } else if (arg === '--reason') {
      options.reason = argv[index + 1];
      index += 1;
    } else if (arg === '--summary') {
      options.summary = argv[index + 1];
      index += 1;
    } else if (arg === '--verdict') {
      options.verdict = argv[index + 1];
      index += 1;
    } else if (/^\d+$/.test(arg)) {
      positional.push(Number(arg));
    } else {
      positional.push(arg);
    }
  }
  if (options.count === null && positional.length > 0 && typeof positional[0] === 'number') {
    options.count = positional[0];
  }
  if (options.reason === null && positional.length > 1 && typeof positional[1] === 'string') {
    options.reason = positional.slice(1).join(' ');
  }
  return options;
}

function queueAvailable(rootDir) {
  const candidates = [
    `${rootDir}/.opencode/node_modules/opencode-queue`,
    `${rootDir}/.opencode/node_modules/@opencode/queue`,
  ];
  return candidates.some((path) => existsSync(path));
}

function requireState(rootDir) {
  const state = loadState(rootDir);
  if (!state) {
    fail('No sprint batch state found. Start one with: npm run sprint:batch:start -- 10', 1);
  }
  return state;
}

function currentSprintFor(rootDir, state, roadmap, requestedId) {
  let sprint = null;
  if (requestedId !== null && requestedId !== undefined && !Number.isNaN(requestedId)) {
    sprint = getSprint(roadmap, requestedId);
    if (!sprint) {
      fail(`Sprint ${requestedId} is not part of roadmap ${roadmap.roadmap}.`);
    }
  } else {
    sprint = nextUnfinishedSprint(roadmap, state);
  }
  if (!sprint) {
    return null;
  }
  const dependencies = dependenciesSatisfied(roadmap, state, sprint);
  if (!dependencies.ok) {
    fail(
      `Sprint ${sprint.id} depends on unfinished sprint(s): ${dependencies.blocking.join(', ')}. No sprint skipping is allowed.`,
      2,
    );
  }
  return sprint;
}

function beginSprint(rootDir, roadmap, state, sprint, batchStarted = false) {
  acquireLock(rootDir, state.batch_id, 'implementing', sprint.id);
  const sprintState = findSprintState(state, sprint.id);
  const attempts = (sprintState?.attempts ?? 0) + 1;
  markSprint(rootDir, state, sprint.id, 'implementing', { attempts });
  heartbeat(rootDir, state.batch_id, 'implementing', sprint.id);
  return { attempts, batchStarted };
}

function printStartOutput(rootDir, roadmap, state, sprint, attempts) {
  const completed = state.sprints
    .filter((entry) => entry.status === 'completed' && !entry.inherited)
    .map((entry) => entry.id);
  const inherited = state.sprints
    .filter((entry) => entry.status === 'completed' && entry.inherited)
    .map((entry) => entry.id);
  console.log(`Batch ${state.batch_id} is RUNNING (requested ${state.requested_count}, completed this batch ${completed.length}).`);
  console.log(`Baseline SHA: ${state.baseline_sha ?? 'unknown'}`);
  console.log(`Queue: ${state.queue_available ? 'available' : 'not available'}`);
  if (inherited.length > 0) {
    console.log(`Inherited completed sprints: ${inherited.map((id) => `S${id}`).join(', ')}`);
  }
  if (completed.length > 0) {
    console.log(`Already completed in this batch: ${completed.map((id) => `S${id}`).join(', ')}`);
  } else if (attempts > 1) {
    console.log(`Sprint ${sprint.id} attempt ${attempts}.`);
  }
  console.log('');
  console.log(formatSprintSpec(sprint));
  console.log('Executor instructions:');
  console.log('  1. Read prompts/KAIRO_SPRINT_BATCH_EXECUTOR.md and prompts/KAIRO_SPRINT_EXECUTOR.md.');
  console.log('  2. Read the sprint sections of docs/roadmap/KAIRO_V2_ROADMAP.md.');
  console.log('  3. Inspect the current implementation before editing.');
  console.log(`  4. Record phase transitions with "node scripts/sprint-batch/cli.mjs verify --sprint ${sprint.id}" and "... evaluate --sprint ${sprint.id}".`);
  console.log(`  5. Complete with "node scripts/sprint-batch/cli.mjs complete --sprint ${sprint.id} --verdict PASS --summary \\"...\\"".`);
  console.log('  6. Then continue immediately with the next sprint until the requested count is reached.');
}

function commandStart(rootDir, options) {
  const roadmap = loadRoadmap(rootDir);
  const requested = options.count ?? 1;
  const count = Math.max(1, Math.min(MAX_BATCH, requested));
  if (requested > MAX_BATCH) {
    console.log(`Requested ${requested} sprints; the autonomous batch maximum is ${MAX_BATCH}. Capped at ${MAX_BATCH}. Start another batch afterwards.`);
  }
  const existing = loadState(rootDir);
  if (existing && !TERMINAL_STATES.has(existing.status)) {
    if (!options.resume) {
      fail(
        `Batch ${existing.batch_id} is ${existing.status} with ${existing.completed_count}/${existing.requested_count} sprints completed.\n`
        + 'Use "npm run sprint:batch:resume" to continue it, or "npm run sprint:batch:stop" to pause it before starting a new batch.',
        2,
      );
    }
    return commandResume(rootDir, options, existing, roadmap);
  }
  if (existing && TERMINAL_STATES.has(existing.status) && existing.status !== 'idle') {
    recordBatch(rootDir, {
      batch_id: existing.batch_id,
      status: existing.status,
      requested_count: existing.requested_count,
      completed_count: existing.completed_count,
      started_at: existing.started_at ?? null,
      finished_at: existing.updated_at ?? null,
      sprints: (existing.sprints ?? []).map((sprint) => ({
        id: sprint.id,
        status: sprint.status,
        completed_at: sprint.completed_at ?? null,
        summary: sprint.summary ?? null,
      })),
    });
  }
  const state = createBatch({
    rootDir,
    count,
    baselineSha: gitSha(rootDir),
    queueAvailable: queueAvailable(rootDir),
    roadmap,
    inheritedCompleted: completedSprintsFromHistory(rootDir),
  });
  const sprint = currentSprintFor(rootDir, state, roadmap, options.sprint);
  if (!sprint) {
    fail('All roadmap sprints are already complete. Nothing to start.', 0);
  }
  const { attempts } = beginSprint(rootDir, roadmap, state, sprint);
  if (options.json) {
    console.log(JSON.stringify({ batch: state.batch_id, status: state.status, sprint: sprint.id, attempts }, null, 2));
    return;
  }
  printStartOutput(rootDir, roadmap, state, sprint, attempts);
}

function commandResume(rootDir, options, existingState, roadmap) {
  const state = existingState ?? requireState(rootDir);
  if (TERMINAL_STATES.has(state.status) && state.completed_count >= state.requested_count) {
    console.log(`Batch ${state.batch_id} is already ${state.status}. Nothing to resume.`);
    return;
  }
  state.status = 'running';
  clearStop(state);
  saveState(rootDir, state);
  const sprint = currentSprintFor(rootDir, state, roadmap, options.sprint ?? state.current_sprint);
  if (!sprint) {
    console.log('All sprints in this batch are complete.');
    return;
  }
  const sprintState = findSprintState(state, sprint.id);
  const resumedPhase = sprintState?.status === 'completed' ? 'pending' : (sprintState?.status ?? 'pending');
  const { attempts } = beginSprint(rootDir, roadmap, state, sprint);
  if (options.json) {
    console.log(JSON.stringify({ batch: state.batch_id, status: state.status, sprint: sprint.id, resumed_from: resumedPhase }, null, 2));
    return;
  }
  console.log(`Resuming batch ${state.batch_id} (resumed sprint ${sprint.id} from phase ${resumedPhase}).`);
  console.log('');
  printStartOutput(rootDir, roadmap, state, sprint, attempts);
}

function commandBegin(rootDir, options) {
  const roadmap = loadRoadmap(rootDir);
  let state = loadState(rootDir);
  if (!state || TERMINAL_STATES.has(state.status)) {
    return commandStart(rootDir, { ...options, resume: false });
  }
  return commandResume(rootDir, options, state, roadmap);
}

function commandPhase(rootDir, options, phase) {
  const roadmap = loadRoadmap(rootDir);
  const state = requireState(rootDir);
  const sprint = currentSprintFor(rootDir, state, roadmap, options.sprint ?? state.current_sprint);
  if (!sprint) {
    fail('No unfinished sprint found in the current batch.', 1);
  }
  markSprint(rootDir, state, sprint.id, phase);
  heartbeat(rootDir, state.batch_id, phase, sprint.id);
  if (options.json) {
    console.log(JSON.stringify({ sprint: sprint.id, phase }, null, 2));
  } else {
    console.log(`Sprint ${sprint.id} phase set to ${phase.toUpperCase()}.`);
  }
}

function batchSummaryFromSprint(rootDir, state, sprint, verdict, options) {
  state.completed_count = state.sprints.filter(
    (entry) => entry.status === 'completed' && !entry.inherited,
  ).length;
  const remaining = state.requested_count - state.completed_count;
  const next = nextUnfinishedSprint(loadRoadmap(rootDir), state);
  const stop = isStopRequested(rootDir, state);
  const reportPath = writeSprintReport(rootDir, sprint, {
    batchId: state.batch_id,
    verdict,
    summary: options.summary ?? null,
    gitSha: gitSha(rootDir),
  });
  console.log(`Sprint report written: ${reportPath}`);
  if (!next) {
    state.status = 'completed';
    state.current_phase = null;
    saveState(rootDir, state);
    releaseLock(rootDir);
    const batchPath = writeBatchReport(rootDir, state, loadRoadmap(rootDir));
    console.log('');
    console.log(buildBatchReport(state, loadRoadmap(rootDir)));
    console.log(`Batch report written: ${batchPath}`);
    return;
  }
  if (remaining <= 0 || stop) {
    state.status = stop ? 'paused' : 'completed';
    state.current_phase = null;
    saveState(rootDir, state);
    releaseLock(rootDir);
    const batchPath = writeBatchReport(rootDir, state, loadRoadmap(rootDir));
    console.log('');
    console.log(buildBatchReport(state, loadRoadmap(rootDir)));
    console.log(`Batch report written: ${batchPath}`);
    if (stop) {
      console.log('Operator stop was requested and honoured at a safe checkpoint.');
    }
    return;
  }
  heartbeat(rootDir, state.batch_id, 'between-sprints', sprint.id);
  console.log('');
  console.log(`Progress: ${state.completed_count}/${state.requested_count} sprints completed in batch ${state.batch_id}.`);
  console.log(`Next unfinished sprint: S${next.id} — ${next.title}`);
  console.log('Continue immediately with the next sprint. Do not wait for the operator.');
}

function commandComplete(rootDir, options) {
  const roadmap = loadRoadmap(rootDir);
  const state = requireState(rootDir);
  const sprint = currentSprintFor(rootDir, state, roadmap, options.sprint ?? state.current_sprint);
  if (!sprint) {
    fail('No unfinished sprint found in the current batch.', 1);
  }
  const verdict = (options.verdict ?? 'PASS').toUpperCase();
  if (!['PASS', 'BLOCKED', 'FAILED'].includes(verdict)) {
    fail('Verdict must be PASS, BLOCKED or FAILED.', 1);
  }
  if (verdict === 'PASS') {
    const sprintState = findSprintState(state, sprint.id);
    if (sprintState && sprintState.status !== 'completed') {
      markSprint(rootDir, state, sprint.id, 'verifying');
      markSprint(rootDir, state, sprint.id, 'evaluating');
      markSprint(rootDir, state, sprint.id, 'completed', {
        verification: { self_review: true },
      });
    } else {
      markSprint(rootDir, state, sprint.id, 'completed');
    }
    batchSummaryFromSprint(rootDir, state, sprint, 'PASS', options);
    return;
  }
  markSprint(rootDir, state, sprint.id, verdict === 'BLOCKED' ? 'blocked' : 'failed', {
    summary: options.summary ?? null,
  });
  state.completed_count = state.sprints.filter((entry) => entry.status === 'completed').length;
  state.status = verdict === 'BLOCKED' ? 'blocked' : 'failed';
  state.current_phase = verdict.toLowerCase();
  if (options.summary) {
    state.blockers.push(`S${sprint.id}: ${options.summary}`);
  }
  saveState(rootDir, state);
  releaseLock(rootDir);
  writeSprintReport(rootDir, sprint, {
    batchId: state.batch_id,
    verdict,
    summary: options.summary ?? null,
    gitSha: gitSha(rootDir),
  });
  const batchPath = writeBatchReport(rootDir, state, roadmap);
  console.log(buildBatchReport(state, roadmap));
  console.log(`Batch report written: ${batchPath}`);
  if (options.summary) {
    console.log(`Stop condition: ${options.summary}`);
  }
  process.exitCode = 2;
}

function commandStop(rootDir, options) {
  const state = loadState(rootDir);
  if (!state || TERMINAL_STATES.has(state.status)) {
    console.log('No active batch to stop.');
    return;
  }
  requestStop(rootDir, state, options.reason ?? 'operator stop requested');
  const lock = loadLock(rootDir);
  if (lock && !lock.released_at && loadState(rootDir)?.batch_id === lock.batch_id) {
    heartbeat(rootDir, state.batch_id, 'stop-requested', state.current_sprint);
    console.log(`Stop requested for batch ${state.batch_id}. The running agent will pause at the next safe checkpoint.`);
  } else {
    releaseLock(rootDir);
    console.log(`Batch ${state.batch_id} set to PAUSED (no active agent lock).`);
  }
}

function commandPause(rootDir) {
  const state = requireState(rootDir);
  requestStop(rootDir, state, 'operator pause');
  state.status = 'paused';
  saveState(rootDir, state);
  releaseLock(rootDir);
  console.log(`Batch ${state.batch_id} paused.`);
}

function commandStatus(rootDir, options) {
  const roadmap = loadRoadmap(rootDir);
  const state = loadState(rootDir);
  const lock = loadLock(rootDir);
  if (options.json) {
    console.log(JSON.stringify({ state, lock }, null, 2));
    return;
  }
  console.log(buildStatusReport(state, roadmap));
  if (lock && !lock.released_at) {
    console.log(`Active lock: batch ${lock.batch_id}, phase ${lock.phase ?? 'unknown'}, heartbeat ${lock.heartbeat_at ?? 'unknown'}`);
  }
}

function commandDoctor(rootDir, options) {
  const result = runDoctor(rootDir);
  if (options.json) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    console.log(formatDoctor(result));
  }
  if (!result.ok) {
    process.exitCode = 1;
  }
}

function commandReport(rootDir) {
  const roadmap = loadRoadmap(rootDir);
  const state = loadState(rootDir);
  if (!state) {
    console.log('No batch state found.');
    return;
  }
  const path = writeBatchReport(rootDir, state, roadmap);
  console.log(buildBatchReport(state, roadmap));
  console.log(`Batch report written: ${path}`);
}

function commandNext(rootDir, options) {
  return commandBegin(rootDir, options);
}

function commandRoadmap(rootDir, options) {
  const roadmap = loadRoadmap(rootDir);
  if (options.json) {
    console.log(JSON.stringify(roadmap, null, 2));
    return;
  }
  console.log(`Roadmap ${roadmap.roadmap} (v${roadmap.version})`);
  for (const sprint of roadmap.sprints) {
    console.log(`  S${sprint.id} [${sprint.phase}] ${sprint.title}`);
  }
}

function main() {
  const [command, ...rest] = process.argv.slice(2);
  const options = parseArgs(rest);
  const rootDir = findRoot();
  ensureStateDir(rootDir);
  switch (command) {
    case 'start':
      commandStart(rootDir, options);
      break;
    case 'resume':
      commandResume(rootDir, options, null, loadRoadmap(rootDir));
      break;
    case 'next':
    case 'begin':
      commandNext(rootDir, options);
      break;
    case 'verify':
      commandPhase(rootDir, options, 'verifying');
      break;
    case 'evaluate':
      commandPhase(rootDir, options, 'evaluating');
      break;
    case 'complete':
      commandComplete(rootDir, options);
      break;
    case 'block':
      commandComplete(rootDir, { ...options, verdict: 'BLOCKED' });
      break;
    case 'fail':
      commandComplete(rootDir, { ...options, verdict: 'FAILED' });
      break;
    case 'stop':
      commandStop(rootDir, options);
      break;
    case 'pause':
      commandPause(rootDir);
      break;
    case 'status':
      commandStatus(rootDir, options);
      break;
    case 'doctor':
      commandDoctor(rootDir, options);
      break;
    case 'report':
      commandReport(rootDir);
      break;
    case 'roadmap':
      commandRoadmap(rootDir, options);
      break;
    default:
      console.log('Kairo sprint batch CLI');
      console.log('');
      console.log('Commands:');
      console.log('  start [N|--count N] [--resume]   start or resume a batch');
      console.log('  resume                            resume the incomplete batch');
      console.log('  next|begin                        mark and print the next sprint');
      console.log('  verify --sprint N                 mark the sprint verifying');
      console.log('  evaluate --sprint N               mark the sprint evaluating');
      console.log('  complete --sprint N [--verdict PASS|BLOCKED|FAILED] [--summary TEXT]');
      console.log('  block|fail --sprint N --reason TEXT');
      console.log('  stop | pause                      request stop / pause the batch');
      console.log('  status [--json]                   batch status');
      console.log('  doctor [--json]                   environment checks');
      console.log('  report                            write and print the batch report');
      console.log('  roadmap [--json]                  list roadmap sprints');
      if (command) {
        process.exitCode = 1;
      }
  }
}

try {
  main();
} catch (error) {
  if (error instanceof LockConflictError) {
    console.error(error.message);
    process.exit(3);
  }
  console.error(`Sprint batch error: ${error.message}`);
  process.exit(1);
}

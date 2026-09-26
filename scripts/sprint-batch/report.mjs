import { existsSync, mkdirSync, readdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { getSprint, nextRoadmapSprintAfter, nextUnfinishedSprint } from './roadmap.mjs';
import { reportsDir, stateDir } from './state.mjs';

function line(value = '') {
  return `${value}\n`;
}

export function sprintStatusLabel(status) {
  return String(status ?? 'unknown').toUpperCase();
}

export function buildStatusReport(state, roadmap) {
  if (!state) {
    return [
      '## Kairo Sprint Batch',
      '',
      'No batch state found.',
      '',
      'Start one with:',
      '  npm run sprint:batch:start -- 10',
      '  /start-next-sprints 10',
      '',
    ].join('\n');
  }

  const currentSprint = state.current_sprint
    ? getSprint(roadmap, state.current_sprint)
    : nextUnfinishedSprint(roadmap, state);
  const remainingInBatch = Math.max(0, state.requested_count - state.completed_count);
  const nextUnfinished = nextUnfinishedSprint(roadmap, state);
  const nextAfterBatch = state.current_sprint
    ? nextRoadmapSprintAfter(roadmap, state.current_sprint)
    : nextUnfinished;

  const recent = (state.sprints ?? [])
    .filter((sprint) => sprint.status !== 'pending')
    .slice(-8)
    .map((sprint) => `S${sprint.id} ${sprintStatusLabel(sprint.status)}`);

  const lines = [];
  lines.push('## Kairo Sprint Batch');
  lines.push('');
  lines.push(`Batch: ${state.batch_id}`);
  lines.push(`Roadmap: ${state.roadmap}`);
  lines.push(`Status: ${String(state.status).toUpperCase()}`);
  const inheritedCount = (state.sprints ?? []).filter(
    (sprint) => sprint.status === 'completed' && sprint.inherited,
  ).length;
  lines.push(`Requested: ${state.requested_count}`);
  lines.push(`Completed: ${state.completed_count}`);
  if (inheritedCount > 0) {
    lines.push(`Inherited completed (earlier batches): ${inheritedCount}`);
  }
  lines.push(
    `Current: ${currentSprint ? `Sprint ${currentSprint.id} — ${currentSprint.title}` : 'none'}`,
  );
  lines.push(`Phase: ${sprintStatusLabel(state.current_phase)}`);
  lines.push(`Started: ${state.started_at ?? 'unknown'}`);
  lines.push(`Last update: ${state.updated_at ?? 'unknown'}`);
  lines.push(`Baseline SHA: ${state.baseline_sha ?? 'unknown'}`);
  lines.push(`Queue: ${state.queue_available ? 'available' : 'not available'}`);
  lines.push(`Stop requested: ${state.stop_requested ? 'yes' : 'no'}`);
  lines.push('');
  if (recent.length > 0) {
    lines.push('Recent:');
    lines.push(...recent);
    lines.push('');
  }
  lines.push('Remaining in this batch:');
  lines.push(String(remainingInBatch));
  lines.push('');
  if (nextUnfinished && state.status !== 'completed') {
    lines.push('Next unfinished sprint:');
    lines.push(`S${nextUnfinished.id} — ${nextUnfinished.title}`);
  } else if (nextAfterBatch) {
    lines.push('Next roadmap sprint after batch:');
    lines.push(`S${nextAfterBatch.id} — ${nextAfterBatch.title}`);
  } else {
    lines.push('All roadmap sprints are complete.');
  }
  if (state.blockers && state.blockers.length > 0) {
    lines.push('');
    lines.push('Blockers:');
    for (const blocker of state.blockers) {
      lines.push(`- ${blocker}`);
    }
  }
  lines.push('');
  return lines.join('\n');
}

export function writeSprintReport(rootDir, sprint, payload) {
  const reports = reportsDir(rootDir);
  mkdirSync(reports, { recursive: true });
  const stamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `sprint-${sprint.id}-${stamp}.md`;
  const path = join(reports, filename);
  const lines = [];
  lines.push(`# Sprint ${sprint.id} — ${sprint.title}`);
  lines.push('');
  lines.push(`Verdict: ${payload.verdict}`);
  lines.push(`Recorded: ${new Date().toISOString()}`);
  lines.push(`Batch: ${payload.batchId ?? 'unknown'}`);
  lines.push('');
  lines.push('## Goal');
  lines.push('');
  lines.push(sprint.goal);
  lines.push('');
  if (payload.summary) {
    lines.push('## Summary');
    lines.push('');
    lines.push(payload.summary);
    lines.push('');
  }
  for (const [heading, key] of [
    ['Files changed', 'filesChanged'],
    ['Architectural decisions', 'decisions'],
    ['Database migrations', 'migrations'],
    ['API changes', 'apiChanges'],
    ['UI changes', 'uiChanges'],
    ['Tests added', 'testsAdded'],
    ['Tests executed', 'testsExecuted'],
    ['Builds executed', 'builds'],
    ['Security checks', 'security'],
    ['Known limitations', 'limitations'],
  ]) {
    const value = payload[key];
    if (!value) {
      continue;
    }
    lines.push(`## ${heading}`);
    lines.push('');
    if (Array.isArray(value)) {
      for (const item of value) {
        lines.push(`- ${item}`);
      }
    } else {
      lines.push(value);
    }
    lines.push('');
  }
  lines.push('## Acceptance criteria result');
  lines.push('');
  for (const criterion of sprint.acceptance ?? []) {
    lines.push(`- ${criterion}`);
  }
  lines.push('');
  lines.push(`Git SHA: ${payload.gitSha ?? 'unknown'}`);
  lines.push('');
  lines.push(`Final verdict: ${payload.verdict}`);
  lines.push('');
  writeFileSync(path, lines.join('\n'), 'utf8');
  return path;
}

export function buildBatchReport(state, roadmap) {
  const completed = (state.sprints ?? []).filter(
    (sprint) => sprint.status === 'completed' && !sprint.inherited,
  );
  const inherited = (state.sprints ?? []).filter(
    (sprint) => sprint.status === 'completed' && sprint.inherited,
  );
  const blocked = (state.sprints ?? []).filter((sprint) => sprint.status === 'blocked');
  const failed = (state.sprints ?? []).filter((sprint) => sprint.status === 'failed');
  const first = completed[0] ?? null;
  const last = completed[completed.length - 1] ?? null;
  const nextUnfinished = nextUnfinishedSprint(roadmap, state);

  const lines = [];
  lines.push('KAIRO AUTONOMOUS BATCH REPORT');
  lines.push('');
  lines.push(`Batch ID: ${state.batch_id}`);
  lines.push(`Requested: ${state.requested_count}`);
  lines.push(`Completed: ${state.completed_count}`);
  if (inherited.length > 0) {
    lines.push(`Inherited completed (earlier batches): ${inherited.map((sprint) => `S${sprint.id}`).join(', ')}`);
  }
  lines.push(`Blocked: ${blocked.length}`);
  if (failed.length > 0) {
    lines.push(`Failed: ${failed.length}`);
  }
  lines.push(`First sprint: ${first ? `S${first.id} — ${first.title}` : 'none'}`);
  lines.push(`Last sprint: ${last ? `S${last.id} — ${last.title}` : 'none'}`);
  lines.push(`Started: ${state.started_at ?? 'unknown'}`);
  lines.push(`Finished: ${new Date().toISOString()}`);
  lines.push(`Sprints: ${(state.sprints ?? []).map((sprint) => `S${sprint.id} ${sprintStatusLabel(sprint.status)}`).join(', ')}`);
  lines.push('');
  lines.push('Remaining known issues:');
  if (blocked.length === 0 && failed.length === 0 && !state.stop_requested) {
    lines.push('- None recorded by the batch state machine.');
  } else {
    for (const sprint of [...blocked, ...failed]) {
      lines.push(`- S${sprint.id}: ${sprint.summary ?? 'blocked'}`);
    }
    if (state.stop_requested) {
      lines.push(`- Operator stop requested: ${state.stop_reason ?? 'no reason recorded'}`);
    }
  }
  lines.push('');
  lines.push(`Next unfinished sprint: ${nextUnfinished ? `S${nextUnfinished.id} — ${nextUnfinished.title}` : 'none'}`);
  lines.push('');
  const verdict = failed.length > 0 || blocked.length > 0
    ? 'BLOCKED'
    : state.completed_count >= state.requested_count
      ? 'PASS'
      : 'PARTIAL';
  lines.push(`Final batch verdict: ${verdict}`);
  lines.push('');
  return lines.join('\n');
}

export function writeBatchReport(rootDir, state, roadmap) {
  const reports = reportsDir(rootDir);
  mkdirSync(reports, { recursive: true });
  const path = join(reports, `batch-${state.batch_id}.md`);
  writeFileSync(path, buildBatchReport(state, roadmap), 'utf8');
  return path;
}

export function listReports(rootDir) {
  const dir = stateDir(rootDir);
  if (!existsSync(dir)) {
    return [];
  }
  return readdirSync(join(dir, 'reports')).sort().reverse();
}

export function formatSprintSpec(sprint) {
  const lines = [];
  lines.push(`Sprint ${sprint.id} — ${sprint.title}`);
  lines.push(`Phase: ${sprint.phase}`);
  lines.push(`Goal: ${sprint.goal}`);
  lines.push('');
  lines.push('Tasks:');
  for (const task of sprint.tasks ?? []) {
    lines.push(`- ${task}`);
  }
  lines.push('');
  lines.push('Acceptance:');
  for (const criterion of sprint.acceptance ?? []) {
    lines.push(`- ${criterion}`);
  }
  lines.push('');
  return lines.join('\n');
}

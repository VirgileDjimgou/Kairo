import { existsSync, readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';

export const ROADMAP_RELATIVE_PATH = 'docs/roadmap/KAIRO_V2_ROADMAP.json';

export function findRoot(startDir = process.cwd()) {
  let current = resolve(startDir);
  for (let index = 0; index < 12; index += 1) {
    if (existsSync(join(current, '.git'))) {
      return current;
    }
    const parent = dirname(current);
    if (parent === current) {
      break;
    }
    current = parent;
  }
  throw new Error(`Unable to locate the Kairo repository root from ${startDir}`);
}

export function loadRoadmap(rootDir = findRoot()) {
  const path = join(rootDir, ROADMAP_RELATIVE_PATH);
  if (!existsSync(path)) {
    throw new Error(`Roadmap file not found: ${ROADMAP_RELATIVE_PATH}`);
  }
  const raw = readFileSync(path, 'utf8');
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (error) {
    throw new Error(`Roadmap JSON is not parseable: ${error.message}`);
  }
  if (!parsed || !Array.isArray(parsed.sprints) || parsed.sprints.length === 0) {
    throw new Error('Roadmap JSON has no sprints array');
  }
  const ids = new Set();
  for (const sprint of parsed.sprints) {
    if (typeof sprint.id !== 'number') {
      throw new Error('Every roadmap sprint must have a numeric id');
    }
    if (ids.has(sprint.id)) {
      throw new Error(`Duplicate roadmap sprint id: ${sprint.id}`);
    }
    ids.add(sprint.id);
  }
  return parsed;
}

export function getSprint(roadmap, id) {
  return roadmap.sprints.find((sprint) => sprint.id === id) ?? null;
}

export function sprintIds(roadmap) {
  return roadmap.sprints.map((sprint) => sprint.id);
}

export function completedSprintIds(state) {
  if (!state || !Array.isArray(state.sprints)) {
    return new Set();
  }
  return new Set(
    state.sprints
      .filter((sprint) => sprint.status === 'completed')
      .map((sprint) => sprint.id),
  );
}

export function nextUnfinishedSprint(roadmap, state) {
  const completed = completedSprintIds(state);
  for (const sprint of roadmap.sprints) {
    if (!completed.has(sprint.id)) {
      return sprint;
    }
  }
  return null;
}

export function nextRoadmapSprintAfter(roadmap, sprintId) {
  const index = roadmap.sprints.findIndex((sprint) => sprint.id === sprintId);
  if (index === -1) {
    return null;
  }
  return roadmap.sprints[index + 1] ?? null;
}

export function dependenciesSatisfied(roadmap, state, sprint) {
  const dependencies = sprint.dependencies ?? [];
  if (dependencies.length === 0) {
    return { ok: true, blocking: [] };
  }
  const completed = completedSprintIds(state);
  const blocking = dependencies.filter((dependency) => !completed.has(dependency));
  return { ok: blocking.length === 0, blocking };
}

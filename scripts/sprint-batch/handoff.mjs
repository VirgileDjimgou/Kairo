import { existsSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { handoffsDir, readJsonFile, writeJsonFile } from './state.mjs';

export const HANDOFF_REQUIRED_FIELDS = [
  'sprint_id',
  'status',
  'objective_completed',
  'files_added',
  'files_modified',
  'files_removed',
  'database_migrations',
  'public_contract_changes',
  'architecture_decisions',
  'new_dependencies',
  'configuration_changes',
  'tests_added',
  'tests_changed',
  'tests_status',
  'security_implications',
  'known_limitations',
  'remaining_followups',
  'next_sprint_dependencies',
  'commit_sha',
  'timestamp',
];

export const HANDOFF_LIST_FIELDS = [
  'files_added',
  'files_modified',
  'files_removed',
  'database_migrations',
  'public_contract_changes',
  'architecture_decisions',
  'new_dependencies',
  'configuration_changes',
  'tests_added',
  'tests_changed',
  'security_implications',
  'known_limitations',
  'remaining_followups',
  'next_sprint_dependencies',
];

export function handoffPath(rootDir, sprintId) {
  return join(handoffsDir(rootDir), `sprint-${sprintId}.json`);
}

export function normalizeHandoff(input, sprintId) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) {
    throw new Error('Handoff payload must be a JSON object.');
  }
  const missing = HANDOFF_REQUIRED_FIELDS.filter(
    (field) => !Object.prototype.hasOwnProperty.call(input, field),
  );
  if (missing.length > 0) {
    throw new Error(`Handoff is missing required field(s): ${missing.join(', ')}.`);
  }
  const normalized = { ...input };
  if (Number(normalized.sprint_id) !== Number(sprintId)) {
    throw new Error(
      `Handoff sprint_id ${normalized.sprint_id} does not match the active sprint ${sprintId}.`,
    );
  }
  normalized.sprint_id = Number(sprintId);
  for (const field of HANDOFF_LIST_FIELDS) {
    const value = normalized[field];
    if (value === null || value === undefined) {
      normalized[field] = [];
    } else if (Array.isArray(value)) {
      normalized[field] = value;
    } else {
      normalized[field] = [value];
    }
  }
  normalized.tests_status = normalized.tests_status ?? 'unknown';
  normalized.commit_sha = normalized.commit_sha ?? null;
  normalized.timestamp = normalized.timestamp ?? new Date().toISOString();
  normalized.status = String(normalized.status ?? 'COMPLETED').toUpperCase();
  return normalized;
}

export function writeHandoff(rootDir, handoff) {
  mkdirSync(handoffsDir(rootDir), { recursive: true });
  const path = handoffPath(rootDir, handoff.sprint_id);
  writeJsonFile(path, handoff);
  return path;
}

export function loadHandoff(rootDir, sprintId) {
  return readJsonFile(handoffPath(rootDir, sprintId), null);
}

export function hasHandoff(rootDir, sprintId) {
  return existsSync(handoffPath(rootDir, sprintId));
}

#!/usr/bin/env node
/**
 * Canonical PWA Service Worker guard.
 *
 * Kairo must expose exactly one Service Worker per application origin. The
 * worker is built from `apps/web/src/sw.ts` through vite-plugin-pwa
 * `injectManifest`; no second worker file (for example a Firebase
 * `firebase-messaging-sw.js`) may exist, because a competing registration can
 * silently take over push and notification-click handling.
 *
 * The guard also asserts the worker keeps the required lifecycle, offline,
 * push, FCM-background and navigation-message contracts.
 *
 * Usage: node scripts/check-pwa-service-worker.mjs
 */
import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const failures = [];

function read(relative) {
  return readFileSync(path.join(root, relative), 'utf8');
}

function requireSnippet(relative, snippet) {
  const content = read(relative);
  if (!content.includes(snippet)) {
    failures.push(`${relative} is missing required snippet: ${snippet}`);
  }
}

const viteConfig = 'apps/web/vite.config.ts';
const worker = 'apps/web/src/sw.ts';

if (!existsSync(path.join(root, worker))) {
  failures.push(`${worker} does not exist; the canonical worker must stay in source.`);
} else {
  requireSnippet(viteConfig, "strategies: 'injectManifest'");
  requireSnippet(viteConfig, "filename: 'sw.ts'");
  requireSnippet(viteConfig, "srcDir: 'src'");
  requireSnippet(viteConfig, 'injectRegister: false');

  requireSnippet(worker, 'self.skipWaiting()');
  requireSnippet(worker, 'clientsClaim()');
  requireSnippet(worker, 'precacheAndRoute(');
  requireSnippet(worker, 'cleanupOutdatedCaches()');
  requireSnippet(worker, 'registerRoute(');
  requireSnippet(worker, "addEventListener('push'");
  requireSnippet(worker, "addEventListener('notificationclick'");
  requireSnippet(worker, "addEventListener('pushsubscriptionchange'");
  requireSnippet(worker, 'self.clients.matchAll(');
  requireSnippet(worker, '.focus()');
  requireSnippet(worker, 'self.clients.openWindow(');
  requireSnippet(worker, 'postMessage(');
  requireSnippet(worker, 'onBackgroundMessage(');
}

function findFiles(directory, matcher, results = []) {
  if (!existsSync(directory)) return results;
  for (const entry of readdirSync(directory)) {
    const absolute = path.join(directory, entry);
    if (statSync(absolute).isDirectory()) {
      findFiles(absolute, matcher, results);
    } else if (matcher(entry)) {
      results.push(path.relative(root, absolute).replace(/\\/g, '/'));
    }
  }
  return results;
}

const competingWorkers = [
  ...findFiles(path.join(root, 'apps/web/public'), (name) => /service-?worker|firebase-messaging-sw|^sw\.(js|ts)$/i.test(name)),
  ...findFiles(path.join(root, 'apps/web/src'), (name) => /firebase-messaging-sw/i.test(name)),
].filter((file) => file !== worker);
if (competingWorkers.length > 0) {
  failures.push(
    `competing Service Worker file(s) found: ${competingWorkers.join(', ')}. ` +
      'The canonical worker must be the only registration source.',
  );
}

requireSnippet('apps/web/src/main.ts', "from 'virtual:pwa-register'");
requireSnippet('apps/web/src/services/web-push.ts', "register('/sw.js'");

if (failures.length > 0) {
  console.error('Canonical PWA Service Worker check failed:');
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log('OK: one canonical PWA Service Worker with the required lifecycle, push, FCM and navigation contracts.');

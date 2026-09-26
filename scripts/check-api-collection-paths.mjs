import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";

/**
 * Guards canonical FastAPI collection routes in the web API layer.
 *
 * FastAPI defines collection routes with a trailing slash (for example
 * `/documents/`). Calling the slash-less form makes the API answer with a 307
 * redirect. When the reverse proxy does not forward the original scheme, that
 * redirect becomes an absolute `http://` URL, which an HTTPS browser blocks as
 * mixed content and the surface fails with a misleading "Network Error".
 *
 * The web client must therefore always call the canonical trailing-slash path.
 */

const repoRoot = process.cwd();
const apiDir = path.join(repoRoot, "apps", "web", "src", "api");

const collectionRoots = [
  "documents",
  "memberships",
  "policies",
  "contributions",
  "events",
  "announcements",
  "disciplinary",
];

const offenders = [];

const pattern = new RegExp(`['"\`]/(${collectionRoots.join("|")})['"\`]`, "g");

async function scanFile(filePath) {
  const content = await fs.readFile(filePath, "utf8");
  const lines = content.split("\n");
  lines.forEach((line, index) => {
    pattern.lastIndex = 0;
    let match;
    while ((match = pattern.exec(line)) !== null) {
      offenders.push({
        file: path.relative(repoRoot, filePath).replaceAll("\\", "/"),
        line: index + 1,
        route: match[1],
        text: line.trim(),
      });
    }
  });
}

async function run() {
  let entries;
  try {
    entries = await fs.readdir(apiDir, { withFileTypes: true });
  } catch (error) {
    console.error(`Cannot read ${apiDir}: ${error.message}`);
    process.exitCode = 1;
    return;
  }

  for (const entry of entries) {
    if (entry.isFile() && entry.name.endsWith(".ts")) {
      await scanFile(path.join(apiDir, entry.name));
    }
  }

  if (offenders.length === 0) {
    console.log("API collection paths are canonical (trailing slash present).");
    return;
  }

  console.error("Slash-less FastAPI collection routes detected in the web client:");
  for (const offender of offenders) {
    console.error(`  ${offender.file}:${offender.line}  /${offender.route}  →  /${offender.route}/`);
    console.error(`      ${offender.text}`);
  }
  console.error(
    "\nUse the canonical trailing-slash path so the API never issues a redirect.",
  );
  process.exitCode = 1;
}

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

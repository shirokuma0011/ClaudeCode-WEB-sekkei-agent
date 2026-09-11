import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";

const temporaryRoot = await fs.mkdtemp(path.join(os.tmpdir(), "claudecode-web-agent-"));
process.env.WEB_AGENT_OUTPUT_ROOT = temporaryRoot;
const { ROOT_DIR, projectDirectory, validateProject } = await import("../scripts/lib.mjs");

const slug = `smoke-test-${process.pid}`;
const outputDir = projectDirectory(slug);
const originalArgv = process.argv;

try {
  process.argv = [process.execPath, path.join(ROOT_DIR, "scripts", "generate-deliverables.mjs"), path.join(ROOT_DIR, "examples", "restaurant-input.md"), slug];
  await import(`../scripts/generate-deliverables.mjs?smoke=${Date.now()}`);
  const preZip = validateProject(slug);
  if (!preZip.ok) throw new Error(preZip.errors.join("\n"));
  process.argv = [process.execPath, path.join(ROOT_DIR, "scripts", "generate-zip.mjs"), slug];
  await import(`../scripts/generate-zip.mjs?smoke=${Date.now()}`);
  const result = validateProject(slug, { requireZip: true });
  if (!result.ok) throw new Error(result.errors.join("\n"));
  if (result.summary.promptCount !== 10) throw new Error("Expected exactly 10 prompts.");
  if (result.summary.htmlPageCount < 5) throw new Error("Expected at least 5 HTML pages.");
  if (result.summary.imageMode !== "prompts-only") throw new Error("Smoke test should use prompts-only mode.");
  console.log("Smoke test passed.");
  console.log(JSON.stringify(result.summary, null, 2));
} finally {
  process.argv = originalArgv;
  await fs.rm(temporaryRoot, { recursive: true, force: true });
}

import fsp from "node:fs/promises";
import path from "node:path";
import { projectDirectory, validateProject } from "./lib.mjs";
import { writeZip } from "./zip-writer.mjs";

const projectSlug = process.argv[2];
if (!projectSlug) {
  console.error("Usage: node scripts/generate-zip.mjs <project-slug>");
  process.exit(1);
}

const validation = validateProject(projectSlug);
if (!validation.ok) {
  console.error("Package validation failed; ZIP was not created:");
  for (const error of validation.errors) console.error(`- ${error}`);
  process.exit(1);
}

const outputDir = projectDirectory(projectSlug);
const zipName = `${projectSlug}-website-package.zip`;
const zipPath = path.join(outputDir, zipName);
await fsp.rm(zipPath, { force: true });

function excluded(relative) {
  const segments = relative.split(path.sep);
  const base = path.basename(relative);
  return segments.some((segment) => segment === ".git" || segment === "node_modules")
    || base === zipName
    || base.endsWith(".zip")
    || base === ".env"
    || base.startsWith(".env.")
    || base.endsWith(".key")
    || base.endsWith(".pem");
}

async function collectFiles(directory, relative = "") {
  const entries = await fsp.readdir(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const nextRelative = path.join(relative, entry.name);
    if (excluded(nextRelative)) continue;
    const absolute = path.join(directory, entry.name);
    if (entry.isSymbolicLink()) throw new Error(`Symbolic links are not allowed in deliverables: ${nextRelative}`);
    if (entry.isDirectory()) files.push(...await collectFiles(absolute, nextRelative));
    else if (entry.isFile()) files.push({ absolute, relative: nextRelative.split(path.sep).join("/") });
  }
  return files;
}

const files = await collectFiles(outputDir);
if (files.length === 0) throw new Error("No files found to archive.");

const zipResult = await writeZip(await Promise.all(files.map(async (file) => ({
  name: file.relative,
  data: await fsp.readFile(file.absolute)
}))), zipPath);

const finalValidation = validateProject(projectSlug, { requireZip: true });
if (!finalValidation.ok) {
  await fsp.rm(zipPath, { force: true });
  throw new Error(`ZIP post-validation failed: ${finalValidation.errors.join("; ")}`);
}

console.log("ZIP generated.");
console.log(JSON.stringify({
  ...finalValidation.summary,
  archivedFileCount: zipResult.entries,
  zipBytes: zipResult.bytes
}, null, 2));

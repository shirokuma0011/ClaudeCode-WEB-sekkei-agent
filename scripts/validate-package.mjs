import { validateProject } from "./lib.mjs";

const args = process.argv.slice(2);
const requireZip = args.includes("--require-zip");
const projectSlug = args.find((arg) => !arg.startsWith("--"));

if (!projectSlug) {
  console.error("Usage: node scripts/validate-package.mjs <project-slug> [--require-zip]");
  process.exit(1);
}

let result;
try {
  result = validateProject(projectSlug, { requireZip });
} catch (error) {
  console.error(error.message);
  process.exit(1);
}

for (const warning of result.warnings) console.warn(`Warning: ${warning}`);
if (!result.ok) {
  console.error("Validation failed:");
  for (const error of result.errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log("Validation passed.");
console.log(JSON.stringify(result.summary, null, 2));


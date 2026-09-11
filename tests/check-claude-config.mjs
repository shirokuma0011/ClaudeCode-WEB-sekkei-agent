// Claude Code向けプロジェクト構成の検査。
//
// CLAUDE.md、.claude/settings.json、.claude/agents/ 配下、.claude/skills/ 配下の SKILL.md が
// 期待どおりの形式で存在し、CLAUDE.md が参照するサブエージェント名と一致することを確認する。
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const errors = [];

const EXPECTED_AGENTS = [
  "sekkei-requirements",
  "sekkei-blueprint",
  "sekkei-copy-seo",
  "sekkei-visual",
  "sekkei-implementation-qa",
  "sekkei-packager"
];

function read(relative) {
  const absolute = path.join(ROOT_DIR, relative);
  if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
    errors.push(`Missing file: ${relative}`);
    return null;
  }
  const content = fs.readFileSync(absolute, "utf8");
  if (content.trim() === "") errors.push(`Empty file: ${relative}`);
  return content;
}

function parseFrontmatter(content, relative) {
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n/.exec(content);
  if (!match) {
    errors.push(`${relative} has no YAML frontmatter.`);
    return {};
  }
  const fields = {};
  for (const line of match[1].split(/\r?\n/)) {
    const pair = /^([A-Za-z0-9_-]+):\s*(.*)$/.exec(line);
    if (pair) fields[pair[1]] = pair[2].trim();
  }
  return fields;
}

// CLAUDE.md
const claudeMd = read("CLAUDE.md");
if (claudeMd) {
  const lineCount = claudeMd.split(/\r?\n/).length;
  if (lineCount > 200) errors.push(`CLAUDE.md is ${lineCount} lines; keep it under 200 for reliable adherence.`);
  for (const importPath of claudeMd.matchAll(/^@([^\s`]+)$/gm)) {
    if (!fs.existsSync(path.join(ROOT_DIR, importPath[1]))) errors.push(`CLAUDE.md imports a missing file: ${importPath[1]}`);
  }
  for (const agent of EXPECTED_AGENTS) {
    if (!claudeMd.includes(`\`${agent}\``)) errors.push(`CLAUDE.md does not reference subagent ${agent}.`);
  }
}

// .claude/settings.json
const settingsRaw = read(".claude/settings.json");
if (settingsRaw) {
  try {
    const settings = JSON.parse(settingsRaw);
    const allow = settings?.permissions?.allow;
    if (!Array.isArray(allow) || allow.length === 0) errors.push(".claude/settings.json must define permissions.allow.");
    for (const required of ["Bash(npm run validate:*)", "Bash(npm run zip:*)", "Bash(npm run generate:*)"]) {
      if (Array.isArray(allow) && !allow.includes(required)) errors.push(`.claude/settings.json permissions.allow is missing ${required}.`);
    }
  } catch (error) {
    errors.push(`.claude/settings.json is invalid JSON: ${error.message}`);
  }
}

// .claude/agents/*.md
const agentsDir = path.join(ROOT_DIR, ".claude", "agents");
const agentFiles = fs.existsSync(agentsDir) ? fs.readdirSync(agentsDir).filter((name) => name.endsWith(".md")) : [];
const agentNames = new Set();
for (const file of agentFiles) {
  const relative = path.join(".claude", "agents", file);
  const content = read(relative);
  if (!content) continue;
  const fields = parseFrontmatter(content, relative);
  if (!fields.name) errors.push(`${relative} frontmatter is missing name.`);
  if (!fields.description) errors.push(`${relative} frontmatter is missing description.`);
  if (fields.name && fields.name !== path.basename(file, ".md")) errors.push(`${relative}: name "${fields.name}" must match the filename.`);
  if (fields.name && !/^[a-z0-9][a-z0-9-]*$/.test(fields.name)) errors.push(`${relative}: name must be lowercase letters, numbers, and hyphens.`);
  if (fields.name) agentNames.add(fields.name);
  for (const section of ["## 入力", "## 処理", "## 出力", "## 完了条件"]) {
    if (!content.includes(section)) errors.push(`${relative} is missing the "${section}" section.`);
  }
}
for (const agent of EXPECTED_AGENTS) {
  if (!agentNames.has(agent)) errors.push(`Missing subagent definition: .claude/agents/${agent}.md`);
}

// .claude/skills/web-sekkei/SKILL.md
const skill = read(".claude/skills/web-sekkei/SKILL.md");
if (skill) {
  const fields = parseFrontmatter(skill, ".claude/skills/web-sekkei/SKILL.md");
  if (fields.name !== "web-sekkei") errors.push("SKILL.md frontmatter name must be web-sekkei.");
  if (!fields.description) errors.push("SKILL.md frontmatter is missing description.");
  for (const agent of EXPECTED_AGENTS) {
    if (!skill.includes(`\`${agent}\``)) errors.push(`SKILL.md does not reference subagent ${agent}.`);
  }
}

// docs referenced by agents
for (const relative of [
  "docs/guidelines/common-rules.md",
  "docs/workflow.md",
  "docs/templates/requirements-template.md",
  "docs/templates/blueprint-template.md",
  "docs/templates/copy-template.md",
  "docs/templates/seo-template.md",
  "docs/templates/image-prompts-template.md",
  "docs/templates/implementation-template.md",
  "docs/templates/checklist-template.md"
]) {
  read(relative);
}

if (errors.length > 0) {
  console.error("Claude Code config check failed:");
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log(`Claude Code config check passed (${agentNames.size} subagents, 1 skill).`);

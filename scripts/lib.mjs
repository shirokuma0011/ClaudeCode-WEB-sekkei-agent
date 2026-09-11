import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
export const ROOT_DIR = path.resolve(SCRIPT_DIR, "..");
export const OUTPUT_ROOT = process.env.WEB_AGENT_OUTPUT_ROOT
  ? path.resolve(process.env.WEB_AGENT_OUTPUT_ROOT)
  : path.join(ROOT_DIR, "output");

export const IMAGE_FILENAMES = [
  "01_hero.webp",
  "02_main-service.webp",
  "03_feature.webp",
  "04_detail.webp",
  "05_scene-01.webp",
  "06_scene-02.webp",
  "07_customer.webp",
  "08_staff.webp",
  "09_exterior-or-space.webp",
  "10_cta.webp"
];

export const REQUIRED_FILES = [
  "README.md",
  "00_project-summary.md",
  "01_requirements.md",
  "02_website-blueprint.md",
  "03_copywriting.md",
  "04_seo-plan.md",
  "05_ui-ux-design.md",
  "06_animation-js-spec.md",
  "07_css-design.md",
  "08_responsive-design.md",
  "09_visual-assets-plan.md",
  "10_image-prompts.md",
  "11_implementation-instructions.md",
  "12_quality-checklist.md",
  "assets/prompts.json",
  "assets/image-index.csv",
  "implementation-starter/README.md",
  "implementation-starter/assets/css/style.css",
  "implementation-starter/assets/js/main.js"
];

export function assertValidSlug(slug) {
  if (typeof slug !== "string" || !/^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$/.test(slug)) {
    throw new Error("project-slug must be 1-64 characters using lowercase letters, numbers, and hyphens only.");
  }
  return slug;
}

export function projectDirectory(slug) {
  assertValidSlug(slug);
  const resolved = path.resolve(OUTPUT_ROOT, slug);
  const relative = path.relative(OUTPUT_ROOT, resolved);
  if (!relative || relative.startsWith("..") || path.isAbsolute(relative)) {
    throw new Error("Resolved output path is outside the output directory.");
  }
  return resolved;
}

export function parseInputMarkdown(source) {
  // 「【見出し】」で始まる行をセクション見出しとして扱う。
  // 「【見出し】\n本文」と「【見出し】本文」の両方を受け付け、空セクションは空文字になる。
  const result = {};
  let key = null;
  let lines = [];
  const flush = () => {
    if (key !== null) result[key] = lines.join("\n").trim();
  };
  for (const line of String(source).replaceAll("\r\n", "\n").split("\n")) {
    const header = /^【([^】]+)】[ \t]*(.*)$/.exec(line);
    if (header) {
      flush();
      key = header[1].trim();
      lines = header[2].trim() ? [header[2].trim()] : [];
    } else if (key !== null) {
      lines.push(line);
    }
  }
  flush();
  return result;
}

export function htmlEscape(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

export function csvEscape(value) {
  const text = String(value ?? "");
  return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

export function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    if (quoted) {
      if (char === '"' && text[index + 1] === '"') {
        field += '"';
        index += 1;
      } else if (char === '"') {
        quoted = false;
      } else {
        field += char;
      }
    } else if (char === '"') {
      quoted = true;
    } else if (char === ",") {
      row.push(field);
      field = "";
    } else if (char === "\n") {
      row.push(field.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += char;
    }
  }
  if (quoted) throw new Error("CSV contains an unterminated quoted field.");
  if (field.length > 0 || row.length > 0) {
    row.push(field.replace(/\r$/, ""));
    rows.push(row);
  }
  return rows.filter((current) => current.some((value) => value !== ""));
}

function listFilesRecursive(directory) {
  if (!fs.existsSync(directory)) return [];
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const absolute = path.join(directory, entry.name);
    return entry.isDirectory() ? listFilesRecursive(absolute) : [absolute];
  });
}

export function validateProject(slug, { requireZip = false } = {}) {
  const base = projectDirectory(slug);
  const errors = [];
  const warnings = [];

  if (!fs.existsSync(base)) {
    return { ok: false, errors: [`Output directory not found: ${base}`], warnings, summary: null };
  }

  for (const relative of REQUIRED_FILES) {
    const absolute = path.join(base, relative);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile() || fs.statSync(absolute).size === 0) {
      errors.push(`Missing or empty required file: ${relative}`);
    }
  }

  let prompts = [];
  const promptsPath = path.join(base, "assets", "prompts.json");
  try {
    prompts = JSON.parse(fs.readFileSync(promptsPath, "utf8"));
    if (!Array.isArray(prompts) || prompts.length !== 10) {
      errors.push("assets/prompts.json must contain exactly 10 entries.");
      prompts = Array.isArray(prompts) ? prompts : [];
    }
  } catch (error) {
    errors.push(`assets/prompts.json is invalid JSON: ${error.message}`);
  }

  const promptIds = new Set();
  const promptNames = new Set();
  for (const [index, item] of prompts.entries()) {
    const label = `prompts.json entry ${index + 1}`;
    if (!Number.isInteger(item?.id) || item.id < 1 || item.id > 10) errors.push(`${label} has an invalid id.`);
    if (promptIds.has(item?.id)) errors.push(`${label} duplicates id ${item.id}.`);
    promptIds.add(item?.id);
    if (!IMAGE_FILENAMES.includes(item?.filename)) errors.push(`${label} has an unexpected filename.`);
    if (promptNames.has(item?.filename)) errors.push(`${label} duplicates filename ${item.filename}.`);
    promptNames.add(item?.filename);
    for (const key of ["usage", "purpose", "prompt", "alt", "recommended_size"]) {
      if (typeof item?.[key] !== "string" || item[key].trim() === "") errors.push(`${label} is missing ${key}.`);
    }
    if (typeof item?.prompt === "string" && !/no text/i.test(item.prompt)) {
      warnings.push(`${label} does not contain the recommended \"no text\" constraint.`);
    }
  }
  if (promptNames.size === 10 && IMAGE_FILENAMES.some((name) => !promptNames.has(name))) {
    errors.push("prompts.json filenames do not match the required image set.");
  }

  const csvPath = path.join(base, "assets", "image-index.csv");
  let csvRows = [];
  try {
    csvRows = parseCsv(fs.readFileSync(csvPath, "utf8"));
    const expectedHeader = ["id", "filename", "usage", "purpose", "recommended_size", "alt"];
    if (JSON.stringify(csvRows[0]) !== JSON.stringify(expectedHeader)) errors.push("image-index.csv header is invalid.");
    if (csvRows.length !== 11) errors.push("image-index.csv must contain one header and exactly 10 data rows.");
    const csvNames = new Set(csvRows.slice(1).map((row) => row[1]));
    if (IMAGE_FILENAMES.some((name) => !csvNames.has(name))) errors.push("image-index.csv filenames do not match the required image set.");
  } catch (error) {
    errors.push(`assets/image-index.csv is invalid: ${error.message}`);
  }

  const imagesDir = path.join(base, "assets", "images");
  const presentImages = IMAGE_FILENAMES.filter((name) => {
    const target = path.join(imagesDir, name);
    return fs.existsSync(target) && fs.statSync(target).isFile() && fs.statSync(target).size > 0;
  });
  let imageMode;
  if (presentImages.length === 10) {
    imageMode = "generated-images";
  } else if (presentImages.length === 0) {
    imageMode = "prompts-only";
    const readme = path.join(imagesDir, "README.md");
    if (!fs.existsSync(readme) || fs.statSync(readme).size === 0) errors.push("Prompt-only mode requires assets/images/README.md.");
  } else {
    imageMode = "incomplete-images";
    errors.push(`Image set is incomplete: found ${presentImages.length} of 10 required images.`);
  }

  const starterDir = path.join(base, "implementation-starter");
  const htmlPages = listFilesRecursive(starterDir).filter((file) => file.toLowerCase().endsWith(".html"));
  if (htmlPages.length < 5) errors.push(`implementation-starter must contain at least 5 HTML pages; found ${htmlPages.length}.`);

  const markdownCount = listFilesRecursive(base).filter((file) => file.toLowerCase().endsWith(".md")).length;
  const zipPath = path.join(base, `${slug}-website-package.zip`);
  if (requireZip && (!fs.existsSync(zipPath) || fs.statSync(zipPath).size === 0)) {
    errors.push(`ZIP file is missing or empty: ${path.basename(zipPath)}`);
  }

  return {
    ok: errors.length === 0,
    errors,
    warnings,
    summary: {
      project: slug,
      directory: base,
      markdownCount,
      promptCount: prompts.length,
      csvImageCount: Math.max(csvRows.length - 1, 0),
      imageCount: presentImages.length,
      imageMode,
      htmlPageCount: htmlPages.length,
      zipPath,
      zipExists: fs.existsSync(zipPath)
    }
  };
}

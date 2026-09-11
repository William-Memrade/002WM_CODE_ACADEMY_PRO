import fs from "node:fs";
import path from "node:path";

const nextDir = path.resolve(process.cwd(), ".next");

if (!fs.existsSync(nextDir)) {
  console.log("[clean] .next does not exist (nothing to do).");
  process.exit(0);
}

try {
  fs.rmSync(nextDir, {
    recursive: true,
    force: true,
    maxRetries: 5,
    retryDelay: 200,
  });
  console.log("[clean] Removed .next");
} catch (error) {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`[clean] Failed to remove .next: ${message}`);
  console.error(
    "[clean] Stop any running `next dev` / `next start` processes and retry."
  );
  process.exit(1);
}


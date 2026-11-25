// News-image entry for 25 November 2026.
//
// The front page is drawn ahead of time by render.py (pure Pillow, no
// network, byte-identical on every run) and stored next to this file as
// entry.png. All this program does is place that image where the grader
// expects it.
//
// Run locally with:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const source = join(here, "entry.png");
const target = join(outDir, "entry.png");

copyFileSync(source, target);

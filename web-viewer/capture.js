#!/usr/bin/env node
/**
 * Headless Capture — state.json → SVG/PNG for PIAF
 * ==================================================
 * Standalone Node.js script. No browser required for SVG output.
 * PNG output requires puppeteer (optional dependency).
 *
 * Usage:
 *   node capture.js <state.json> [options]
 *
 * Options:
 *   --output, -o   Output file path (default: plan-layout.svg)
 *   --format, -f   Output format: svg or png (default: svg)
 *   --width, -w    PNG width in pixels (default: from print config)
 *   --height, -h   PNG height in pixels (default: from print config)
 *   --dpi          DPI for PNG (default: from print config or 300)
 *   --layers       Comma-separated layer names to include (default: all)
 *   --no-legend    Omit legend from output
 *
 * Examples:
 *   node capture.js ../rhino-python-driver/state.json -o plan.svg
 *   node capture.js ../rhino-python-driver/state.json -f png -o plan.png --dpi 600
 *   node capture.js state.json --layers JIG_PLAN,JIG_BLOCKS,JIG_SITE
 */

import { readFileSync, writeFileSync } from "fs";
import { resolve } from "path";
import { JSDOM } from "jsdom";

// ── Argument Parsing ──────────────────────────────────

const args = process.argv.slice(2);
if (args.length === 0 || args.includes("--help")) {
  console.log(`
Usage: node capture.js <state.json> [options]

Options:
  --output, -o   Output file path (default: plan-layout.svg)
  --format, -f   Output format: svg or png (default: svg)
  --width, -w    PNG width in pixels (default: from print config)
  --height, -h   PNG height in pixels (default: from print config)
  --dpi          DPI for PNG (default: from print config or 300)
  --layers       Comma-separated layers to include (default: all)
  --no-legend    Omit legend

Examples:
  node capture.js ../rhino-python-driver/state.json -o plan.svg
  node capture.js state.json -f png -o plan.png --dpi 600
`);
  process.exit(0);
}

function getArg(flags, fallback) {
  for (const flag of flags) {
    const idx = args.indexOf(flag);
    if (idx !== -1 && idx + 1 < args.length) return args[idx + 1];
  }
  return fallback;
}

const inputFile = args.find(a => !a.startsWith("-"));
const outputFile = getArg(["--output", "-o"], null);
const format = getArg(["--format", "-f"], null);
const pngWidth = getArg(["--width", "-w"], null);
const pngHeight = getArg(["--height", "-h"], null);
const dpiArg = getArg(["--dpi"], null);
const layerFilter = getArg(["--layers"], null);
const noLegend = args.includes("--no-legend");

if (!inputFile) {
  console.error("Error: No input file specified");
  process.exit(1);
}

// Determine format from extension or flag
const outPath = outputFile || `plan-layout.${format || "svg"}`;
const outFormat = format || (outPath.endsWith(".png") ? "png" : "svg");

// ── Load State ────────────────────────────────────────

let state;
try {
  const raw = readFileSync(resolve(inputFile), "utf-8");
  state = JSON.parse(raw);
} catch (e) {
  console.error(`Error loading ${inputFile}: ${e.message}`);
  process.exit(1);
}

if (noLegend && state.legend) state.legend.enabled = false;

// ── SVG Rendering (uses jsdom for DOM API) ────────────

const dom = new JSDOM("<!DOCTYPE html><html><body></body></html>");
const document = dom.window.document;

// Patch global document for svg-renderer.js
globalThis.document = document;

// Dynamically import the renderer (it uses document.createElementNS)
const { renderSVG, exportSVGString, LAYER_ORDER } = await import("./svg-renderer.js");

if (outFormat === "svg") {
  console.log(`Rendering SVG from ${inputFile}...`);

  // Create a temporary SVG element
  const NS = "http://www.w3.org/2000/svg";
  const svgEl = document.createElementNS(NS, "svg");
  svgEl.setAttribute("xmlns", NS);

  const info = renderSVG(svgEl, state);

  // Filter layers if requested
  if (layerFilter) {
    const keep = new Set(layerFilter.split(",").map(s => s.trim()));
    for (const name of LAYER_ORDER) {
      if (!keep.has(name)) {
        const g = svgEl.querySelector(`[data-layer="${name}"]`);
        if (g) g.remove();
      }
    }
  }

  const svgStr = '<?xml version="1.0" encoding="UTF-8"?>\n' + svgEl.outerHTML;
  writeFileSync(resolve(outPath), svgStr, "utf-8");
  console.log(`Written: ${outPath} (${(svgStr.length / 1024).toFixed(1)} KB)`);

} else if (outFormat === "png") {
  // PNG requires puppeteer for rendering SVG → raster
  console.log(`Rendering PNG from ${inputFile}...`);
  console.log("PNG output requires puppeteer. Install with: npm install puppeteer");
  console.log("For SVG output (recommended for PIAF), use: --format svg");

  try {
    const puppeteer = await import("puppeteer");
    const browser = await puppeteer.default.launch({ headless: true });
    const page = await browser.newPage();

    const printCfg = state.print || {};
    const dpi = parseInt(dpiArg) || printCfg.dpi || 300;
    const w = parseInt(pngWidth) || (printCfg.paper_width_in || 24) * dpi;
    const h = parseInt(pngHeight) || (printCfg.paper_height_in || 36) * dpi;

    await page.setViewport({ width: w, height: h, deviceScaleFactor: 1 });

    // Generate SVG and render it
    const NS = "http://www.w3.org/2000/svg";
    const svgEl = document.createElementNS(NS, "svg");
    svgEl.setAttribute("xmlns", NS);
    renderSVG(svgEl, state);
    const svgStr = svgEl.outerHTML;

    const html = `<!DOCTYPE html><html><body style="margin:0;background:white;">
      <div style="width:${w}px;height:${h}px;">${svgStr}</div>
    </body></html>`;

    await page.setContent(html, { waitUntil: "networkidle0" });
    await page.screenshot({ path: resolve(outPath), fullPage: false });
    await browser.close();

    console.log(`Written: ${outPath} (${w}x${h}px @ ${dpi} DPI)`);
  } catch (e) {
    if (e.code === "ERR_MODULE_NOT_FOUND") {
      console.error("puppeteer not found. Install with: npm install puppeteer");
      console.error("Or use SVG format instead: node capture.js state.json -f svg");
    } else {
      console.error(`PNG export error: ${e.message}`);
    }
    process.exit(1);
  }
}

/**
 * Viewer Controller — ties SVG renderer + Three.js viewer together
 * =================================================================
 * Handles: file loading, view switching, layer toggles,
 * SVG pan/zoom, 3D camera presets, element toggles, section slider,
 * export (SVG + PNG).
 */

import { renderSVG, exportSVGString, LAYER_ORDER } from "./svg-renderer.js";
import {
  initThreeViewer, buildScene, captureImage,
  setCameraPreset, setGroupVisible, setSectionHeight,
  setClippingEnabled,
} from "./three-viewer.js";

let currentState = null;
let svgInfo = null;
let threeInitialized = false;

// ── DOM refs ──────────────────────────────────────────

const svgCanvas = document.getElementById("svg-canvas");
const view2d = document.getElementById("view-2d");
const view3d = document.getElementById("view-3d");
const statusText = document.getElementById("status-text");
const mousePos = document.getElementById("mouse-pos");
const panel3d = document.getElementById("panel-3d");
const controls2d = document.getElementById("controls-2d");

// ── SVG Pan / Zoom ────────────────────────────────────

let viewBox = { x: 0, y: 0, w: 400, h: 400 };
let isPanning = false;
let panStart = { x: 0, y: 0 };

function updateViewBox() {
  svgCanvas.setAttribute("viewBox", `${viewBox.x} ${viewBox.y} ${viewBox.w} ${viewBox.h}`);
}

function svgPointFromEvent(e) {
  const rect = svgCanvas.getBoundingClientRect();
  return {
    x: viewBox.x + (e.clientX - rect.left) / rect.width * viewBox.w,
    y: viewBox.y + (e.clientY - rect.top) / rect.height * viewBox.h,
  };
}

view2d.addEventListener("mousedown", (e) => {
  if (e.button !== 0) return;
  isPanning = true;
  panStart = svgPointFromEvent(e);
  view2d.classList.add("panning");
});

window.addEventListener("mousemove", (e) => {
  if (isPanning) {
    const cur = svgPointFromEvent(e);
    viewBox.x -= (cur.x - panStart.x);
    viewBox.y -= (cur.y - panStart.y);
    updateViewBox();
    panStart = svgPointFromEvent(e);
  }
  if (currentState && view2d.classList.contains("active")) {
    const pt = svgPointFromEvent(e);
    mousePos.textContent = `X: ${pt.x.toFixed(1)}  Y: ${(-pt.y).toFixed(1)}`;
  }
});

window.addEventListener("mouseup", () => {
  isPanning = false;
  view2d.classList.remove("panning");
});

view2d.addEventListener("wheel", (e) => {
  e.preventDefault();
  const factor = e.deltaY > 0 ? 1.15 : 0.87;
  const pt = svgPointFromEvent(e);
  viewBox.x = pt.x - (pt.x - viewBox.x) * factor;
  viewBox.y = pt.y - (pt.y - viewBox.y) * factor;
  viewBox.w *= factor;
  viewBox.h *= factor;
  updateViewBox();
}, { passive: false });

// ── Zoom Buttons ──────────────────────────────────────

document.getElementById("btn-zoom-fit").addEventListener("click", () => {
  if (svgInfo) {
    viewBox = { x: svgInfo.minX, y: svgInfo.minY, w: svgInfo.width, h: svgInfo.height };
    updateViewBox();
  }
});

document.getElementById("btn-zoom-in").addEventListener("click", () => {
  const cx = viewBox.x + viewBox.w / 2, cy = viewBox.y + viewBox.h / 2;
  viewBox.w *= 0.7; viewBox.h *= 0.7;
  viewBox.x = cx - viewBox.w / 2; viewBox.y = cy - viewBox.h / 2;
  updateViewBox();
});

document.getElementById("btn-zoom-out").addEventListener("click", () => {
  const cx = viewBox.x + viewBox.w / 2, cy = viewBox.y + viewBox.h / 2;
  viewBox.w *= 1.4; viewBox.h *= 1.4;
  viewBox.x = cx - viewBox.w / 2; viewBox.y = cy - viewBox.h / 2;
  updateViewBox();
});

// ── File Loading ──────────────────────────────────────

const fileInput = document.getElementById("file-input");

document.getElementById("btn-load").addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (ev) => {
    try {
      currentState = JSON.parse(ev.target.result);
      loadState(currentState, file.name);
    } catch (err) {
      statusText.textContent = `Error: ${err.message}`;
    }
  };
  reader.readAsText(file);
});

async function tryAutoLoad() {
  const paths = [
    "../rhino-python-driver/state.json",
    "../CLI JIG TEST/state.json",
    "state.json",
  ];
  for (const p of paths) {
    try {
      const resp = await fetch(p);
      if (resp.ok) {
        currentState = await resp.json();
        loadState(currentState, p);
        return;
      }
    } catch {}
  }
  statusText.textContent = "No file loaded — click Load JSON to open a state.json file";
}

function loadState(state, filename) {
  // Render 2D SVG
  svgInfo = renderSVG(svgCanvas, state);
  viewBox = { x: svgInfo.minX, y: svgInfo.minY, w: svgInfo.width, h: svgInfo.height };
  updateViewBox();

  // Build 3D scene
  if (threeInitialized) buildScene(state);

  // Build layer toggles
  buildLayerToggles();

  // Update section slider range from state
  const wallH = (state.tactile3d || {}).wall_height || 9;
  const cutH = (state.tactile3d || {}).cut_height || 4;
  const slider = document.getElementById("slider-section");
  slider.max = wallH;
  slider.value = cutH;
  document.getElementById("section-height-val").textContent = cutH.toFixed(1);

  const nBays = Object.keys(state.bays).length;
  const nAps = Object.values(state.bays).reduce((s, b) => s + (b.apertures || []).length, 0);
  const nRooms = Object.keys(state.rooms || {}).length;
  statusText.textContent = `${filename} — ${nBays} bays, ${nAps} apertures, ${nRooms} rooms — schema ${state.schema}`;
}

// ── Layer Toggles (2D) ───────────────────────────────

function buildLayerToggles() {
  const container = document.getElementById("layer-toggles");
  container.innerHTML = "";
  for (const name of LAYER_ORDER) {
    const label = document.createElement("label");
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = true;
    cb.addEventListener("change", () => {
      const g = svgCanvas.querySelector(`[data-layer="${name}"]`);
      if (g) g.style.display = cb.checked ? "" : "none";
    });
    label.appendChild(cb);
    label.appendChild(document.createTextNode(name.replace("JIG_", "")));
    container.appendChild(label);
  }
}

// ── View Switching ────────────────────────────────────

const tabs = document.querySelectorAll(".tab");
tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    const viewName = tab.dataset.view;
    document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));

    if (viewName === "2d") {
      view2d.classList.add("active");
      panel3d.classList.add("hidden");
      controls2d.classList.remove("hidden");
    } else {
      view3d.classList.add("active");
      panel3d.classList.remove("hidden");
      controls2d.classList.add("hidden");
      if (!threeInitialized) {
        initThreeViewer(view3d);
        threeInitialized = true;
        if (currentState) buildScene(currentState);
      }
    }
  });
});

// ── 3D Camera Presets ─────────────────────────────────

document.querySelectorAll(".cam-btn").forEach((btn) => {
  btn.addEventListener("click", () => setCameraPreset(btn.dataset.preset));
});

// ── 3D Element Toggles ───────────────────────────────

document.querySelectorAll("#element-toggles input[type=checkbox]").forEach((cb) => {
  cb.addEventListener("change", () => {
    setGroupVisible(cb.dataset.group, cb.checked);
  });
});

// ── Section Cut Slider ────────────────────────────────

const sectionSlider = document.getElementById("slider-section");
const sectionVal = document.getElementById("section-height-val");

sectionSlider.addEventListener("input", () => {
  const h = parseFloat(sectionSlider.value);
  sectionVal.textContent = h.toFixed(1);
  setSectionHeight(h);
});

document.getElementById("chk-clipping").addEventListener("change", (e) => {
  setClippingEnabled(e.target.checked);
});

// ── Export ─────────────────────────────────────────────

document.getElementById("btn-export-svg").addEventListener("click", () => {
  if (!currentState) return;
  const svgStr = exportSVGString(currentState);
  const blob = new Blob([svgStr], { type: "image/svg+xml" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "plan-layout.svg";
  a.click();
  URL.revokeObjectURL(a.href);
});

document.getElementById("btn-export-png").addEventListener("click", () => {
  if (!currentState) return;
  const activeView = document.querySelector(".tab.active").dataset.view;

  if (activeView === "3d" && threeInitialized) {
    const dataUrl = captureImage(2400, 1800);
    if (dataUrl) downloadDataUrl(dataUrl, "plan-layout-3d.png");
  } else {
    exportSVGAsPNG(currentState);
  }
});

function downloadDataUrl(dataUrl, filename) {
  const a = document.createElement("a");
  a.href = dataUrl;
  a.download = filename;
  a.click();
}

function exportSVGAsPNG(state) {
  const svgStr = exportSVGString(state);
  const printCfg = state.print || {};
  const dpi = printCfg.dpi || 300;
  const pxW = (printCfg.paper_width_in || 24) * dpi;
  const pxH = (printCfg.paper_height_in || 36) * dpi;

  const canvas = document.createElement("canvas");
  canvas.width = pxW;
  canvas.height = pxH;
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "white";
  ctx.fillRect(0, 0, pxW, pxH);

  const img = new Image();
  const blob = new Blob([svgStr], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  img.onload = () => {
    ctx.drawImage(img, 0, 0, pxW, pxH);
    URL.revokeObjectURL(url);
    const pngUrl = canvas.toDataURL("image/png");
    downloadDataUrl(pngUrl, "plan-layout-2d.png");
  };
  img.src = url;
}

// ── Keyboard Shortcuts ────────────────────────────────

window.addEventListener("keydown", (e) => {
  // Don't capture when typing in inputs
  if (e.target.tagName === "INPUT") return;
  if (e.key === "1") document.querySelector('[data-view="2d"]').click();
  if (e.key === "2") document.querySelector('[data-view="3d"]').click();
  if (e.key === "f" || e.key === "F") document.getElementById("btn-zoom-fit").click();
  if (e.key === "+" || e.key === "=") document.getElementById("btn-zoom-in").click();
  if (e.key === "-") document.getElementById("btn-zoom-out").click();
  // 3D camera presets
  if (e.key === "p") setCameraPreset("perspective");
  if (e.key === "t") setCameraPreset("plan");
});

// ── Init ──────────────────────────────────────────────

tryAutoLoad();

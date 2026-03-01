/**
 * SVG Renderer for Plan Layout Jig state.json
 * =============================================
 * Direct port of rhino_watcher.py drawing logic to SVG output.
 * Produces precise lineweights (mm), dash patterns, and hatch fills
 * suitable for PIAF tactile printing.
 *
 * All coordinates are in the model's native units (feet).
 * The SVG viewBox maps directly to model space — lineweights are
 * specified in model units to give exact mm at print scale.
 */

const NS = "http://www.w3.org/2000/svg";

const LAYER_ORDER = [
  "JIG_SITE", "JIG_BACKGROUND", "JIG_HATCHES", "JIG_BAYS",
  "JIG_COLUMNS", "JIG_PLAN", "JIG_BLOCKS", "JIG_CORRIDOR",
  "JIG_VOIDS", "JIG_ROOMS", "JIG_LABELS", "JIG_LEGEND",
];

const LAYER_COLORS = {
  JIG_SITE:       "#505050",
  JIG_BACKGROUND: "#ffffff",
  JIG_HATCHES:    "#c8c8c8",
  JIG_BAYS:       "#000000",
  JIG_COLUMNS:    "#000000",
  JIG_PLAN:       "#282828",
  JIG_BLOCKS:     "#000000",
  JIG_CORRIDOR:   "#646464",
  JIG_VOIDS:      "#000000",
  JIG_ROOMS:      "#000000",
  JIG_LABELS:     "#000000",
  JIG_LEGEND:     "#000000",
};

const HATCH_MAP = {
  diagonal: "hatch-diagonal",
  crosshatch: "hatch-crosshatch",
  dots: "hatch-dots",
  horizontal: "hatch-horizontal",
  solid: "hatch-solid",
  hatch1: "hatch-diagonal",
};

// ── Style Helpers ──────────────────────────────────────

function _s(state, key, fallback) {
  return (state.style && state.style[key] !== undefined) ? state.style[key] : fallback;
}

// ── Geometry Helpers ──────────────────────────────────

function getSpacingArrays(bay) {
  const [nx, ny] = bay.bays;
  const sxa = bay.spacing_x, sya = bay.spacing_y;
  let cx, cy;
  if (sxa && sxa.length === nx) {
    cx = [0]; for (const s of sxa) cx.push(cx[cx.length - 1] + s);
  } else {
    const s = bay.spacing[0]; cx = Array.from({length: nx + 1}, (_, i) => i * s);
  }
  if (sya && sya.length === ny) {
    cy = [0]; for (const s of sya) cy.push(cy[cy.length - 1] + s);
  } else {
    const s = bay.spacing[1]; cy = Array.from({length: ny + 1}, (_, j) => j * s);
  }
  return [cx, cy];
}

function localToWorld(lx, ly, origin, rotDeg) {
  const r = rotDeg * Math.PI / 180;
  return [
    origin[0] + lx * Math.cos(r) - ly * Math.sin(r),
    origin[1] + lx * Math.sin(r) + ly * Math.cos(r),
  ];
}

function arcPoints(cx, cy, radius, startDeg, endDeg, n = 24) {
  const pts = [];
  for (let i = 0; i <= n; i++) {
    const a = (startDeg + (endDeg - startDeg) * i / n) * Math.PI / 180;
    pts.push([cx + radius * Math.cos(a), cy + radius * Math.sin(a)]);
  }
  return pts;
}

function calcWallSegments(wallLen, apertures) {
  if (!apertures || apertures.length === 0) return [[0, wallLen]];
  const segs = [];
  let pos = 0;
  for (const ap of apertures) {
    const cn = ap.corner || 0, wd = ap.width || 3;
    if (cn > pos) segs.push([pos, cn]);
    pos = cn + wd;
  }
  if (pos < wallLen) segs.push([pos, wallLen]);
  return segs;
}

// ── SVG Element Helpers ───────────────────────────────

function el(tag, attrs = {}) {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  return e;
}

function svgLine(g, p1, p2, sw) {
  // In SVG, Y is flipped (down is positive), so we negate Y
  g.appendChild(el("line", {
    x1: p1[0], y1: -p1[1], x2: p2[0], y2: -p2[1],
    "stroke-width": sw, stroke: "currentColor", fill: "none",
  }));
}

function svgRect(g, x0, y0, x1, y1, sw) {
  const pts = `${x0},${-y0} ${x1},${-y0} ${x1},${-y1} ${x0},${-y1}`;
  g.appendChild(el("polygon", {
    points: pts, "stroke-width": sw, stroke: "currentColor", fill: "none",
  }));
}

function svgPolyline(g, pts, sw, closed = false) {
  if (pts.length < 2) return null;
  const d = pts.map((p, i) => `${i === 0 ? "M" : "L"}${p[0]},${-p[1]}`).join(" ")
    + (closed ? " Z" : "");
  const path = el("path", {
    d, "stroke-width": sw, stroke: "currentColor", fill: "none",
  });
  g.appendChild(path);
  return path;
}

function svgCircle(g, cx, cy, r, sw) {
  g.appendChild(el("circle", {
    cx, cy: -cy, r, "stroke-width": sw, stroke: "currentColor", fill: "none",
  }));
}

function svgText(g, txt, pt, height) {
  const t = el("text", {
    x: pt[0], y: -pt[1], "font-size": height, fill: "currentColor",
    "font-family": "Arial, sans-serif", "dominant-baseline": "auto",
  });
  t.textContent = txt;
  g.appendChild(t);
}

function svgDashedLine(g, p1, p2, dashLen, gapLen, sw) {
  const dx = p2[0] - p1[0], dy = p2[1] - p1[1];
  const total = Math.hypot(dx, dy);
  if (total < 0.001) return;
  const ux = dx / total, uy = dy / total;
  let pos = 0;
  while (pos < total) {
    const end = Math.min(pos + dashLen, total);
    svgLine(g,
      [p1[0] + ux * pos, p1[1] + uy * pos],
      [p1[0] + ux * end, p1[1] + uy * end], sw);
    pos = end + gapLen;
  }
}

function svgFilledRect(g, x0, y0, x1, y1, fillColor) {
  g.appendChild(el("rect", {
    x: Math.min(x0, x1), y: -Math.max(y0, y1),
    width: Math.abs(x1 - x0), height: Math.abs(y1 - y0),
    fill: fillColor, stroke: "none",
  }));
}

function svgHatchedPolygon(g, pts, patternId, sw) {
  if (!pts || pts.length < 3) return;
  const d = pts.map((p, i) => `${i === 0 ? "M" : "L"}${p[0]},${-p[1]}`).join(" ") + " Z";
  g.appendChild(el("path", {
    d, fill: `url(#${patternId})`, stroke: "currentColor",
    "stroke-width": sw * 0.5,
  }));
}

function svgHatchedCircle(g, cx, cy, r, patternId, sw) {
  g.appendChild(el("circle", {
    cx, cy: -cy, r, fill: `url(#${patternId})`, stroke: "currentColor",
    "stroke-width": sw * 0.5,
  }));
}

function svgFilledPolygon(g, pts, fillColor) {
  if (!pts || pts.length < 3) return;
  const d = pts.map((p, i) => `${i === 0 ? "M" : "L"}${p[0]},${-p[1]}`).join(" ") + " Z";
  g.appendChild(el("path", { d, fill: fillColor, stroke: "none" }));
}

function svgFilledCircle(g, cx, cy, r, fillColor) {
  g.appendChild(el("circle", { cx, cy: -cy, r, fill: fillColor, stroke: "none" }));
}

// ── Hatch Pattern Definitions ─────────────────────────

function createHatchPatterns(defs, scale = 1.0) {
  const s = 4 * scale;

  // Diagonal lines
  const diag = el("pattern", {
    id: "hatch-diagonal", patternUnits: "userSpaceOnUse",
    width: s, height: s, patternTransform: `rotate(45)`,
  });
  diag.appendChild(el("line", {
    x1: 0, y1: 0, x2: 0, y2: s, stroke: "#666", "stroke-width": 0.3,
  }));
  defs.appendChild(diag);

  // Crosshatch
  const cross = el("pattern", {
    id: "hatch-crosshatch", patternUnits: "userSpaceOnUse",
    width: s, height: s,
  });
  cross.appendChild(el("line", {
    x1: 0, y1: 0, x2: s, y2: s, stroke: "#666", "stroke-width": 0.3,
  }));
  cross.appendChild(el("line", {
    x1: s, y1: 0, x2: 0, y2: s, stroke: "#666", "stroke-width": 0.3,
  }));
  defs.appendChild(cross);

  // Dots
  const dots = el("pattern", {
    id: "hatch-dots", patternUnits: "userSpaceOnUse",
    width: s, height: s,
  });
  dots.appendChild(el("circle", {
    cx: s / 2, cy: s / 2, r: 0.5, fill: "#666",
  }));
  defs.appendChild(dots);

  // Horizontal lines
  const horiz = el("pattern", {
    id: "hatch-horizontal", patternUnits: "userSpaceOnUse",
    width: s, height: s,
  });
  horiz.appendChild(el("line", {
    x1: 0, y1: s / 2, x2: s, y2: s / 2, stroke: "#666", "stroke-width": 0.3,
  }));
  defs.appendChild(horiz);

  // Solid fill
  const solid = el("pattern", {
    id: "hatch-solid", patternUnits: "userSpaceOnUse",
    width: 1, height: 1,
  });
  solid.appendChild(el("rect", { x: 0, y: 0, width: 1, height: 1, fill: "#ccc" }));
  defs.appendChild(solid);
}

// ── Layer Drawing Functions ───────────────────────────

function drawSite(g, state, sw) {
  const site = state.site;
  const [ox, oy] = site.origin;
  svgRect(g, ox, oy, ox + site.width, oy + site.height, sw);
}

function drawBackgroundMasks(g, state) {
  const bays = state.bays;
  const pad = _s(state, "background_pad", 2.0);
  const sorted = Object.entries(bays).sort((a, b) => (a[1].z_order || 0) - (b[1].z_order || 0));
  for (const [, bay] of sorted) {
    if ((bay.z_order || 0) <= 0) continue;
    const gt = bay.grid_type || "rectangular";
    const [ox, oy] = bay.origin;
    const rot = bay.rotation_deg;
    if (gt === "rectangular") {
      const [cx, cy] = getSpacingArrays(bay);
      const w = cx[cx.length - 1], h = cy[cy.length - 1];
      const corners = [[-pad, -pad], [w + pad, -pad], [w + pad, h + pad], [-pad, h + pad]];
      const worldPts = corners.map(([lx, ly]) => localToWorld(lx, ly, [ox, oy], rot));
      svgFilledPolygon(g, worldPts, "#ffffff");
    } else {
      const outer = (bay.rings || 4) * (bay.ring_spacing || 20) + pad;
      svgFilledCircle(g, ox, oy, outer, "#ffffff");
    }
  }
}

function drawRoomHatches(g, state, sw) {
  const rooms = state.rooms || {};
  const bays = state.bays || {};
  for (const [, rm] of Object.entries(rooms)) {
    const hi = rm.hatch_image || "none";
    if (hi === "none") continue;
    const rtype = rm.type || "bay";
    const src = rm.source_bay;
    const hs = rm.hatch_scale || 1.0;
    const base = hi.replace(/\.[^.]+$/, "").toLowerCase();
    const patternId = HATCH_MAP[base] || "hatch-diagonal";

    if (rtype === "bay" && src && bays[src]) {
      const bay = bays[src];
      const [ox, oy] = bay.origin;
      const rot = bay.rotation_deg;
      if ((bay.grid_type || "rectangular") === "rectangular") {
        const [cx, cy] = getSpacingArrays(bay);
        const corners = [[0, 0], [cx[cx.length - 1], 0],
          [cx[cx.length - 1], cy[cy.length - 1]], [0, cy[cy.length - 1]]];
        const worldPts = corners.map(([lx, ly]) => localToWorld(lx, ly, [ox, oy], rot));
        svgHatchedPolygon(g, worldPts, patternId, sw);
      } else {
        const outer = (bay.rings || 4) * (bay.ring_spacing || 20);
        svgHatchedCircle(g, ox, oy, outer, patternId, sw);
      }
    } else if (rtype === "void" && src && bays[src]) {
      const bay = bays[src];
      const vc = bay.void_center, vs = bay.void_size;
      if ((bay.void_shape || "rectangle") === "circle") {
        svgHatchedCircle(g, vc[0], vc[1], vs[0] / 2, patternId, sw);
      } else {
        const x0 = vc[0] - vs[0] / 2, y0 = vc[1] - vs[1] / 2;
        const pts = [[x0, y0], [x0 + vs[0], y0], [x0 + vs[0], y0 + vs[1]], [x0, y0 + vs[1]]];
        svgHatchedPolygon(g, pts, patternId, sw);
      }
    } else if (rtype === "landscape") {
      const site = state.site;
      const [sox, soy] = site.origin;
      const pts = [[sox, soy], [sox + site.width, soy],
        [sox + site.width, soy + site.height], [sox, soy + site.height]];
      svgHatchedPolygon(g, pts, patternId, sw);
    }
  }
}

function drawBays(g, state, sw) {
  const sorted = Object.entries(state.bays).sort((a, b) => (a[1].z_order || 0) - (b[1].z_order || 0));
  for (const [, bay] of sorted) {
    const gt = bay.grid_type || "rectangular";
    const [ox, oy] = bay.origin;
    const rot = bay.rotation_deg;
    if (gt === "radial") {
      const nr = bay.rings || 4, rs = bay.ring_spacing || 20;
      const na = bay.arms || 8, arc = bay.arc_deg || 360;
      const arcStart = bay.arc_start_deg || 0;
      for (let ring = 1; ring <= nr; ring++) {
        const r = ring * rs;
        if (arc >= 360) {
          svgCircle(g, ox, oy, r, sw);
        } else {
          const pts = arcPoints(ox, oy, r, arcStart, arcStart + arc, 48);
          svgPolyline(g, pts, sw);
        }
      }
      const outer = nr * rs;
      for (let arm = 0; arm < na; arm++) {
        const angle = arcStart + arc * arm / na;
        const a = angle * Math.PI / 180;
        svgLine(g, [ox, oy], [ox + outer * Math.cos(a), oy + outer * Math.sin(a)], sw);
      }
      if (arc < 360) {
        const a = (arcStart + arc) * Math.PI / 180;
        svgLine(g, [ox, oy], [ox + outer * Math.cos(a), oy + outer * Math.sin(a)], sw);
      }
    } else {
      const [cx, cy] = getSpacingArrays(bay);
      for (const yv of cy)
        svgLine(g, localToWorld(cx[0], yv, [ox, oy], rot),
          localToWorld(cx[cx.length - 1], yv, [ox, oy], rot), sw);
      for (const xv of cx)
        svgLine(g, localToWorld(xv, cy[0], [ox, oy], rot),
          localToWorld(xv, cy[cy.length - 1], [ox, oy], rot), sw);
    }
  }
}

function drawColumns(g, state, sw) {
  const cs = _s(state, "column_size", 1.5);
  const half = cs / 2;
  for (const [, bay] of Object.entries(state.bays)) {
    const gt = bay.grid_type || "rectangular";
    const [ox, oy] = bay.origin;
    const rot = bay.rotation_deg;
    if (gt === "rectangular") {
      const [cx, cy] = getSpacingArrays(bay);
      for (const xv of cx) {
        for (const yv of cy) {
          const [wx, wy] = localToWorld(xv, yv, [ox, oy], rot);
          svgRect(g, wx - half, wy - half, wx + half, wy + half, sw);
        }
      }
    } else {
      svgRect(g, ox - half, oy - half, ox + half, oy + half, sw);
      const nr = bay.rings || 4, rs = bay.ring_spacing || 20;
      const na = bay.arms || 8, arc = bay.arc_deg || 360;
      const arcStart = bay.arc_start_deg || 0;
      for (let ring = 1; ring <= nr; ring++) {
        const r = ring * rs;
        for (let arm = 0; arm < na; arm++) {
          const angle = arcStart + arc * arm / na;
          const a = angle * Math.PI / 180;
          const cpx = ox + r * Math.cos(a), cpy = oy + r * Math.sin(a);
          svgRect(g, cpx - half, cpy - half, cpx + half, cpy + half, sw);
        }
      }
    }
  }
}

function drawWallLine(g, segStart, segEnd, fixedVal, axis, halfT, ox, oy, rot, sw) {
  if (axis === "x") {
    svgLine(g, localToWorld(segStart, fixedVal - halfT, [ox, oy], rot),
      localToWorld(segEnd, fixedVal - halfT, [ox, oy], rot), sw);
    svgLine(g, localToWorld(segStart, fixedVal + halfT, [ox, oy], rot),
      localToWorld(segEnd, fixedVal + halfT, [ox, oy], rot), sw);
  } else {
    svgLine(g, localToWorld(fixedVal - halfT, segStart, [ox, oy], rot),
      localToWorld(fixedVal - halfT, segEnd, [ox, oy], rot), sw);
    svgLine(g, localToWorld(fixedVal + halfT, segStart, [ox, oy], rot),
      localToWorld(fixedVal + halfT, segEnd, [ox, oy], rot), sw);
  }
}

function drawPlanLayout(g, state, sw) {
  for (const [, bay] of Object.entries(state.bays)) {
    if ((bay.grid_type || "rectangular") !== "rectangular") continue;
    const w = bay.walls || {};
    if (!w.enabled) continue;
    const t = w.thickness || 0.5, halfT = t / 2;
    const [ox, oy] = bay.origin;
    const rot = bay.rotation_deg;
    const [cx, cy] = getSpacingArrays(bay);
    const aps = bay.apertures || [];

    // Horizontal walls (x-axis gridlines)
    for (let j = 0; j < cy.length; j++) {
      const yVal = cy[j];
      const wallAps = aps
        .filter(a => a.axis === "x" && a.gridline === j)
        .sort((a, b) => (a.corner || 0) - (b.corner || 0));
      for (const [s, e] of calcWallSegments(cx[cx.length - 1], wallAps))
        drawWallLine(g, s, e, yVal, "x", halfT, ox, oy, rot, sw);
      for (const ap of wallAps) {
        const cn = ap.corner || 0, wd = ap.width || 3;
        for (const xPos of [cn, cn + wd]) {
          svgLine(g, localToWorld(xPos, yVal - halfT, [ox, oy], rot),
            localToWorld(xPos, yVal + halfT, [ox, oy], rot), sw);
        }
      }
    }

    // Vertical walls (y-axis gridlines)
    for (let i = 0; i < cx.length; i++) {
      const xVal = cx[i];
      const wallAps = aps
        .filter(a => a.axis === "y" && a.gridline === i)
        .sort((a, b) => (a.corner || 0) - (b.corner || 0));
      for (const [s, e] of calcWallSegments(cy[cy.length - 1], wallAps))
        drawWallLine(g, s, e, xVal, "y", halfT, ox, oy, rot, sw);
      for (const ap of wallAps) {
        const cn = ap.corner || 0, wd = ap.width || 3;
        for (const yPos of [cn, cn + wd]) {
          svgLine(g, localToWorld(xVal - halfT, yPos, [ox, oy], rot),
            localToWorld(xVal + halfT, yPos, [ox, oy], rot), sw);
        }
      }
    }
  }
}

function drawDoorSymbol(g, ap, bay, ox, oy, rot, cx, cy, wd, arcN, sw) {
  const axis = ap.axis || "x", gl = ap.gridline || 0;
  const cn = ap.corner || 0, hingePos = ap.hinge || "start";
  const swingDir = ap.swing || "positive";
  const swingSign = swingDir === "positive" ? 1 : -1;
  let hx, hy, startAng, endAng;

  if (axis === "x") {
    const yVal = gl < cy.length ? cy[gl] : cy[cy.length - 1];
    hx = hingePos === "start" ? cn : cn + wd;
    hy = yVal;
    if (hingePos === "start") { startAng = 0; endAng = 90 * swingSign; }
    else { startAng = 180; endAng = 180 + 90 * swingSign; }
  } else {
    const xVal = gl < cx.length ? cx[gl] : cx[cx.length - 1];
    hx = xVal;
    hy = hingePos === "start" ? cn : cn + wd;
    if (hingePos === "start") { startAng = 90; endAng = 90 + 90 * swingSign; }
    else { startAng = 270; endAng = 270 + 90 * swingSign; }
  }

  const a0 = Math.min(startAng, endAng), a1 = Math.max(startAng, endAng);
  const arcPts = [];
  for (let k = 0; k <= arcN; k++) {
    const ang = (a0 + (a1 - a0) * k / arcN) * Math.PI / 180;
    arcPts.push(localToWorld(hx + wd * Math.cos(ang), hy + wd * Math.sin(ang), [ox, oy], rot));
  }
  svgPolyline(g, arcPts, sw);
  const leafAng = endAng * Math.PI / 180;
  svgLine(g, localToWorld(hx, hy, [ox, oy], rot),
    localToWorld(hx + wd * Math.cos(leafAng), hy + wd * Math.sin(leafAng), [ox, oy], rot), sw);
}

function drawWindowSymbol(g, ap, bay, ox, oy, rot, cx, cy, wd, sw) {
  const axis = ap.axis || "x", gl = ap.gridline || 0, cn = ap.corner || 0;
  if (axis === "x") {
    const yVal = gl < cy.length ? cy[gl] : cy[cy.length - 1];
    svgLine(g, localToWorld(cn, yVal, [ox, oy], rot),
      localToWorld(cn + wd, yVal, [ox, oy], rot), sw);
  } else {
    const xVal = gl < cx.length ? cx[gl] : cx[cx.length - 1];
    svgLine(g, localToWorld(xVal, cn, [ox, oy], rot),
      localToWorld(xVal, cn + wd, [ox, oy], rot), sw);
  }
}

function drawPortalSymbol(g, ap, bay, ox, oy, rot, cx, cy, wd, sw) {
  const axis = ap.axis || "x", gl = ap.gridline || 0;
  const cn = ap.corner || 0;
  const t = (bay.walls || {}).thickness || 0.5;
  const mark = t * 1.5;
  if (axis === "x") {
    const yVal = gl < cy.length ? cy[gl] : cy[cy.length - 1];
    svgLine(g, localToWorld(cn, yVal - mark, [ox, oy], rot),
      localToWorld(cn, yVal + mark, [ox, oy], rot), sw);
    svgLine(g, localToWorld(cn + wd, yVal - mark, [ox, oy], rot),
      localToWorld(cn + wd, yVal + mark, [ox, oy], rot), sw);
  } else {
    const xVal = gl < cx.length ? cx[gl] : cx[cx.length - 1];
    svgLine(g, localToWorld(xVal - mark, cn, [ox, oy], rot),
      localToWorld(xVal + mark, cn, [ox, oy], rot), sw);
    svgLine(g, localToWorld(xVal - mark, cn + wd, [ox, oy], rot),
      localToWorld(xVal + mark, cn + wd, [ox, oy], rot), sw);
  }
}

function drawBlockInsertions(g, state, sw) {
  const blocks = state.blocks || {};
  const arcN = _s(state, "arc_segments", 16);
  for (const [, bay] of Object.entries(state.bays)) {
    if ((bay.grid_type || "rectangular") !== "rectangular") continue;
    const [ox, oy] = bay.origin;
    const rot = bay.rotation_deg;
    const [cx, cy] = getSpacingArrays(bay);
    for (const ap of (bay.apertures || [])) {
      const atype = ap.type || "door";
      const wd = ap.width || 3;
      if (atype === "door") drawDoorSymbol(g, ap, bay, ox, oy, rot, cx, cy, wd, arcN, sw);
      else if (atype === "window") drawWindowSymbol(g, ap, bay, ox, oy, rot, cx, cy, wd, sw);
      else if (atype === "portal") drawPortalSymbol(g, ap, bay, ox, oy, rot, cx, cy, wd, sw);

      const bk = blocks[atype] || {};
      if (bk.show_label !== false) {
        const axis = ap.axis || "x", gl = ap.gridline || 0, cn = ap.corner || 0;
        const prefix = bk.label_prefix || atype[0].toUpperCase();
        const num = (ap.id || "").replace(/\D/g, "") || ap.id || "";
        const lh = bk.label_height || 1.5;
        const t = (bay.walls || {}).thickness || 0.5;
        const labelOffset = t + lh * 0.5;
        if (axis === "x") {
          const yVal = gl < cy.length ? cy[gl] : cy[cy.length - 1];
          svgText(g, `${prefix}${num}`,
            localToWorld(cn + wd / 2, yVal + labelOffset, [ox, oy], rot), lh);
        } else {
          const xVal = gl < cx.length ? cx[gl] : cx[cx.length - 1];
          svgText(g, `${prefix}${num}`,
            localToWorld(xVal + labelOffset, cn + wd / 2, [ox, oy], rot), lh);
        }
      }
    }
  }

  // Room labels
  const rooms = state.rooms || {};
  const roomBk = blocks.room || {};
  for (const [, rm] of Object.entries(rooms)) {
    if (roomBk.show_label === false) continue;
    const label = rm.label || "";
    if (!label) continue;
    const lh = roomBk.label_height || 3.0;
    const rtype = rm.type || "bay";
    const src = rm.source_bay;
    if (rtype === "bay" && src && state.bays[src]) {
      const bay = state.bays[src];
      const [ox, oy] = bay.origin;
      const rot = bay.rotation_deg;
      if ((bay.grid_type || "rectangular") === "rectangular") {
        const [cxs, cys] = getSpacingArrays(bay);
        svgText(g, label, localToWorld(cxs[cxs.length - 1] / 2, cys[cys.length - 1] / 2,
          [ox, oy], rot), lh);
      } else {
        svgText(g, label, [ox, oy], lh);
      }
    } else if (rtype === "void" && src && state.bays[src]) {
      const vc = state.bays[src].void_center;
      svgText(g, label, [vc[0], vc[1]], lh * 0.8);
    } else if (rtype === "landscape") {
      svgText(g, label, [state.site.origin[0] + 5, state.site.origin[1] + 5], lh * 0.6);
    }
  }
}

function drawCorridors(g, state, sw) {
  const dashLen = _s(state, "corridor_dash_len", 3.0);
  const gapLen = _s(state, "corridor_gap_len", 2.0);
  const corSw = _s(state, "corridor_lineweight_mm", 0.35);

  for (const [, bay] of Object.entries(state.bays)) {
    const cor = bay.corridor || {};
    if (!cor.enabled || (bay.grid_type || "rectangular") !== "rectangular") continue;
    const [ox, oy] = bay.origin;
    const rot = bay.rotation_deg;
    const [cx, cy] = getSpacingArrays(bay);
    const axis = cor.axis || "x";
    const pos = cor.position || 1;
    const halfW = (cor.width || 8) / 2;

    if (axis === "x") {
      if (pos < 0 || pos >= cy.length) continue;
      const yCenter = cy[pos], xS = cx[0], xE = cx[cx.length - 1];
      svgLine(g, localToWorld(xS, yCenter + halfW, [ox, oy], rot),
        localToWorld(xE, yCenter + halfW, [ox, oy], rot), corSw);
      svgLine(g, localToWorld(xS, yCenter - halfW, [ox, oy], rot),
        localToWorld(xE, yCenter - halfW, [ox, oy], rot), corSw);
      svgDashedLine(g,
        localToWorld(xS, yCenter, [ox, oy], rot),
        localToWorld(xE, yCenter, [ox, oy], rot), dashLen, gapLen, corSw);
      // Corridor hatch
      const ht = cor.hatch || "none";
      if (ht !== "none" && ht !== "") {
        const base = ht.replace(/\.[^.]+$/, "").toLowerCase();
        const patternId = HATCH_MAP[base] || "hatch-diagonal";
        const pts = [
          localToWorld(xS, yCenter - halfW, [ox, oy], rot),
          localToWorld(xE, yCenter - halfW, [ox, oy], rot),
          localToWorld(xE, yCenter + halfW, [ox, oy], rot),
          localToWorld(xS, yCenter + halfW, [ox, oy], rot),
        ];
        svgHatchedPolygon(g, pts, patternId, corSw);
      }
    } else {
      if (pos < 0 || pos >= cx.length) continue;
      const xCenter = cx[pos], yS = cy[0], yE = cy[cy.length - 1];
      svgLine(g, localToWorld(xCenter - halfW, yS, [ox, oy], rot),
        localToWorld(xCenter - halfW, yE, [ox, oy], rot), corSw);
      svgLine(g, localToWorld(xCenter + halfW, yS, [ox, oy], rot),
        localToWorld(xCenter + halfW, yE, [ox, oy], rot), corSw);
      svgDashedLine(g,
        localToWorld(xCenter, yS, [ox, oy], rot),
        localToWorld(xCenter, yE, [ox, oy], rot), dashLen, gapLen, corSw);
      const ht = cor.hatch || "none";
      if (ht !== "none" && ht !== "") {
        const base = ht.replace(/\.[^.]+$/, "").toLowerCase();
        const patternId = HATCH_MAP[base] || "hatch-diagonal";
        const pts = [
          localToWorld(xCenter - halfW, yS, [ox, oy], rot),
          localToWorld(xCenter + halfW, yS, [ox, oy], rot),
          localToWorld(xCenter + halfW, yE, [ox, oy], rot),
          localToWorld(xCenter - halfW, yE, [ox, oy], rot),
        ];
        svgHatchedPolygon(g, pts, patternId, corSw);
      }
    }
  }
}

function drawVoids(g, state, sw) {
  for (const [, bay] of Object.entries(state.bays)) {
    const vc = bay.void_center, vs = bay.void_size;
    if ((bay.void_shape || "rectangle") === "circle") {
      svgCircle(g, vc[0], vc[1], vs[0] / 2, sw);
    } else {
      const x0 = vc[0] - vs[0] / 2, y0 = vc[1] - vs[1] / 2;
      svgRect(g, x0, y0, x0 + vs[0], y0 + vs[1], sw);
    }
  }
}

function drawLabels(g, state) {
  const txtH = _s(state, "label_text_height", 0.3);
  const brlH = _s(state, "braille_text_height", 0.5);
  const labelOff = _s(state, "label_offset", 3.0);
  for (const [name, bay] of Object.entries(state.bays)) {
    const gt = bay.grid_type || "rectangular";
    const [ox, oy] = bay.origin;
    let labelPt, braillePt;
    if (gt === "rectangular") {
      const [cxArr, cyArr] = getSpacingArrays(bay);
      const rot = bay.rotation_deg;
      labelPt = localToWorld(cxArr[cxArr.length - 1] / 2, cyArr[cyArr.length - 1] + labelOff, [ox, oy], rot);
      braillePt = localToWorld(cxArr[cxArr.length - 1] / 2,
        cyArr[cyArr.length - 1] + labelOff + brlH * 1.5, [ox, oy], rot);
    } else {
      const outer = (bay.rings || 4) * (bay.ring_spacing || 20);
      labelPt = [ox, oy + outer + labelOff];
      braillePt = [ox, oy + outer + labelOff + brlH * 1.5];
    }
    const label = bay.label || `Bay ${name}`;
    const braille = bay.braille || "";
    if (label) svgText(g, label, labelPt, txtH);
    if (braille) svgText(g, braille, braillePt, brlH);
  }
}

function drawCellRooms(g, state, sw) {
  const txtH = _s(state, "label_text_height", 0.3);
  for (const [bayName, bay] of Object.entries(state.bays)) {
    const cells = bay.cells;
    if (!cells || (bay.grid_type || "rectangular") !== "rectangular") continue;
    const [ox, oy] = bay.origin;
    const rot = bay.rotation_deg;
    const [cx, cy] = getSpacingArrays(bay);
    const [nx, ny] = bay.bays;

    // Build lookup
    const cellNames = {};
    for (const [key, cl] of Object.entries(cells)) {
      const parts = key.split(",");
      if (parts.length === 2) cellNames[key] = cl.name || "";
    }

    // Group by room name
    const rooms = {};
    for (const [key, name] of Object.entries(cellNames)) {
      if (!name) continue;
      const [c, r] = key.split(",").map(Number);
      if (!rooms[name]) rooms[name] = { cells: [], label: "", braille: "",
        hatch: "none", hatch_scale: 1, hatch_rotation: 0, area: 0 };
      rooms[name].cells.push([c, r]);
      const cl = cells[key];
      rooms[name].area += (cx[c + 1] - cx[c]) * (cy[r + 1] - cy[r]);
      if (cl.label && !rooms[name].label) rooms[name].label = cl.label;
      if (cl.braille && !rooms[name].braille) rooms[name].braille = cl.braille;
      if (cl.hatch && cl.hatch !== "none" && rooms[name].hatch === "none") {
        rooms[name].hatch = cl.hatch;
        rooms[name].hatch_scale = cl.hatch_scale || 1;
        rooms[name].hatch_rotation = cl.hatch_rotation || 0;
      }
    }

    for (const [rname, rd] of Object.entries(rooms)) {
      const roomSet = new Set(rd.cells.map(([c, r]) => `${c},${r}`));
      for (const [c, r] of rd.cells) {
        const x0 = cx[c], x1 = cx[c + 1], y0 = cy[r], y1 = cy[r + 1];
        // Boundary edges
        if (c === 0 || !roomSet.has(`${c - 1},${r}`))
          svgLine(g, localToWorld(x0, y0, [ox, oy], rot), localToWorld(x0, y1, [ox, oy], rot), sw);
        if (c === nx - 1 || !roomSet.has(`${c + 1},${r}`))
          svgLine(g, localToWorld(x1, y0, [ox, oy], rot), localToWorld(x1, y1, [ox, oy], rot), sw);
        if (r === 0 || !roomSet.has(`${c},${r - 1}`))
          svgLine(g, localToWorld(x0, y0, [ox, oy], rot), localToWorld(x1, y0, [ox, oy], rot), sw);
        if (r === ny - 1 || !roomSet.has(`${c},${r + 1}`))
          svgLine(g, localToWorld(x0, y1, [ox, oy], rot), localToWorld(x1, y1, [ox, oy], rot), sw);

        // Cell hatch
        const cl = cells[`${c},${r}`] || {};
        const ht = cl.hatch || rd.hatch;
        if (ht !== "none" && ht !== "") {
          const base = ht.replace(/\.[^.]+$/, "").toLowerCase();
          const patternId = HATCH_MAP[base] || "hatch-diagonal";
          const pts = [
            localToWorld(x0, y0, [ox, oy], rot), localToWorld(x1, y0, [ox, oy], rot),
            localToWorld(x1, y1, [ox, oy], rot), localToWorld(x0, y1, [ox, oy], rot),
          ];
          svgHatchedPolygon(g, pts, patternId, sw);
        }
      }

      // Label at centroid
      const label = rd.label || rname;
      const n = rd.cells.length;
      const sumX = rd.cells.reduce((s, [c]) => s + (cx[c] + cx[c + 1]) / 2, 0);
      const sumY = rd.cells.reduce((s, [, r]) => s + (cy[r] + cy[r + 1]) / 2, 0);
      svgText(g, label, localToWorld(sumX / n, sumY / n, [ox, oy], rot), txtH * 6);
      svgText(g, `${Math.round(rd.area).toLocaleString()} sf`,
        localToWorld(sumX / n, sumY / n - txtH * 8, [ox, oy], rot), txtH * 4);
      if (rd.braille) {
        const brlH = _s(state, "braille_text_height", 0.5);
        svgText(g, rd.braille,
          localToWorld(sumX / n, sumY / n - txtH * 14, [ox, oy], rot), brlH);
      }
    }
  }
}

function drawLegend(g, state, sw) {
  const leg = state.legend || {};
  if (!leg.enabled) return;

  const site = state.site;
  const [sox, soy] = site.origin;
  const sW = site.width, sH = site.height;
  const lw = leg.width || 40;
  const pad = leg.padding || 3;
  const rowH = leg.row_height || 7;
  const swatch = leg.swatch_size || 5;
  const txtH = leg.text_height || 2;
  const brlH = leg.braille_height || 2.5;
  const showBraille = leg.show_braille !== false;
  const showHatches = leg.show_hatches !== false;
  const showApertures = leg.show_apertures !== false;

  const rooms = state.rooms || {};
  const blocks = state.blocks || {};
  const hatchedRooms = showHatches
    ? Object.entries(rooms).filter(([, rm]) => (rm.hatch_image || "none") !== "none")
    : [];
  const apTypes = showApertures
    ? ["door", "window", "portal"].filter(t => blocks[t])
    : [];
  const nRows = hatchedRooms.length + apTypes.length;
  if (nRows === 0) return;

  const totalH = pad * 2 + (1 + nRows) * rowH;
  const pos = leg.position || "bottom-right";
  let lox, loy;
  if (pos === "bottom-right") { lox = sox + sW + pad * 2; loy = soy; }
  else if (pos === "bottom-left") { lox = sox - lw - pad * 2; loy = soy; }
  else if (pos === "top-right") { lox = sox + sW + pad * 2; loy = soy + sH - totalH; }
  else if (pos === "top-left") { lox = sox - lw - pad * 2; loy = soy + sH - totalH; }
  else if (pos === "custom") { [lox, loy] = leg.custom_origin || [0, 0]; }
  else { lox = sox + sW + pad * 2; loy = soy; }

  svgRect(g, lox, loy, lox + lw, loy + totalH, sw);
  let cursorY = loy + totalH - pad;
  svgText(g, leg.title || "Legend", [lox + pad, cursorY - txtH], txtH * 1.3);
  cursorY -= rowH;

  for (const [rid, rm] of hatchedRooms.sort((a, b) => a[0].localeCompare(b[0]))) {
    const sx0 = lox + pad, sy0 = cursorY - swatch;
    const hi = rm.hatch_image || "none";
    const base = hi.replace(/\.[^.]+$/, "").toLowerCase();
    const patternId = HATCH_MAP[base] || "hatch-diagonal";
    const pts = [[sx0, sy0], [sx0 + swatch, sy0], [sx0 + swatch, cursorY], [sx0, cursorY]];
    svgHatchedPolygon(g, pts, patternId, sw);
    svgText(g, rm.label || rid, [sx0 + swatch + pad, cursorY - txtH * 1.2], txtH);
    if (showBraille && rm.braille) {
      svgText(g, rm.braille, [sx0 + swatch + pad, cursorY - txtH * 1.2 - brlH * 1.2], brlH);
    }
    cursorY -= rowH;
  }

  for (const bt of apTypes) {
    const bk = blocks[bt];
    const prefix = bk.label_prefix || bt[0].toUpperCase();
    const sx0 = lox + pad, sy0 = cursorY - swatch;
    const midY = sy0 + swatch / 2;
    if (bt === "door") {
      const arcPts = arcPoints(sx0, sy0, swatch, 0, 90, 8);
      svgPolyline(g, arcPts, sw);
      svgLine(g, [sx0, sy0], [sx0 + swatch, sy0], sw);
    } else if (bt === "window") {
      svgLine(g, [sx0, midY], [sx0 + swatch, midY], sw);
      svgLine(g, [sx0, midY - swatch * 0.15], [sx0, midY + swatch * 0.15], sw);
      svgLine(g, [sx0 + swatch, midY - swatch * 0.15], [sx0 + swatch, midY + swatch * 0.15], sw);
    } else if (bt === "portal") {
      svgLine(g, [sx0, sy0], [sx0, sy0 + swatch * 0.4], sw);
      svgLine(g, [sx0 + swatch, sy0], [sx0 + swatch, sy0 + swatch * 0.4], sw);
    }
    svgText(g, `${prefix} = ${bt.charAt(0).toUpperCase() + bt.slice(1)}`,
      [sx0 + swatch + pad, cursorY - txtH * 1.2], txtH);
    cursorY -= rowH;
  }
}

// ── Master Render ─────────────────────────────────────

export function renderSVG(svgEl, state) {
  // Clear
  while (svgEl.firstChild) svgEl.removeChild(svgEl.firstChild);

  // ViewBox: model space with padding
  const site = state.site;
  const [sox, soy] = site.origin;
  const pad = 20;
  // SVG Y is flipped, so we compute accordingly
  const minX = sox - pad;
  const maxX = sox + site.width + pad + 60; // extra for legend
  const minY = -(soy + site.height + pad);
  const maxY = -(soy - pad);
  svgEl.setAttribute("viewBox", `${minX} ${minY} ${maxX - minX} ${maxY - minY}`);

  // Defs (hatch patterns)
  const defs = el("defs");
  createHatchPatterns(defs);
  svgEl.appendChild(defs);

  // Lineweights from style
  const heavySw = _s(state, "heavy_lineweight_mm", 1.4);
  const lightSw = _s(state, "light_lineweight_mm", 0.08);
  const wallSw = _s(state, "wall_lineweight_mm", 0.25);
  const corSw = _s(state, "corridor_lineweight_mm", 0.35);

  // Create layer groups
  const layerGroups = {};
  for (const name of LAYER_ORDER) {
    const g = el("g", {
      id: name,
      "data-layer": name,
      color: LAYER_COLORS[name] || "#000000",
    });
    layerGroups[name] = g;
    svgEl.appendChild(g);
  }

  // Draw each layer
  drawSite(layerGroups.JIG_SITE, state, heavySw);
  drawBackgroundMasks(layerGroups.JIG_BACKGROUND, state);
  drawRoomHatches(layerGroups.JIG_HATCHES, state, lightSw);
  drawBays(layerGroups.JIG_BAYS, state, lightSw);
  drawColumns(layerGroups.JIG_COLUMNS, state, lightSw);
  drawPlanLayout(layerGroups.JIG_PLAN, state, wallSw);
  drawBlockInsertions(layerGroups.JIG_BLOCKS, state, lightSw);
  drawCorridors(layerGroups.JIG_CORRIDOR, state, corSw);
  drawVoids(layerGroups.JIG_VOIDS, state, heavySw * 0.5);
  drawLabels(layerGroups.JIG_LABELS, state);
  drawCellRooms(layerGroups.JIG_ROOMS, state, wallSw);
  drawLegend(layerGroups.JIG_LEGEND, state, lightSw);

  return { layerGroups, minX, minY, width: maxX - minX, height: maxY - minY };
}

export function exportSVGString(state) {
  const tmp = document.createElementNS(NS, "svg");
  tmp.setAttribute("xmlns", NS);
  renderSVG(tmp, state);
  return '<?xml version="1.0" encoding="UTF-8"?>\n' + tmp.outerHTML;
}

export { LAYER_ORDER };

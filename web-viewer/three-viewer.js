/**
 * Three.js 3D Viewer for Plan Layout Jig  v2.0
 * ==============================================
 * Full 3D architectural model from state.json:
 *   - Extruded walls with aperture cutouts
 *   - Door leaf panels with swing arcs
 *   - Window openings (sill + lintel)
 *   - Column extrusions at grid intersections
 *   - Corridor floor zones
 *   - Void boundaries
 *   - Site boundary wall
 *   - Floor slab
 *   - Grid lines etched on floor
 *   - Floating room/bay labels (sprites)
 *   - True clipping plane at section cut height
 *   - Shadow-casting directional light
 *   - Edge outlines for architectural look
 *   - Camera presets (perspective, plan, section)
 */

import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

// ── Geometry Helpers ──────────────────────────────────

function getSpacingArrays(bay) {
  const [nx, ny] = bay.bays;
  const sxa = bay.spacing_x, sya = bay.spacing_y;
  let cx, cy;
  if (sxa && sxa.length === nx) {
    cx = [0]; for (const s of sxa) cx.push(cx[cx.length - 1] + s);
  } else {
    cx = Array.from({length: nx + 1}, (_, i) => i * bay.spacing[0]);
  }
  if (sya && sya.length === ny) {
    cy = [0]; for (const s of sya) cy.push(cy[cy.length - 1] + s);
  } else {
    cy = Array.from({length: ny + 1}, (_, j) => j * bay.spacing[1]);
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

function _s(state, key, fallback) {
  return (state.style && state.style[key] !== undefined) ? state.style[key] : fallback;
}

// ── Shape Extrusion Helper ────────────────────────────

function extrudeShape(corners, height) {
  const shape = new THREE.Shape();
  shape.moveTo(corners[0][0], corners[0][1]);
  for (let i = 1; i < corners.length; i++) shape.lineTo(corners[i][0], corners[i][1]);
  shape.closePath();
  return new THREE.ExtrudeGeometry(shape, { depth: height, bevelEnabled: false });
}

// ── Materials ─────────────────────────────────────────

const MATERIALS = {};

function initMaterials(clippingPlanes) {
  const cp = clippingPlanes || [];
  MATERIALS.wall = new THREE.MeshStandardMaterial({
    color: 0xd4a373, roughness: 0.85, metalness: 0.0,
    clippingPlanes: cp, clipShadows: true,
  });
  MATERIALS.wallEdge = new THREE.LineBasicMaterial({ color: 0x333333 });
  MATERIALS.column = new THREE.MeshStandardMaterial({
    color: 0x8b8b8b, roughness: 0.6, metalness: 0.15,
    clippingPlanes: cp, clipShadows: true,
  });
  MATERIALS.floor = new THREE.MeshStandardMaterial({
    color: 0xe8e0d4, roughness: 0.95, metalness: 0.0,
  });
  MATERIALS.corridor = new THREE.MeshStandardMaterial({
    color: 0xb8cfe0, roughness: 0.9, metalness: 0.0,
    transparent: true, opacity: 0.6,
  });
  MATERIALS.void = new THREE.MeshStandardMaterial({
    color: 0x90c090, roughness: 0.9, metalness: 0.0,
    transparent: true, opacity: 0.3, side: THREE.DoubleSide,
  });
  MATERIALS.site = new THREE.MeshStandardMaterial({
    color: 0x999999, roughness: 0.8, metalness: 0.0,
    transparent: true, opacity: 0.4,
  });
  MATERIALS.door = new THREE.MeshStandardMaterial({
    color: 0x6b4226, roughness: 0.7, metalness: 0.05,
    clippingPlanes: cp, clipShadows: true,
  });
  MATERIALS.window = new THREE.MeshStandardMaterial({
    color: 0x88bbdd, roughness: 0.2, metalness: 0.1,
    transparent: true, opacity: 0.4,
    clippingPlanes: cp, clipShadows: true,
  });
  MATERIALS.sectionPlane = new THREE.MeshBasicMaterial({
    color: 0xff4444, transparent: true, opacity: 0.08,
    side: THREE.DoubleSide, depthWrite: false,
  });
  MATERIALS.ground = new THREE.MeshStandardMaterial({
    color: 0xd0d0c0, roughness: 1.0, metalness: 0.0,
  });
  MATERIALS.gridLine = new THREE.LineBasicMaterial({ color: 0x666666 });
}

// ── Element Groups (for toggle visibility) ────────────

const GROUPS = {
  walls: null,
  columns: null,
  floor: null,
  corridors: null,
  voids: null,
  doors: null,
  windows: null,
  site: null,
  grid: null,
  labels: null,
  section: null,
  edges: null,
  ground: null,
};

function makeGroup(name) {
  const g = new THREE.Group();
  g.name = name;
  GROUPS[name] = g;
  return g;
}

// ── Build: Walls ──────────────────────────────────────

function buildWalls(state, extrudeH) {
  const group = makeGroup("walls");
  for (const [, bay] of Object.entries(state.bays)) {
    if ((bay.grid_type || "rectangular") !== "rectangular") continue;
    const w = bay.walls || {};
    if (!w.enabled) continue;
    const t = w.thickness || 0.5, halfT = t / 2;
    const [ox, oy] = bay.origin;
    const rot = bay.rotation_deg;
    const [cx, cy] = getSpacingArrays(bay);
    const aps = bay.apertures || [];

    const addWall = (segStart, segEnd, fixedVal, axis) => {
      if (segEnd - segStart < 0.001) return;
      let corners;
      if (axis === "x") {
        corners = [
          localToWorld(segStart, fixedVal - halfT, [ox, oy], rot),
          localToWorld(segEnd,   fixedVal - halfT, [ox, oy], rot),
          localToWorld(segEnd,   fixedVal + halfT, [ox, oy], rot),
          localToWorld(segStart, fixedVal + halfT, [ox, oy], rot),
        ];
      } else {
        corners = [
          localToWorld(fixedVal - halfT, segStart, [ox, oy], rot),
          localToWorld(fixedVal + halfT, segStart, [ox, oy], rot),
          localToWorld(fixedVal + halfT, segEnd,   [ox, oy], rot),
          localToWorld(fixedVal - halfT, segEnd,   [ox, oy], rot),
        ];
      }
      const geom = extrudeShape(corners, extrudeH);
      const mesh = new THREE.Mesh(geom, MATERIALS.wall);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      group.add(mesh);

      // Edge outlines
      const edgeGeom = new THREE.EdgesGeometry(geom, 15);
      const edges = new THREE.LineSegments(edgeGeom, MATERIALS.wallEdge);
      GROUPS.edges.add(edges);
    };

    // Horizontal walls
    for (let j = 0; j < cy.length; j++) {
      const yVal = cy[j];
      const wallAps = aps.filter(a => a.axis === "x" && a.gridline === j)
        .sort((a, b) => (a.corner || 0) - (b.corner || 0));
      for (const [s, e] of calcWallSegments(cx[cx.length - 1], wallAps))
        addWall(s, e, yVal, "x");
    }
    // Vertical walls
    for (let i = 0; i < cx.length; i++) {
      const xVal = cx[i];
      const wallAps = aps.filter(a => a.axis === "y" && a.gridline === i)
        .sort((a, b) => (a.corner || 0) - (b.corner || 0));
      for (const [s, e] of calcWallSegments(cy[cy.length - 1], wallAps))
        addWall(s, e, xVal, "y");
    }
  }
  return group;
}

// ── Build: Columns ────────────────────────────────────

function buildColumns(state, extrudeH) {
  const group = makeGroup("columns");
  const cs = _s(state, "column_size", 1.5);
  const half = cs / 2;
  for (const [, bay] of Object.entries(state.bays)) {
    const gt = bay.grid_type || "rectangular";
    const [ox, oy] = bay.origin;
    const rot = bay.rotation_deg;
    if (gt === "rectangular") {
      const [cx, cy] = getSpacingArrays(bay);
      for (const xv of cx) for (const yv of cy) {
        const [wx, wy] = localToWorld(xv, yv, [ox, oy], rot);
        const geom = new THREE.BoxGeometry(cs, cs, extrudeH);
        const mesh = new THREE.Mesh(geom, MATERIALS.column);
        mesh.position.set(wx, wy, extrudeH / 2);
        mesh.castShadow = true;
        group.add(mesh);
      }
    } else {
      // Center column
      const geom0 = new THREE.BoxGeometry(cs, cs, extrudeH);
      const m0 = new THREE.Mesh(geom0, MATERIALS.column);
      m0.position.set(ox, oy, extrudeH / 2);
      m0.castShadow = true;
      group.add(m0);
      // Ring/arm columns
      const nr = bay.rings || 4, rs = bay.ring_spacing || 20;
      const na = bay.arms || 8, arc = bay.arc_deg || 360;
      const arcStart = bay.arc_start_deg || 0;
      for (let ring = 1; ring <= nr; ring++) {
        const r = ring * rs;
        for (let arm = 0; arm < na; arm++) {
          const angle = (arcStart + arc * arm / na) * Math.PI / 180;
          const cpx = ox + r * Math.cos(angle), cpy = oy + r * Math.sin(angle);
          const geom = new THREE.BoxGeometry(cs, cs, extrudeH);
          const mesh = new THREE.Mesh(geom, MATERIALS.column);
          mesh.position.set(cpx, cpy, extrudeH / 2);
          mesh.castShadow = true;
          group.add(mesh);
        }
      }
    }
  }
  return group;
}

// ── Build: Floor Slab ─────────────────────────────────

function buildFloor(state, thickness) {
  const group = makeGroup("floor");
  const site = state.site;
  const [sox, soy] = site.origin;
  const sw = site.width, sh = site.height;
  const geom = new THREE.BoxGeometry(sw, sh, thickness);
  const mesh = new THREE.Mesh(geom, MATERIALS.floor);
  mesh.position.set(sox + sw / 2, soy + sh / 2, -thickness / 2);
  mesh.receiveShadow = true;
  group.add(mesh);
  return group;
}

// ── Build: Corridors ──────────────────────────────────

function buildCorridors(state) {
  const group = makeGroup("corridors");
  const stripH = 0.15; // thin raised floor strip
  for (const [, bay] of Object.entries(state.bays)) {
    const cor = bay.corridor || {};
    if (!cor.enabled || (bay.grid_type || "rectangular") !== "rectangular") continue;
    const [ox, oy] = bay.origin;
    const rot = bay.rotation_deg;
    const [cx, cy] = getSpacingArrays(bay);
    const axis = cor.axis || "x";
    const pos = cor.position || 1;
    const halfW = (cor.width || 8) / 2;

    let corners;
    if (axis === "x") {
      if (pos < 0 || pos >= cy.length) continue;
      const yCenter = cy[pos], xS = cx[0], xE = cx[cx.length - 1];
      corners = [
        localToWorld(xS, yCenter - halfW, [ox, oy], rot),
        localToWorld(xE, yCenter - halfW, [ox, oy], rot),
        localToWorld(xE, yCenter + halfW, [ox, oy], rot),
        localToWorld(xS, yCenter + halfW, [ox, oy], rot),
      ];
    } else {
      if (pos < 0 || pos >= cx.length) continue;
      const xCenter = cx[pos], yS = cy[0], yE = cy[cy.length - 1];
      corners = [
        localToWorld(xCenter - halfW, yS, [ox, oy], rot),
        localToWorld(xCenter + halfW, yS, [ox, oy], rot),
        localToWorld(xCenter + halfW, yE, [ox, oy], rot),
        localToWorld(xCenter - halfW, yE, [ox, oy], rot),
      ];
    }
    const geom = extrudeShape(corners, stripH);
    const mesh = new THREE.Mesh(geom, MATERIALS.corridor);
    mesh.position.z = 0.01; // sit just above floor
    group.add(mesh);
  }
  return group;
}

// ── Build: Voids ──────────────────────────────────────

function buildVoids(state, extrudeH) {
  const group = makeGroup("voids");
  for (const [, bay] of Object.entries(state.bays)) {
    const vc = bay.void_center, vs = bay.void_size;
    if (!vc || !vs) continue;
    if ((bay.void_shape || "rectangle") === "circle") {
      const r = vs[0] / 2;
      const geom = new THREE.CylinderGeometry(r, r, extrudeH, 32);
      const mesh = new THREE.Mesh(geom, MATERIALS.void);
      // CylinderGeometry is Y-up by default, rotate to Z-up
      mesh.rotation.x = Math.PI / 2;
      mesh.position.set(vc[0], vc[1], extrudeH / 2);
      group.add(mesh);
      // Outline ring at top
      const ringGeom = new THREE.RingGeometry(r - 0.3, r, 32);
      const ring = new THREE.Mesh(ringGeom, new THREE.MeshBasicMaterial({
        color: 0x338833, side: THREE.DoubleSide,
      }));
      ring.position.set(vc[0], vc[1], extrudeH + 0.05);
      group.add(ring);
    } else {
      const w = vs[0], h = vs[1];
      const x0 = vc[0] - w / 2, y0 = vc[1] - h / 2;
      const corners = [[x0, y0], [x0 + w, y0], [x0 + w, y0 + h], [x0, y0 + h]];
      const geom = extrudeShape(corners, extrudeH);
      const mesh = new THREE.Mesh(geom, MATERIALS.void);
      group.add(mesh);
      // Top outline
      const edgeGeom = new THREE.EdgesGeometry(geom, 15);
      const edges = new THREE.LineSegments(edgeGeom, new THREE.LineBasicMaterial({ color: 0x338833 }));
      group.add(edges);
    }
  }
  return group;
}

// ── Build: Doors ──────────────────────────────────────

function buildDoors(state, extrudeH) {
  const group = makeGroup("doors");
  const leafThickness = 0.15;
  for (const [, bay] of Object.entries(state.bays)) {
    if ((bay.grid_type || "rectangular") !== "rectangular") continue;
    const [ox, oy] = bay.origin;
    const rot = bay.rotation_deg;
    const [cx, cy] = getSpacingArrays(bay);
    for (const ap of (bay.apertures || [])) {
      if (ap.type !== "door") continue;
      const axis = ap.axis || "x", gl = ap.gridline || 0;
      const cn = ap.corner || 0, wd = ap.width || 3;
      const hingePos = ap.hinge || "start";
      const swingDir = ap.swing || "positive";
      const doorH = Math.min(ap.height || 7, extrudeH);

      // Door leaf — thin panel at swing angle (shown at 30 degrees open)
      const swingAngle = (swingDir === "positive" ? 1 : -1) * 30 * Math.PI / 180;
      let hx, hy, leafRotation;

      if (axis === "x") {
        const yVal = gl < cy.length ? cy[gl] : cy[cy.length - 1];
        hx = hingePos === "start" ? cn : cn + wd;
        hy = yVal;
        leafRotation = rot * Math.PI / 180 + swingAngle;
      } else {
        const xVal = gl < cx.length ? cx[gl] : cx[cx.length - 1];
        hx = xVal;
        hy = hingePos === "start" ? cn : cn + wd;
        leafRotation = rot * Math.PI / 180 + Math.PI / 2 + swingAngle;
      }

      const [whx, why] = localToWorld(hx, hy, [ox, oy], rot);

      // Door leaf panel
      const leafGeom = new THREE.BoxGeometry(wd, leafThickness, doorH);
      const leaf = new THREE.Mesh(leafGeom, MATERIALS.door);
      leaf.position.set(whx, why, doorH / 2);
      // Offset pivot to hinge edge
      leafGeom.translate(wd / 2, 0, 0);
      leaf.rotation.z = leafRotation;
      leaf.castShadow = true;
      group.add(leaf);

      // Swing arc on floor (polyline)
      const arcN = 16;
      const startAng = leafRotation;
      const fullSwingAng = (swingDir === "positive" ? 1 : -1) * 90 * Math.PI / 180
        + rot * Math.PI / 180;
      const arcPts = [];
      for (let k = 0; k <= arcN; k++) {
        const a = startAng + (fullSwingAng - startAng) * k / arcN;
        arcPts.push(new THREE.Vector3(
          whx + wd * Math.cos(a), why + wd * Math.sin(a), 0.05));
      }
      const arcGeom = new THREE.BufferGeometry().setFromPoints(arcPts);
      const arc = new THREE.Line(arcGeom, new THREE.LineBasicMaterial({
        color: 0x6b4226, linewidth: 2 }));
      group.add(arc);
    }
  }
  return group;
}

// ── Build: Windows ────────────────────────────────────

function buildWindows(state, extrudeH) {
  const group = makeGroup("windows");
  const sillHeight = 2.5;  // typical sill
  for (const [, bay] of Object.entries(state.bays)) {
    if ((bay.grid_type || "rectangular") !== "rectangular") continue;
    const w = bay.walls || {};
    if (!w.enabled) continue;
    const t = w.thickness || 0.5, halfT = t / 2;
    const [ox, oy] = bay.origin;
    const rot = bay.rotation_deg;
    const [cx, cy] = getSpacingArrays(bay);
    for (const ap of (bay.apertures || [])) {
      if (ap.type !== "window") continue;
      const axis = ap.axis || "x", gl = ap.gridline || 0;
      const cn = ap.corner || 0, wd = ap.width || 6;
      const winH = Math.min(ap.height || 4, extrudeH - sillHeight);
      if (winH <= 0) continue;

      let corners;
      if (axis === "x") {
        const yVal = gl < cy.length ? cy[gl] : cy[cy.length - 1];
        corners = [
          localToWorld(cn,      yVal - halfT, [ox, oy], rot),
          localToWorld(cn + wd, yVal - halfT, [ox, oy], rot),
          localToWorld(cn + wd, yVal + halfT, [ox, oy], rot),
          localToWorld(cn,      yVal + halfT, [ox, oy], rot),
        ];
      } else {
        const xVal = gl < cx.length ? cx[gl] : cx[cx.length - 1];
        corners = [
          localToWorld(xVal - halfT, cn,      [ox, oy], rot),
          localToWorld(xVal + halfT, cn,      [ox, oy], rot),
          localToWorld(xVal + halfT, cn + wd, [ox, oy], rot),
          localToWorld(xVal - halfT, cn + wd, [ox, oy], rot),
        ];
      }

      // Glass pane
      const glassGeom = extrudeShape(corners, winH);
      const glass = new THREE.Mesh(glassGeom, MATERIALS.window);
      glass.position.z = sillHeight;
      group.add(glass);

      // Edge outlines
      const edgeGeom = new THREE.EdgesGeometry(glassGeom, 15);
      const edges = new THREE.LineSegments(edgeGeom,
        new THREE.LineBasicMaterial({ color: 0x5588aa }));
      edges.position.z = sillHeight;
      group.add(edges);
    }
  }
  return group;
}

// ── Build: Site Boundary ──────────────────────────────

function buildSite(state, extrudeH) {
  const group = makeGroup("site");
  const site = state.site;
  const [sox, soy] = site.origin;
  const sw = site.width, sh = site.height;
  const wallH = extrudeH * 0.2;
  const wallT = 0.3;

  // Four walls around site perimeter
  const sides = [
    [[sox, soy], [sox + sw, soy]],           // bottom
    [[sox + sw, soy], [sox + sw, soy + sh]], // right
    [[sox + sw, soy + sh], [sox, soy + sh]], // top
    [[sox, soy + sh], [sox, soy]],           // left
  ];
  for (const [p1, p2] of sides) {
    const dx = p2[0] - p1[0], dy = p2[1] - p1[1];
    const len = Math.hypot(dx, dy);
    const nx = -dy / len * wallT / 2, ny = dx / len * wallT / 2;
    const corners = [
      [p1[0] - nx, p1[1] - ny], [p2[0] - nx, p2[1] - ny],
      [p2[0] + nx, p2[1] + ny], [p1[0] + nx, p1[1] + ny],
    ];
    const geom = extrudeShape(corners, wallH);
    const mesh = new THREE.Mesh(geom, MATERIALS.site);
    group.add(mesh);
  }
  return group;
}

// ── Build: Grid Lines on Floor ────────────────────────

function buildGrid(state) {
  const group = makeGroup("grid");
  const points = [];
  for (const [, bay] of Object.entries(state.bays)) {
    const gt = bay.grid_type || "rectangular";
    const [ox, oy] = bay.origin;
    const rot = bay.rotation_deg;
    if (gt === "rectangular") {
      const [cx, cy] = getSpacingArrays(bay);
      for (const yv of cy) {
        const p1 = localToWorld(cx[0], yv, [ox, oy], rot);
        const p2 = localToWorld(cx[cx.length - 1], yv, [ox, oy], rot);
        points.push(new THREE.Vector3(p1[0], p1[1], 0.02),
          new THREE.Vector3(p2[0], p2[1], 0.02));
      }
      for (const xv of cx) {
        const p1 = localToWorld(xv, cy[0], [ox, oy], rot);
        const p2 = localToWorld(xv, cy[cy.length - 1], [ox, oy], rot);
        points.push(new THREE.Vector3(p1[0], p1[1], 0.02),
          new THREE.Vector3(p2[0], p2[1], 0.02));
      }
    } else {
      const nr = bay.rings || 4, rs = bay.ring_spacing || 20;
      const na = bay.arms || 8, arc = bay.arc_deg || 360;
      const arcStart = bay.arc_start_deg || 0;
      for (let ring = 1; ring <= nr; ring++) {
        const r = ring * rs;
        const n = 48;
        for (let i = 0; i < n; i++) {
          const a0 = (arcStart + arc * i / n) * Math.PI / 180;
          const a1 = (arcStart + arc * (i + 1) / n) * Math.PI / 180;
          points.push(
            new THREE.Vector3(ox + r * Math.cos(a0), oy + r * Math.sin(a0), 0.02),
            new THREE.Vector3(ox + r * Math.cos(a1), oy + r * Math.sin(a1), 0.02));
        }
      }
      const outer = nr * rs;
      for (let arm = 0; arm < na; arm++) {
        const angle = (arcStart + arc * arm / na) * Math.PI / 180;
        points.push(
          new THREE.Vector3(ox, oy, 0.02),
          new THREE.Vector3(ox + outer * Math.cos(angle), oy + outer * Math.sin(angle), 0.02));
      }
    }
  }
  if (points.length > 0) {
    const geom = new THREE.BufferGeometry().setFromPoints(points);
    group.add(new THREE.LineSegments(geom, MATERIALS.gridLine));
  }
  return group;
}

// ── Build: Labels (Sprite Text) ───────────────────────

function makeTextSprite(text, opts = {}) {
  const fontSize = opts.fontSize || 48;
  const color = opts.color || "#222222";
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d");
  ctx.font = `bold ${fontSize}px Arial`;
  const metrics = ctx.measureText(text);
  const textW = metrics.width;
  canvas.width = Math.ceil(textW) + 16;
  canvas.height = fontSize + 16;
  ctx.font = `bold ${fontSize}px Arial`;
  ctx.fillStyle = color;
  ctx.textBaseline = "top";
  ctx.fillText(text, 8, 8);

  const tex = new THREE.CanvasTexture(canvas);
  tex.minFilter = THREE.LinearFilter;
  const mat = new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false });
  const sprite = new THREE.Sprite(mat);
  const aspect = canvas.width / canvas.height;
  const scale = opts.scale || 12;
  sprite.scale.set(scale * aspect, scale, 1);
  return sprite;
}

function buildLabels(state, extrudeH) {
  const group = makeGroup("labels");
  const labelZ = extrudeH + 2;
  for (const [name, bay] of Object.entries(state.bays)) {
    const gt = bay.grid_type || "rectangular";
    const [ox, oy] = bay.origin;
    const label = bay.label || `Bay ${name}`;
    let px, py;
    if (gt === "rectangular") {
      const [cxArr, cyArr] = getSpacingArrays(bay);
      const rot = bay.rotation_deg;
      [px, py] = localToWorld(cxArr[cxArr.length - 1] / 2, cyArr[cyArr.length - 1] / 2,
        [ox, oy], rot);
    } else {
      px = ox; py = oy;
    }
    const sprite = makeTextSprite(label, { scale: 8 });
    sprite.position.set(px, py, labelZ);
    group.add(sprite);
  }
  // Room labels
  const rooms = state.rooms || {};
  for (const [rid, rm] of Object.entries(rooms)) {
    const rLabel = rm.label || "";
    if (!rLabel || rm.type === "landscape") continue;
    const src = rm.source_bay;
    if (!src || !state.bays[src]) continue;
    const bay = state.bays[src];
    let px, py;
    if (rm.type === "void") {
      const vc = bay.void_center;
      if (!vc) continue;
      px = vc[0]; py = vc[1];
    } else if ((bay.grid_type || "rectangular") === "rectangular") {
      const [cxs, cys] = getSpacingArrays(bay);
      const rot = bay.rotation_deg;
      [px, py] = localToWorld(cxs[cxs.length - 1] / 2, cys[cys.length - 1] / 2,
        [bay.origin[0], bay.origin[1]], rot);
      continue; // skip — bay label already covers this
    } else {
      continue;
    }
    const sprite = makeTextSprite(rLabel, { scale: 6, color: "#336633" });
    sprite.position.set(px, py, labelZ * 0.8);
    group.add(sprite);
  }
  return group;
}

// ── Build: Section Plane ──────────────────────────────

function buildSectionPlane(state, cutHeight) {
  const group = makeGroup("section");
  const site = state.site;
  const [sox, soy] = site.origin;
  const sw = site.width, sh = site.height;
  const pad = 20;
  const planeGeom = new THREE.PlaneGeometry(sw + pad * 2, sh + pad * 2);
  const plane = new THREE.Mesh(planeGeom, MATERIALS.sectionPlane);
  plane.position.set(sox + sw / 2, soy + sh / 2, cutHeight);
  group.add(plane);
  return group;
}

// ── Build: Ground Plane ───────────────────────────────

function buildGround(state) {
  const group = makeGroup("ground");
  const site = state.site;
  const [sox, soy] = site.origin;
  const sw = site.width, sh = site.height;
  const pad = 40;
  const geom = new THREE.PlaneGeometry(sw + pad * 2, sh + pad * 2);
  const mesh = new THREE.Mesh(geom, MATERIALS.ground);
  mesh.position.set(sox + sw / 2, soy + sh / 2, -0.6);
  mesh.receiveShadow = true;
  group.add(mesh);

  // Ground grid
  const gridPts = [];
  const step = 10;
  const x0 = sox - pad, x1 = sox + sw + pad;
  const y0 = soy - pad, y1 = soy + sh + pad;
  for (let x = Math.floor(x0 / step) * step; x <= x1; x += step) {
    gridPts.push(new THREE.Vector3(x, y0, -0.55), new THREE.Vector3(x, y1, -0.55));
  }
  for (let y = Math.floor(y0 / step) * step; y <= y1; y += step) {
    gridPts.push(new THREE.Vector3(x0, y, -0.55), new THREE.Vector3(x1, y, -0.55));
  }
  const gridGeom = new THREE.BufferGeometry().setFromPoints(gridPts);
  group.add(new THREE.LineSegments(gridGeom,
    new THREE.LineBasicMaterial({ color: 0xbbbbaa, transparent: true, opacity: 0.4 })));
  return group;
}

// ── Scene State ───────────────────────────────────────

let scene, camera, renderer, controls;
let clippingPlane;
let currentState = null;

export function initThreeViewer(container) {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xeeeee8);

  // Clipping plane (section cut)
  clippingPlane = new THREE.Plane(new THREE.Vector3(0, 0, -1), 4);

  // Camera
  const aspect = container.clientWidth / container.clientHeight;
  camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 10000);
  camera.position.set(100, -150, 200);
  camera.up.set(0, 0, 1);

  // Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.localClippingEnabled = true;
  container.appendChild(renderer.domElement);

  // Controls
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.1;
  controls.target.set(90, 130, 0);
  controls.maxPolarAngle = Math.PI * 0.95;

  // Lighting — key + fill + ambient
  const ambient = new THREE.AmbientLight(0xffffff, 0.5);
  scene.add(ambient);

  const hemi = new THREE.HemisphereLight(0xddeeff, 0xd4c5a9, 0.4);
  scene.add(hemi);

  const sun = new THREE.DirectionalLight(0xffffff, 1.0);
  sun.position.set(80, -60, 180);
  sun.castShadow = true;
  sun.shadow.mapSize.width = 2048;
  sun.shadow.mapSize.height = 2048;
  sun.shadow.camera.left = -200;
  sun.shadow.camera.right = 200;
  sun.shadow.camera.top = 200;
  sun.shadow.camera.bottom = -200;
  sun.shadow.camera.near = 1;
  sun.shadow.camera.far = 500;
  sun.shadow.bias = -0.001;
  scene.add(sun);

  const fill = new THREE.DirectionalLight(0xffffff, 0.3);
  fill.position.set(-100, 100, 100);
  scene.add(fill);

  // Axes
  const axes = new THREE.AxesHelper(15);
  scene.add(axes);

  // Resize
  const ro = new ResizeObserver(() => {
    const w = container.clientWidth, h = container.clientHeight;
    if (w === 0 || h === 0) return;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  });
  ro.observe(container);

  animate();
  return { scene, camera, renderer, controls };
}

function animate() {
  requestAnimationFrame(animate);
  if (controls) controls.update();
  if (renderer && scene && camera) renderer.render(scene, camera);
}

// ── Master Build ──────────────────────────────────────

export function buildScene(state) {
  if (!scene) return;
  currentState = state;

  // Remove old groups
  for (const key of Object.keys(GROUPS)) {
    if (GROUPS[key]) { scene.remove(GROUPS[key]); GROUPS[key] = null; }
  }

  const t3 = state.tactile3d || {};
  const wallHeight = t3.wall_height || 9;
  const cutHeight = t3.cut_height || 4;
  const floorThick = t3.floor_thickness || 0.5;
  const floorOn = t3.floor_enabled !== false;
  const scaleFactor = t3.scale_factor || 1.0;
  const extrudeH = Math.min(wallHeight, cutHeight);

  // Update clipping plane
  clippingPlane.constant = cutHeight;

  // Initialize materials with clipping
  initMaterials([clippingPlane]);

  // Edges group must exist before walls (walls add to it)
  makeGroup("edges");

  // Build all element groups
  scene.add(buildWalls(state, extrudeH));
  scene.add(buildColumns(state, extrudeH));
  if (floorOn) scene.add(buildFloor(state, floorThick));
  scene.add(buildCorridors(state));
  scene.add(buildVoids(state, extrudeH));
  scene.add(buildDoors(state, extrudeH));
  scene.add(buildWindows(state, extrudeH));
  scene.add(buildSite(state, extrudeH));
  scene.add(buildGrid(state));
  scene.add(buildLabels(state, extrudeH));
  scene.add(buildSectionPlane(state, cutHeight));
  scene.add(buildGround(state));
  scene.add(GROUPS.edges);

  // Apply scale factor
  if (scaleFactor !== 1.0) {
    for (const key of Object.keys(GROUPS)) {
      if (GROUPS[key]) GROUPS[key].scale.setScalar(scaleFactor);
    }
  }

  // Camera → center of site
  const site = state.site;
  const cx = site.origin[0] + site.width / 2;
  const cy = site.origin[1] + site.height / 2;
  controls.target.set(cx, cy, 0);
  camera.position.set(cx + site.width * 0.8, cy - site.height * 0.8, site.height * 0.6);
  controls.update();
}

// ── Camera Presets ────────────────────────────────────

export function setCameraPreset(preset) {
  if (!currentState || !controls) return;
  const site = currentState.site;
  const cx = site.origin[0] + site.width / 2;
  const cy = site.origin[1] + site.height / 2;
  const maxDim = Math.max(site.width, site.height);

  controls.target.set(cx, cy, 0);

  switch (preset) {
    case "perspective":
      camera.position.set(cx + maxDim * 0.7, cy - maxDim * 0.7, maxDim * 0.5);
      break;
    case "plan":
      camera.position.set(cx, cy, maxDim * 1.3);
      break;
    case "north":
      camera.position.set(cx, cy - maxDim * 1.2, maxDim * 0.3);
      break;
    case "east":
      camera.position.set(cx + maxDim * 1.2, cy, maxDim * 0.3);
      break;
    case "south":
      camera.position.set(cx, cy + maxDim * 1.2, maxDim * 0.3);
      break;
    case "west":
      camera.position.set(cx - maxDim * 1.2, cy, maxDim * 0.3);
      break;
  }
  controls.update();
}

// ── Toggle Element Visibility ─────────────────────────

export function setGroupVisible(name, visible) {
  if (GROUPS[name]) GROUPS[name].visible = visible;
}

export function getGroupNames() {
  return Object.keys(GROUPS);
}

// ── Section Cut Height ────────────────────────────────

export function setSectionHeight(height) {
  if (clippingPlane) clippingPlane.constant = height;
  if (GROUPS.section && GROUPS.section.children[0]) {
    GROUPS.section.children[0].position.z = height;
  }
}

// ── Clipping Toggle ───────────────────────────────────

export function setClippingEnabled(enabled) {
  if (renderer) renderer.localClippingEnabled = enabled;
}

// ── Export ─────────────────────────────────────────────

export function captureImage(width, height) {
  if (!renderer) return null;
  const oldW = renderer.domElement.width, oldH = renderer.domElement.height;
  renderer.setSize(width, height);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.render(scene, camera);
  const dataUrl = renderer.domElement.toDataURL("image/png");
  renderer.setSize(oldW, oldH);
  camera.aspect = oldW / oldH;
  camera.updateProjectionMatrix();
  return dataUrl;
}

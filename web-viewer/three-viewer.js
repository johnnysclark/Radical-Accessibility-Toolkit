/**
 * Three.js 3D Viewer for Plan Layout Jig
 * ========================================
 * Renders the tactile 3D model: extruded walls, floor slab,
 * and section cut visualization. Port of rhino_watcher.py's
 * JIG_TACTILE3D layer + tactile_print.py mesh generation.
 */

import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

// ── Geometry Helpers (mirrored from svg-renderer) ─────

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

// ── Wall Box Geometry ─────────────────────────────────

function createWallBox(segStart, segEnd, fixedVal, axis, halfT, ox, oy, rot, height) {
  if (segEnd - segStart < 0.001) return null;
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

  // Create a BoxGeometry-like shape from the 4 corners extruded up
  const shape = new THREE.Shape();
  shape.moveTo(corners[0][0], corners[0][1]);
  for (let i = 1; i < 4; i++) shape.lineTo(corners[i][0], corners[i][1]);
  shape.closePath();

  const extrudeSettings = { depth: height, bevelEnabled: false };
  return new THREE.ExtrudeGeometry(shape, extrudeSettings);
}

// ── Floor Slab ────────────────────────────────────────

function createFloorSlab(state, thickness) {
  const site = state.site;
  const [sox, soy] = site.origin;
  const sw = site.width, sh = site.height;

  const shape = new THREE.Shape();
  shape.moveTo(sox, soy);
  shape.lineTo(sox + sw, soy);
  shape.lineTo(sox + sw, soy + sh);
  shape.lineTo(sox, soy + sh);
  shape.closePath();

  return new THREE.ExtrudeGeometry(shape, { depth: thickness, bevelEnabled: false });
}

// ── Grid Lines (2D overlay on floor) ──────────────────

function createGridLines(state) {
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
        points.push(new THREE.Vector3(p1[0], p1[1], 0.01));
        points.push(new THREE.Vector3(p2[0], p2[1], 0.01));
      }
      for (const xv of cx) {
        const p1 = localToWorld(xv, cy[0], [ox, oy], rot);
        const p2 = localToWorld(xv, cy[cy.length - 1], [ox, oy], rot);
        points.push(new THREE.Vector3(p1[0], p1[1], 0.01));
        points.push(new THREE.Vector3(p2[0], p2[1], 0.01));
      }
    } else {
      // Radial: rings + arms
      const nr = bay.rings || 4, rs = bay.ring_spacing || 20;
      const na = bay.arms || 8, arc = bay.arc_deg || 360;
      const arcStart = bay.arc_start_deg || 0;
      for (let ring = 1; ring <= nr; ring++) {
        const r = ring * rs;
        const n = 48;
        for (let i = 0; i < n; i++) {
          const a0 = (arcStart + arc * i / n) * Math.PI / 180;
          const a1 = (arcStart + arc * (i + 1) / n) * Math.PI / 180;
          points.push(new THREE.Vector3(ox + r * Math.cos(a0), oy + r * Math.sin(a0), 0.01));
          points.push(new THREE.Vector3(ox + r * Math.cos(a1), oy + r * Math.sin(a1), 0.01));
        }
      }
      const outer = nr * rs;
      for (let arm = 0; arm < na; arm++) {
        const angle = (arcStart + arc * arm / na) * Math.PI / 180;
        points.push(new THREE.Vector3(ox, oy, 0.01));
        points.push(new THREE.Vector3(ox + outer * Math.cos(angle), oy + outer * Math.sin(angle), 0.01));
      }
    }
  }
  const geom = new THREE.BufferGeometry().setFromPoints(points);
  return new THREE.LineSegments(geom, new THREE.LineBasicMaterial({ color: 0x444444 }));
}

// ── Section Cut Plane ─────────────────────────────────

function createSectionPlane(state, cutHeight) {
  const site = state.site;
  const [sox, soy] = site.origin;
  const sw = site.width, sh = site.height;
  const pad = 10;
  const planeGeom = new THREE.PlaneGeometry(sw + pad * 2, sh + pad * 2);
  const planeMat = new THREE.MeshBasicMaterial({
    color: 0xff4444, transparent: true, opacity: 0.1,
    side: THREE.DoubleSide, depthWrite: false,
  });
  const plane = new THREE.Mesh(planeGeom, planeMat);
  plane.position.set(sox + sw / 2, soy + sh / 2, cutHeight);
  plane.name = "sectionPlane";
  return plane;
}

// ── Master Build ──────────────────────────────────────

let scene, camera, renderer, controls;
let currentMeshes = [];

export function initThreeViewer(container) {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf0f0f0);

  // Camera
  const aspect = container.clientWidth / container.clientHeight;
  camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 10000);
  camera.position.set(100, -150, 200);
  camera.up.set(0, 0, 1);

  // Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  container.appendChild(renderer.domElement);

  // Controls
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.1;
  controls.target.set(90, 130, 0);

  // Lighting
  const ambient = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambient);
  const directional = new THREE.DirectionalLight(0xffffff, 0.8);
  directional.position.set(100, -100, 200);
  scene.add(directional);
  const fill = new THREE.DirectionalLight(0xffffff, 0.3);
  fill.position.set(-100, 100, 100);
  scene.add(fill);

  // Axes helper
  const axes = new THREE.AxesHelper(20);
  scene.add(axes);

  // Resize handler
  const ro = new ResizeObserver(() => {
    const w = container.clientWidth, h = container.clientHeight;
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

export function buildScene(state) {
  if (!scene) return;

  // Remove old meshes
  for (const m of currentMeshes) scene.remove(m);
  currentMeshes = [];

  const t3 = state.tactile3d || {};
  const wallHeight = t3.wall_height || 9;
  const cutHeight = t3.cut_height || 4;
  const floorThick = t3.floor_thickness || 0.5;
  const floorOn = t3.floor_enabled !== false;
  const extrudeH = Math.min(wallHeight, cutHeight);

  const wallMat = new THREE.MeshStandardMaterial({
    color: 0xb44444, roughness: 0.7, metalness: 0.1,
  });
  const floorMat = new THREE.MeshStandardMaterial({
    color: 0xcccccc, roughness: 0.9, metalness: 0.0,
  });

  // Extrude wall segments
  for (const [, bay] of Object.entries(state.bays)) {
    if ((bay.grid_type || "rectangular") !== "rectangular") continue;
    const w = bay.walls || {};
    if (!w.enabled) continue;
    const t = w.thickness || 0.5, halfT = t / 2;
    const [ox, oy] = bay.origin;
    const rot = bay.rotation_deg;
    const [cx, cy] = getSpacingArrays(bay);
    const aps = bay.apertures || [];

    // Horizontal walls
    for (let j = 0; j < cy.length; j++) {
      const yVal = cy[j];
      const wallAps = aps
        .filter(a => a.axis === "x" && a.gridline === j)
        .sort((a, b) => (a.corner || 0) - (b.corner || 0));
      for (const [s, e] of calcWallSegments(cx[cx.length - 1], wallAps)) {
        const geom = createWallBox(s, e, yVal, "x", halfT, ox, oy, rot, extrudeH);
        if (geom) {
          const mesh = new THREE.Mesh(geom, wallMat);
          scene.add(mesh);
          currentMeshes.push(mesh);
        }
      }
    }

    // Vertical walls
    for (let i = 0; i < cx.length; i++) {
      const xVal = cx[i];
      const wallAps = aps
        .filter(a => a.axis === "y" && a.gridline === i)
        .sort((a, b) => (a.corner || 0) - (b.corner || 0));
      for (const [s, e] of calcWallSegments(cy[cy.length - 1], wallAps)) {
        const geom = createWallBox(s, e, xVal, "y", halfT, ox, oy, rot, extrudeH);
        if (geom) {
          const mesh = new THREE.Mesh(geom, wallMat);
          scene.add(mesh);
          currentMeshes.push(mesh);
        }
      }
    }
  }

  // Floor slab
  if (floorOn) {
    const floorGeom = createFloorSlab(state, floorThick);
    const floor = new THREE.Mesh(floorGeom, floorMat);
    floor.position.z = -floorThick;
    scene.add(floor);
    currentMeshes.push(floor);
  }

  // Grid lines on floor
  const gridLines = createGridLines(state);
  scene.add(gridLines);
  currentMeshes.push(gridLines);

  // Section cut plane indicator
  const sectionPlane = createSectionPlane(state, cutHeight);
  scene.add(sectionPlane);
  currentMeshes.push(sectionPlane);

  // Point camera at center of site
  const site = state.site;
  const cx = site.origin[0] + site.width / 2;
  const cy = site.origin[1] + site.height / 2;
  controls.target.set(cx, cy, 0);
  camera.position.set(cx + site.width * 0.8, cy - site.height * 0.8, site.height * 0.6);
  controls.update();
}

export function getRenderer() { return renderer; }

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

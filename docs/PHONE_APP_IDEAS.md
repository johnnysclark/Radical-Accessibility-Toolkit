# Phone App Ideas for the Radical Accessibility Toolkit

## Context

The Radical Accessibility Toolkit is an accessibility-first architectural design system built for blind and low-vision architecture students. Its core loop is: author designs via text commands, store state in JSON, render in Rhino, export to PIAF tactile prints or 3D-printed models, evaluate by touch, and iterate. Everything passes through text. The phone is the one powerful computer that's always in your pocket, always has a camera, always has haptics, always has a mic and speaker, and always has built-in accessibility (VoiceOver/TalkBack). Here are ideas for apps that extend the toolkit into that device.

---

## 1. Haptic Floor Plan Explorer

**What it does:** Load a state.json floor plan onto the phone screen. As you drag your finger across the surface, the phone vibrates differently depending on what you're touching: strong buzz for walls, rhythmic pulse for doors, light hum for corridors, nothing for open rooms, texture pattern for hatched zones. It's like reading a PIAF print, but the "print" is always in your pocket and dynamically updates as the design changes.

**Why it's cool:**
- PIAF prints require a printer and heat machine. This gives instant tactile feedback from any design state, anywhere.
- Modern phone haptic engines (Apple Taptic Engine, Android HD haptics) can produce surprisingly distinct patterns -- enough to differentiate 6-8 surface types.
- The phone knows the finger position, so it can simultaneously announce via VoiceOver: "Classroom 1, diagonal hatch, 576 square feet" as you enter a room.
- Pinch to zoom works naturally. Two-finger drag to pan. Shake to hear a full description.
- Could overlay a structural grid as a subtle "click" pattern at gridline crossings.

**Technical hook:** Reads state.json directly (or fetches from MCP server over network). Uses the same spatial math as the state renderer in `tools/tact/src/tact/core/state_renderer.py` to map finger coordinates to architectural elements.

---

## 2. Voice Design Studio

**What it does:** A mobile voice-first design companion. You talk to it like you talk to Claude Code, but it's optimized for phone: big simple UI, works with AirPods, operates hands-free. "Add a bay, 6 by 3, 24-foot spacing." "Rotate bay A by 15 degrees." "What's the corridor width?" It sends commands to the MCP server (via network) and reads back confirmations.

**Why it's cool:**
- Design brainstorming on a walk. Architecture students often have their best ideas away from the desk -- on the bus, in the shower, walking through a building. This lets you sketch with words from anywhere.
- The existing CLI commands are already designed to be spoken (short, speakable, no special characters). The infrastructure is there.
- Could maintain a local "scratchpad" state.json that syncs to the main workstation later, or connect live.
- Natural fit with the project's philosophy: text is the universal interface, and voice is just text with a microphone.

**Technical hook:** Wraps the same command parser from `controller/controller_cli.py`. Could run a lightweight MCP client on the phone, or SSH tunnel to the desktop session. Claude Code's existing `remote-control` feature could be the backbone.

---

## 3. Tactile Camera (Scan-to-Touch Pipeline)

**What it does:** Point the phone camera at any architectural drawing -- a floor plan on a wall, a sketch on a napkin, a page in a textbook -- and the app captures it, runs it through the TACT pipeline, and either (a) sends a PIAF-ready PDF to a networked printer, (b) loads it into the Haptic Explorer (idea 1), or (c) queues it for when you're back at the PIAF machine. Includes the multi-level image description from the Image Describer tool so you get an instant spoken description while the tactile conversion processes.

**Why it's cool:**
- Right now, getting a precedent image into the tactile pipeline requires: find the image file, transfer to the workstation, run `tact convert`. This collapses it to: point phone, tap, done.
- During studio pin-ups and critiques, a blind student could point at classmates' drawings on the wall and get instant descriptions + queued tactile prints.
- The TACT pipeline already has presets (floor_plan, photograph, sketch, section, elevation) -- the app could auto-detect which preset to use via Claude vision, or let you pick.
- Build a personal library of scanned precedents, each with description + tactile version, searchable by voice.

**Technical hook:** Camera capture + Claude API for image description (same as `tools/image-describer/arch_alt_text.py`). TACT conversion via MCP function `image_to_piaf`. Preset auto-selection via `analyze_image`.

---

## 4. Spatial Audio Walkthrough

**What it does:** Put in earbuds/AirPods. The app loads a state.json design and generates a binaural spatial audio environment. You "walk" through the building using the phone's gyroscope and simple gestures (swipe forward to step, turn phone to turn). Walls reflect sound (reverb changes near walls vs. open corridors). Doors click as you pass through them. Room names are whispered from their center points. Columns tick like clocks. The corridor has a different acoustic signature than a classroom.

**Why it's cool:**
- This is the missing sensory channel. PIAF prints give touch. The CLI gives text. This gives spatial hearing -- and architects think spatially.
- Head-tracking with AirPods Pro means turning your head actually changes what you hear. Walk toward a wall, the reverb tightens. Step into a large room, it opens up.
- Could sonify design changes in real-time: make a change in the CLI, hear the space transform in your ears.
- Precedent: there's real research on auditory architecture and spatial audio for accessibility. This would be a concrete implementation.
- The state.json already contains everything needed: room boundaries, wall positions, door locations, corridor paths. No additional data needed.

**Technical hook:** Uses bay geometry from state.json to build a simple acoustic model. Room dimensions drive reverb parameters. Wall positions drive reflection timing. iOS Core Haptics + AVAudioEngine spatial audio APIs, or Web Audio API for cross-platform.

---

## 5. Site Visit Companion

**What it does:** When visiting a real building (for precedent study, site analysis, or field trip), the app uses GPS + compass + LiDAR (iPhone Pro) to understand where you are and what's around you. Point the phone at a building facade and hear: "Three-story brick building, approximately 45 feet wide. Six windows per floor, evenly spaced. Main entrance centered, double doors with transom." Walk along a corridor and the app tracks your path, building a spatial map you can later import as a starting point for a new design.

**Why it's cool:**
- Architecture education heavily involves site visits and precedent study. For a blind student, these are often passive -- someone describes what they see. This makes them active and independent.
- LiDAR scanning + Claude vision is a powerful combination: LiDAR gives accurate dimensions, vision gives semantic understanding.
- The walked path could auto-generate a rough state.json with zones, corridors, and approximate room sizes -- a "field sketch" made by walking.
- Could anchor descriptions to compass directions, matching the project's semantic approach: "The library wing extends north from the main corridor" rather than "the big part is on the left."

**Technical hook:** ARKit/ARCore for spatial tracking. Claude API for image description (reuses Image Describer patterns). GPS for macro-positioning. Export to state.json format for import into the Layout Jig controller.

---

## 6. Pegboard Scanner 2.0

**What it does:** Enhanced version of the existing prototype pegboard input system. Instead of a fixed overhead camera + OpenCV on a desktop, use the phone camera with on-device ML. Hold the phone over the pegboard (or mount it on a simple stand). The app recognizes wire positions in real-time, provides audio feedback as wires are placed ("Wall detected, 24 feet, running east-west"), and converts the physical layout to state.json commands. Colored wire = different element types (red = walls, blue = corridors, green = zones).

**Why it's cool:**
- The pegboard is one of the project's most innovative ideas -- physical-first design input. But the current prototype needs a desktop + webcam + OpenCV setup. Moving it to a phone makes it portable and self-contained.
- Real-time audio feedback transforms the pegboard from "build then scan" to "build and hear" -- each wire placed gets immediate confirmation.
- On-device ML (Core ML / TensorFlow Lite) can run wire detection without network latency.
- Multiple students could each have their own pegboard + phone setup in a studio, no shared equipment needed.

**Technical hook:** On-device vision model for wire detection. Color classification for element types. Export as CLI commands or direct state.json mutations. Connects to the same controller command set.

---

## 7. Tactile QR Bridge

**What it does:** Embed machine-readable codes (QR or DataMatrix) into PIAF tactile prints -- they survive the heating process as raised patterns. When a blind user encounters an unfamiliar print, they scan it with their phone. The app looks up the design, reads the full description aloud, offers the Haptic Explorer view, shows the design history, or connects to the live state for real-time collaboration.

**Why it's cool:**
- Tactile prints are currently "offline" artifacts. Once printed, there's no link back to the digital design. This bridges that gap.
- A student could pick up any print in the studio -- their own from last week, a classmate's, an instructor's example -- and instantly get context.
- The QR code could encode a snapshot ID, so you get the exact state the print represents, not just the current (possibly changed) design.
- Could enable a "tactile print library" where prints are filed physically but indexed digitally.
- Instructors could create annotated prints where scanning reveals layer-by-layer explanations.

**Technical hook:** QR generation added to the PDF output stage in `tools/tact/src/tact/core/pdf_generator.py`. App decodes QR, fetches snapshot from `controller/snapshots/` or a cloud store. Links to MCP functions for description.

---

## 8. Collaborative Design Table

**What it does:** Multiple phones on a shared surface, each representing a design zone or building wing. An overhead "anchor" phone or tablet sees all devices via camera and maps their physical positions to zone positions in state.json. Slide your phone north on the table, your zone moves north in the design. Rotate it, the wing rotates. Stack two phones, the zones merge. Pull them apart, they separate.

**Why it's cool:**
- Tangible interaction for spatial design -- move physical objects to manipulate digital space.
- Makes collaborative design sessions accessible: each person controls their zone, and the spatial arrangement is something everyone can perceive (by touching where phones are on the table).
- Could work in a design studio crit: "Move the library wing further from the gym" becomes literally sliding a phone across the table.
- Audio feedback from each phone describes its zone and relationships to neighbors.

**Technical hook:** UWB (Ultra-Wideband) on newer iPhones for precise relative positioning, or camera-based tracking from a tablet overhead. Zone commands from `controller/controller_cli.py` (zone add, zone modify, zone describe). State sync via MCP.

---

## 9. Material and Texture Identifier

**What it does:** Point the phone camera at a building material, surface, or texture sample. The app identifies it ("red brick, running bond pattern, approximately 3-5/8 inch modular") and maps it to the project's hatch pattern vocabulary (diagonal, crosshatch, dots, horizontal, vertical). You can then assign that material to a room in your design: "Use this for Classroom 1." The material gets stored with its real-world photo, description, and hatch mapping.

**Why it's cool:**
- Connects real materials to the abstract hatch patterns used in tactile prints.
- During a site visit, touch a wall surface, scan it, and later feel the same hatch pattern on your tactile print -- closing the sensory loop.
- Builds a personal materials library organized by touch/description rather than visual appearance.
- The hatch patterns in PIAF prints are already designed to be distinguishable by touch. This makes them meaningful by linking them to real textures.

**Technical hook:** Claude vision for material identification. Maps to the existing hatch vocabulary in `controller/controller_cli.py` (cell hatch types: diagonal, crosshatch, dots, horizontal, vertical, etc.). Stores mappings in a materials JSON alongside state.json.

---

## 10. Accessibility Audit AR

**What it does:** Point the phone at a real space (hallway, doorway, ramp, bathroom). The app uses LiDAR + camera to measure key dimensions and checks them against ADA standards -- the same checks the existing `auditor.py` runs on digital designs, but applied to physical spaces. "This doorway is 30 inches wide. ADA requires 32 inches minimum. FAIL." Could also compare a built space against the original design in state.json to verify construction accuracy.

**Why it's cool:**
- The project already has a digital ADA auditor. This is its physical-world counterpart.
- A blind student could independently verify accessibility of real spaces -- empowering in a field that's literally about making spaces work for everyone.
- The as-built vs. as-designed comparison closes yet another loop in the physical-digital round-trip.
- Measurements are spoken, not displayed -- fully accessible by design.

**Technical hook:** ARKit LiDAR for dimension capture. Same ADA rules as `controller/auditor.py` (door widths, corridor widths, turning radiuses). Comparison against state.json bay/aperture/corridor data.

---

## Ranking by Impact and Feasibility

| Rank | App | Impact | Feasibility | Notes |
|------|-----|--------|-------------|-------|
| 1 | Haptic Floor Plan Explorer | Very High | High | Core phone APIs, direct state.json reuse |
| 2 | Tactile Camera | Very High | High | Leverages existing TACT pipeline |
| 3 | Voice Design Studio | High | High | Wraps existing CLI, voice is native |
| 4 | Spatial Audio Walkthrough | Very High | Medium | Novel UX, needs audio design work |
| 5 | Tactile QR Bridge | Medium | Very High | Simple to implement, high utility |
| 6 | Site Visit Companion | High | Medium | LiDAR + vision, field-dependent |
| 7 | Accessibility Audit AR | High | Medium | LiDAR measurement accuracy varies |
| 8 | Pegboard Scanner 2.0 | High | Medium | Needs custom ML model training |
| 9 | Material Identifier | Medium | High | Claude vision does the heavy lifting |
| 10 | Collaborative Design Table | High | Low | UWB/positioning is tricky |

---

## Recommended First Build: RAT Mobile (Ideas 1 + 2 + 3 combined)

A single app with three tabs:

1. **Explore** (Haptic Explorer) -- Load any state.json, explore by touch + haptics + voice
2. **Design** (Voice Studio) -- Speak commands, hear confirmations, iterate on the go
3. **Capture** (Tactile Camera) -- Scan drawings/buildings, get descriptions, queue PIAF prints

This gives the toolkit a complete mobile presence: input (capture + voice), processing (commands + conversion), and output (haptic exploration + audio description). Built on the same state.json and MCP infrastructure that already exists.

**Tech stack suggestion:** Swift/SwiftUI (iOS first, since VoiceOver is best-in-class for accessibility and Taptic Engine has the richest haptic API). React Native as cross-platform alternative if Android parity needed early.

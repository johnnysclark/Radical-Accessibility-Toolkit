# Architectural Tactile Graphics Guidelines

VERSION: 1.0
LAST_UPDATED: 2025-12-26
STATUS: Living Document - Refinement Through Testing

---

## 1. Overview

### Purpose

This document provides guidelines for converting architectural images into tactile graphics suitable for PIAF (Picture In A Flash) production. It serves two audiences:

1. **Human readers**: Architecture students, educators, and accessibility specialists who need to understand tactile graphic principles
2. **LLM agents**: AI systems that analyze architectural images and invoke the Image-to-PIAF tool with appropriate parameters

### Scope

Covers all visual materials encountered in architecture education:
- Studio work (plans, sections, elevations, sketches, models)
- Structures courses (load diagrams, stress fields, connection details)
- History/theory (photographs, drawings, site plans, maps)
- Technical systems (environmental diagrams, fabrication drawings)
- Data visualization (charts, graphs, simulations)

### User Context

PRIMARY_USER: Blind/low-vision architecture student
ACADEMIC_LEVEL: Sophomore
CURRENT_COURSES: Structures, Design Studio
BRAILLE_PROFICIENCY: Grade 2 (contracted) - fluent
GOAL: Self-sufficiency in creating and interpreting tactile graphics

---

## 2. Pattern Integration

### System Architecture

```
WORKFLOW:
  Image → Image-Description-Machine → LLM Analysis → Image-to-PIAF → Tactile PDF
```

### Component Roles

**Image-Description-Machine** (patterns/image_description_machine/)
- Generates Macro/Meso/Micro descriptions of architectural images
- Identifies medium type, materials, spatial relationships
- Extracts text present in image
- Provides context for tactile conversion decisions

**This Document** (ARCHITECTURAL_TACTILE_GUIDELINES.md)
- Decision framework for LLM agents
- Parameter selection logic for Image-to-PIAF
- Category-specific conversion rules
- Quality criteria for tactile output

**Image-to-PIAF** (tactile CLI tool)
- Converts images to high-contrast black/white
- Applies text detection and Braille conversion
- Handles tiling for oversized images
- Generates print-ready PDF for PIAF machine

### LLM Decision Flow

```
1. Receive architectural image
2. Apply Image-Description-Machine pattern
3. From description, determine:
   - Graphic category (see Section 4)
   - Complexity level (simple/moderate/complex)
   - Text density (none/sparse/moderate/dense)
   - Required simplification (if any)
4. Select Image-to-PIAF parameters using this document
5. Invoke tool with appropriate options
6. Validate output against principles (Section 3)
```

---

## 3. General Principles

### ABSOLUTE RULE: No Overlapping Information

```
CRITICAL: Tactile elements that overlap become unreadable when PIAFed.
         This applies to:
         - Braille labels over original text
         - Line work crossing at multiple points
         - Dense hatching or stipple patterns
         - Symbol keys placed over drawing content
```

ENFORCEMENT:
- The Image-to-PIAF tool automatically repositions overlapping Braille labels
- Labels that cannot be repositioned are omitted with a log message
- Original text regions are whited out before Braille placement
- Simplification must be applied to overly dense drawings

### Preserve Original Scale

RULE: Maintain the scale of the original drawing unless:
- Paper size constraints require tiling
- User explicitly requests a different scale
- Critical detail would be lost at original size

RATIONALE: Architecture students must develop accurate scale intuition. Changing scale without notification undermines spatial reasoning.

### Braille Standards

PREFERRED_GRADE: 2 (contracted)
RATIONALE: User is fluent in Grade 2; contracted Braille is more compact, reducing overlap potential

BRAILLE_PARAMETERS:
- Grade 2 for all text conversion
- Minimum 3mm between adjacent labels
- Labels positioned below original text location when possible
- Maximum label length: 40 characters (longer text summarized or split)

### Color to Pattern/Texture Conversion

Colors cannot be represented tactilely. Convert using:

| Color Purpose | Tactile Representation |
|---------------|------------------------|
| Differentiation | Distinct line patterns (solid, dashed, dotted) |
| Hierarchy | Line weight variation |
| Emphasis | Texture density variation |
| Zone indication | Boundary lines with texture fill |

THEORETICAL_BASIS: Way & Barner (1997) proposed automated color-to-texture mapping using K-means segmentation to divide images into color regions, then applying the four-color theorem (any planar map can be colored with four colors, no two adjacent regions sharing a color) to assign distinct tactile textures. With as few as four textures, any architectural plan's color-coded zones could be made tactilely distinguishable. This approach — mapping color regions to tactile texture fills — is a high-priority enhancement for the pipeline.

CURRENT_LIMITATION: Automatic color-to-texture mapping not yet implemented. LLM should describe color-coded information in accompanying text description. Future implementation should use K-means segmentation + texture assignment per Way & Barner's method.

### Simplification Transparency

RULE: When simplification is applied, explain:
1. What was simplified
2. Why simplification was necessary
3. What information may have been lost
4. How to access the original if needed

FORMAT:
```
SIMPLIFICATION_APPLIED:
  - [Element]: [Original] -> [Simplified]
  - REASON: [Tactile clarity / Density reduction / Overlap prevention]
  - INFORMATION_LOSS: [Description of what is no longer distinguishable]
```

---

## 4. Graphic Categories

### CATEGORY: Floor Plans

IDENTIFIER: Horizontal section through building showing walls, doors, windows, rooms
TYPICAL_SOURCE: CAD exports, hand drawings, textbook figures
PRESET: floor_plan
THRESHOLD: 140-150
ENHANCEMENT: s_curve (strength 1.0)
PAPER_SIZE: letter (small plans) or tabloid (complex plans)
KEY_FEATURES:
- Wall thickness critical for tactile recognition
- Door swings must be clear
- Room labels essential
- Furniture usually simplified or omitted

### CATEGORY: Sections

IDENTIFIER: Vertical cut through building showing floor levels, ceiling heights, structure
TYPICAL_SOURCE: CAD drawings, construction documents
PRESET: section
THRESHOLD: 145
ENHANCEMENT: s_curve (strength 1.2)
PAPER_SIZE: letter or tabloid based on building height
KEY_FEATURES:
- Cut material (poche) must have distinct texture
- Level lines need clear spacing
- Dimension strings important for structures coursework

### CATEGORY: Elevations

IDENTIFIER: Orthographic view of building exterior, no perspective distortion
TYPICAL_SOURCE: CAD drawings, measured drawings
PRESET: elevation
THRESHOLD: 135
ENHANCEMENT: s_curve (strength 1.0)
PAPER_SIZE: letter
KEY_FEATURES:
- Window patterns show rhythm
- Material indication simplified
- Ground line must be clear

### CATEGORY: Structural Diagrams

IDENTIFIER: Load paths, force diagrams, moment diagrams, connection details
TYPICAL_SOURCE: Structures course materials, engineering documents
PRESET: technical_drawing
THRESHOLD: 150
ENHANCEMENT: none (line work should be clean)
PAPER_SIZE: letter
KEY_FEATURES:
- Arrow direction critical (loads, reactions)
- Line weight indicates force magnitude
- Support symbols (pin, roller, fixed) must be distinct
- Dimension annotations essential

SPECIAL_CONSIDERATION: Force diagrams often use color to show tension vs compression. LLM must describe this in text since tactile cannot differentiate.

### CATEGORY: Site Plans

IDENTIFIER: Building footprint in context of site, landscape, adjacent structures
TYPICAL_SOURCE: Planning documents, design presentations
PRESET: site_plan
THRESHOLD: 140
ENHANCEMENT: s_curve (strength 1.0)
PAPER_SIZE: tabloid (usually larger coverage area)
KEY_FEATURES:
- North arrow essential
- Property boundaries clear
- Building footprint solid or heavy outline
- Landscape often simplified to boundaries only

### CATEGORY: Detail Drawings

IDENTIFIER: Enlarged construction details showing assemblies, connections, materials
TYPICAL_SOURCE: Construction documents, technical references
PRESET: detail_drawing
THRESHOLD: 145
ENHANCEMENT: s_curve (strength 1.1)
PAPER_SIZE: letter
KEY_FEATURES:
- Layer separation in assemblies
- Fastener locations
- Material breaks and joints
- Dimension strings critical

### CATEGORY: Sketches and Diagrams

IDENTIFIER: Freehand conceptual drawings, bubble diagrams, parti sketches
TYPICAL_SOURCE: Studio work, lecture notes, design development
PRESET: sketch
THRESHOLD: 130
ENHANCEMENT: s_curve (strength 1.3)
PAPER_SIZE: letter
KEY_FEATURES:
- Line quality variable (enhance contrast)
- Hierarchy may be unclear (describe in text)
- Quick notations may be illegible (note in output)

### CATEGORY: Photographs

IDENTIFIER: Photos of buildings, spaces, construction, models
TYPICAL_SOURCE: Case studies, site visits, precedent research
PRESET: photograph
THRESHOLD: 120
ENHANCEMENT: clahe
PAPER_SIZE: letter
KEY_FEATURES:
- Heavy simplification usually required
- Focus on major masses and edges
- Depth cues lost (describe in text)
- Consider if tactile version is appropriate vs detailed text description

SPECIAL_CONSIDERATION: Photographs often convert poorly to tactile. LLM should assess whether Image-Description-Machine output alone may be more useful than tactile conversion.

### CATEGORY: Axonometric/Isometric Views

IDENTIFIER: 3D parallel projection showing three dimensions without perspective
TYPICAL_SOURCE: Design presentations, textbook illustrations
PRESET: diagram
THRESHOLD: 135
ENHANCEMENT: auto_contrast
PAPER_SIZE: letter or tabloid
KEY_FEATURES:
- Maintain line weight hierarchy (edges vs surface lines)
- Hidden lines may confuse (consider removal)
- Exploded views need clear separation between parts

### CATEGORY: Presentation Boards

IDENTIFIER: Multi-image compositions with text, typically design review format
TYPICAL_SOURCE: Studio reviews, competition entries
PRESET: presentation
THRESHOLD: 125
ENHANCEMENT: clahe
PAPER_SIZE: tabloid
TILING: often required
KEY_FEATURES:
- May need to tile and convert sections separately
- Image hierarchy determines processing order
- Consider extracting individual graphics for separate conversion

---

## 5. Tool Invocation

### CLI Command Syntax

```bash
tact INPUT_PATH [OPTIONS]
```

### Core Options

```
--output, -o PATH          Output PDF path (default: INPUT_piaf.pdf)
--threshold INTEGER        Black/white threshold 0-255 (default: 128)
--paper-size {letter|tabloid}  Output paper size (default: letter)
--verbose, -v              Detailed processing output
```

### Text and Braille Options

```
--detect-text              Enable OCR text detection
--braille-grade {1|2}      Braille grade (default: 2 for Grade 2)
```

### Enhancement Options

```
--enhance {s_curve|auto_contrast|clahe|histogram}
                           Apply contrast enhancement
--enhance-strength FLOAT   Enhancement strength 0.0-2.0 (default: 1.0)
```

### Tiling Options

```
--enable-tiling            Split large images into multiple pages
```

### Preset Option

```
--preset PRESET_NAME       Use predefined settings
```

AVAILABLE_PRESETS: floor_plan, sketch, photograph, elevation, section, diagram, site_plan, detail_drawing, technical_drawing, presentation

### Example Invocations

```bash
# Floor plan with text detection and Grade 2 Braille
tact floor-plan.jpg --preset floor_plan --detect-text --braille-grade 2 --verbose

# Structural diagram (clean lines, no enhancement)
tact beam-diagram.png --preset technical_drawing --detect-text --braille-grade 2

# Large site plan requiring tiling
tact site-plan.pdf --preset site_plan --enable-tiling --detect-text --braille-grade 2

# Photograph with heavy contrast enhancement
tact building-photo.jpg --preset photograph --detect-text --braille-grade 2 --verbose

# Custom settings (override preset)
tact sketch.jpg --preset sketch --threshold 120 --enhance-strength 1.5
```

### LLM Invocation Pattern

When an LLM determines parameters, construct the command as:

```
COMMAND_TEMPLATE:
  tact "{input_path}" \
    --preset {category_preset} \
    --detect-text \
    --braille-grade 2 \
    {additional_options} \
    --verbose
```

ALWAYS_INCLUDE:
- --detect-text (for label conversion)
- --braille-grade 2 (user preference)
- --verbose (for validation)

---

## 6. Decision Framework

### When to Simplify

TRIGGER: Image density exceeds 40% black after processing

ACTIONS:
1. Increase threshold (fewer pixels become black)
2. Apply morphological erosion
3. Use --auto-reduce-density --target-density 0.30

TRIGGER: More than 15 text labels detected

ACTIONS:
1. Prioritize labels by architectural significance
2. Consider symbol key with numbered references
3. Abbreviate where possible (KITCHEN -> KIT, BATHROOM -> BATH)

TRIGGER: Complex pattern/hatching fills large areas

ACTIONS:
1. Replace pattern with boundary outline only
2. Add text label identifying material
3. Describe pattern in accompanying text description

### When to Tile

TRIGGER: Original image dimensions exceed paper size at 1:1 scale

CALCULATION:
```
Letter paper: 8.5" x 11" at 300 DPI = 2550 x 3300 pixels
Tabloid paper: 11" x 17" at 300 DPI = 3300 x 5100 pixels

IF image_width > paper_width OR image_height > paper_height:
  ENABLE_TILING = true
```

TILING_OPTIONS:
1. Use --enable-tiling for automatic splitting with registration marks
2. Consider --paper-size tabloid first to avoid tiling
3. For very large drawings (>4 tiles), consider selective conversion of key areas

### When to Use Symbol Keys

TRIGGER: Many similar elements need labeling (rooms, spaces, structural members)

IMPLEMENTATION:
1. Create numbered reference system
2. Place symbol key in margin area
3. Use single-character or number labels on drawing
4. Full text in key only

EXAMPLE:
```
Drawing: Shows "1", "2", "3" at room locations
Key (in margin):
1 = Kitchen
2 = Living Room
3 = Bedroom
```

CURRENT_STATUS: Symbol key generation is manual; LLM should recommend approach in output description

### When NOT to Convert to Tactile

CONSIDER_TEXT_ONLY_DESCRIPTION:
- Photographs with complex depth (stairs in perspective, complex rooflines)
- Images where color is primary information carrier
- Very low resolution source images
- Images with text as primary content (better to transcribe)
- Decorative images without spatial information

RECOMMENDATION_FORMAT:
```
TACTILE_CONVERSION_NOT_RECOMMENDED
REASON: [Specific reason]
ALTERNATIVE: Detailed text description via Image-Description-Machine
DESCRIPTION_FOLLOWS: [Yes/No]
```

---

## 7. Testing Notes

### Purpose

This section records findings from student testing sessions. Each entry documents what worked, what failed, and resulting guideline updates.

### Testing Protocol

1. Convert image using current guidelines
2. Print on PIAF machine
3. Student explores tactile graphic
4. Record: comprehension time, confusion points, suggestions
5. Update guidelines based on findings

### Test Log

```
DATE: [YYYY-MM-DD]
IMAGE_TYPE: [Category from Section 4]
SOURCE_FILE: [Filename]
PARAMETERS_USED: [CLI command]
OUTCOME: [Success / Partial / Failed]
FINDINGS:
  - [What worked]
  - [What was confusing]
  - [Student suggestions]
GUIDELINE_UPDATES:
  - [Changes made to this document]
---
```

### Pending Tests

- [ ] Floor plan with furniture vs without
- [ ] Structural force diagram with color-coded tension/compression
- [ ] Multi-level section with dimension strings
- [ ] Site plan with topographic contours
- [ ] Exploded axonometric assembly diagram
- [ ] Photograph of building vs text description comparison

### Known Issues

```
ISSUE_ID: 001
DESCRIPTION: Dense hatching patterns create unusable tactile texture
STATUS: Workaround - simplify to outline only
PROPOSED_FIX: Pattern detection and replacement (Phase 4)
---
ISSUE_ID: 002
DESCRIPTION: Small text (<10pt) OCR unreliable
STATUS: Known limitation
PROPOSED_FIX: Manual label entry option
---
ISSUE_ID: 003
DESCRIPTION: Grayscale gradients lost in threshold conversion
STATUS: By design (PIAF requires black/white)
PROPOSED_FIX: Describe gradients in text; consider contour lines for topography
---
```

---

## Appendix A: Quick Reference Card

```
STANDARD_COMMAND:
tact INPUT --preset PRESET --detect-text --braille-grade 2 --verbose

PRESET SELECTION:
  Plans/Sections -> floor_plan, section
  Diagrams -> technical_drawing, diagram
  Sketches -> sketch
  Photos -> photograph (consider text-only alternative)
  Large drawings -> site_plan, presentation (with --enable-tiling)

DENSITY ISSUES:
  Too dark -> increase threshold (try 150, 160, 170)
  Too light -> decrease threshold (try 110, 100, 90)

OVERLAP ISSUES:
  Handled automatically by tool
  If persistent, reduce text density or use symbol key

BRAILLE:
  Always Grade 2 for this user
  Labels auto-repositioned if overlapping
  Original text whited out before Braille placement
```

---

## Appendix B: Glossary

**PIAF**: Picture In A Flash - thermal swell paper machine that raises black areas
**Tactile graphic**: Raised-line drawing readable by touch
**Swell paper**: Microcapsule paper that expands when heated (black areas rise)
**Density**: Percentage of black pixels; >40% causes over-swelling
**Tiling**: Splitting large image across multiple sheets with alignment marks
**Poche**: Solid fill indicating cut material in architectural sections
**Grade 2 Braille**: Contracted Braille using abbreviations and contractions
**Threshold**: Gray level (0-255) above which pixels become white

---

## Document Maintenance

OWNER: Fabric Accessible Graphics Project
REVIEW_CYCLE: After each testing session
VERSIONING: Semantic (MAJOR.MINOR for guideline changes)

CHANGE_LOG:
```
1.0 (2025-12-26): Initial document creation
  - Established 9 graphic categories
  - Defined core principles
  - Documented CLI syntax
  - Created decision framework
  - Added testing log structure
```

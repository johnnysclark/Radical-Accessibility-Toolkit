#!/usr/bin/env bun
/**
 * ImageDetector.ts - Proactive Architectural Image Detection
 *
 * PURPOSE:
 * Detects when architectural images are present in conversation and
 * proactively offers tactile conversion options. Logs detections to
 * memory for learning and improvement over time.
 *
 * TRIGGER: UserPromptSubmit (when user sends a message with potential images)
 *
 * INPUT:
 * - stdin: Hook input JSON containing message content and attachments
 *
 * OUTPUT:
 * - stdout: JSON with detection results and suggested actions
 * - stderr: Status messages for logging
 * - exit(0): Success
 * - exit(1): Error
 *
 * DETECTION CATEGORIES:
 * - floor_plan: Architectural floor plans
 * - section: Building cross-sections
 * - elevation: Building elevations
 * - site_plan: Site and landscape plans
 * - diagram: Technical diagrams
 * - sketch: Hand-drawn sketches
 * - detail: Construction details
 * - unknown: Unrecognized architectural content
 * - non_architectural: Not an architectural image
 *
 * SIDE EFFECTS:
 * - Writes: .radical-accessibility/memory/detections.jsonl
 * - Reads: User prompt and attachments
 *
 * CONFIGURATION:
 * Set environment variable RADICAL_ACCESSIBILITY_MEMORY_DIR to customize
 * the memory storage location (defaults to ~/.radical-accessibility/memory)
 */

import { writeFileSync, appendFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';

// Types
interface HookInput {
  session_id?: string;
  message?: string;
  attachments?: Attachment[];
  images?: string[]; // Base64 or file paths
}

interface Attachment {
  type: string;
  path?: string;
  url?: string;
  mimeType?: string;
}

interface DetectionResult {
  detected: boolean;
  category: string;
  confidence: 'high' | 'medium' | 'low';
  suggestedAction: string;
  suggestedPreset?: string;
  reasoning: string;
}

interface DetectionLog {
  timestamp: string;
  session_id: string;
  category: string;
  confidence: string;
  user_accepted: boolean | null; // null = pending
  preset_used?: string;
  source_path?: string;
}

// Constants
const MEMORY_DIR = process.env.RADICAL_ACCESSIBILITY_MEMORY_DIR ||
  join(process.env.HOME || '', '.radical-accessibility', 'memory');
const DETECTIONS_FILE = join(MEMORY_DIR, 'detections.jsonl');

// Architectural keywords for quick text-based detection
const ARCHITECTURAL_KEYWORDS = [
  // Drawing types
  'floor plan', 'floorplan', 'site plan', 'section', 'elevation',
  'detail', 'diagram', 'sketch', 'drawing', 'axonometric', 'isometric',
  'perspective', 'rendering', 'blueprint',
  // Architectural elements
  'building', 'house', 'apartment', 'office', 'structure',
  'wall', 'door', 'window', 'stair', 'room', 'space',
  // Scales and annotations
  'scale', '1:100', '1:50', '1:200', 'dimensions',
  // Programs
  'bedroom', 'bathroom', 'kitchen', 'living', 'dining',
  'lobby', 'corridor', 'entrance', 'exit',
  // Professional terms
  'architect', 'architecture', 'cad', 'revit', 'autocad',
  'tactile', 'piaf', 'accessible', 'blind', 'low vision'
];

// File extensions that indicate images
const IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.pdf'];

/**
 * Ensure memory directory exists
 */
function ensureMemoryDir(): void {
  if (!existsSync(MEMORY_DIR)) {
    mkdirSync(MEMORY_DIR, { recursive: true });
    console.error(`[ImageDetector] Created memory directory: ${MEMORY_DIR}`);
  }
}

/**
 * Log detection to memory for learning
 */
function logDetection(log: DetectionLog): void {
  ensureMemoryDir();
  const line = JSON.stringify(log) + '\n';
  appendFileSync(DETECTIONS_FILE, line);
  console.error(`[ImageDetector] Logged detection: ${log.category}`);
}

/**
 * Check if message text contains architectural keywords
 */
function hasArchitecturalKeywords(text: string): { found: boolean; matches: string[] } {
  const lowerText = text.toLowerCase();
  const matches = ARCHITECTURAL_KEYWORDS.filter(keyword =>
    lowerText.includes(keyword.toLowerCase())
  );
  return { found: matches.length > 0, matches };
}

/**
 * Check if attachments contain images
 */
function hasImageAttachments(attachments?: Attachment[]): boolean {
  if (!attachments || attachments.length === 0) return false;

  return attachments.some(att => {
    if (att.mimeType?.startsWith('image/')) return true;
    if (att.type === 'image') return true;
    if (att.path) {
      const ext = att.path.toLowerCase().slice(att.path.lastIndexOf('.'));
      return IMAGE_EXTENSIONS.includes(ext);
    }
    return false;
  });
}

/**
 * Determine suggested preset based on keywords
 */
function suggestPreset(keywords: string[]): string {
  const keywordSet = new Set(keywords.map(k => k.toLowerCase()));

  if (keywordSet.has('floor plan') || keywordSet.has('floorplan')) return 'floor_plan';
  if (keywordSet.has('section')) return 'section';
  if (keywordSet.has('elevation')) return 'elevation';
  if (keywordSet.has('site plan')) return 'site_plan';
  if (keywordSet.has('sketch')) return 'sketch';
  if (keywordSet.has('detail')) return 'technical_drawing';
  if (keywordSet.has('diagram')) return 'diagram';

  return 'floor_plan'; // Default
}

/**
 * Analyze input and determine if architectural image is present
 */
function analyzeInput(input: HookInput): DetectionResult {
  const message = input.message || '';
  const { found: hasKeywords, matches: keywordMatches } = hasArchitecturalKeywords(message);
  const hasImages = hasImageAttachments(input.attachments) ||
    (input.images && input.images.length > 0);

  // Case 1: Has both images and architectural keywords - high confidence
  if (hasImages && hasKeywords) {
    const preset = suggestPreset(keywordMatches);
    return {
      detected: true,
      category: inferCategory(keywordMatches),
      confidence: 'high',
      suggestedAction: 'offer_conversion',
      suggestedPreset: preset,
      reasoning: `Image attachment detected with architectural keywords: ${keywordMatches.slice(0, 3).join(', ')}`
    };
  }

  // Case 2: Has images but no keywords - needs vision analysis
  if (hasImages && !hasKeywords) {
    return {
      detected: true,
      category: 'needs_analysis',
      confidence: 'low',
      suggestedAction: 'analyze_with_vision',
      reasoning: 'Image detected but no architectural keywords. Vision analysis recommended.'
    };
  }

  // Case 3: Has keywords but no images - might be discussing plans
  if (hasKeywords && !hasImages) {
    return {
      detected: false,
      category: 'discussion_only',
      confidence: 'medium',
      suggestedAction: 'none',
      reasoning: `Architectural discussion detected (${keywordMatches.slice(0, 3).join(', ')}) but no images attached.`
    };
  }

  // Case 4: Nothing relevant
  return {
    detected: false,
    category: 'non_architectural',
    confidence: 'high',
    suggestedAction: 'none',
    reasoning: 'No architectural images or keywords detected.'
  };
}

/**
 * Infer category from keyword matches
 */
function inferCategory(keywords: string[]): string {
  const keywordSet = new Set(keywords.map(k => k.toLowerCase()));

  if (keywordSet.has('floor plan') || keywordSet.has('floorplan')) return 'floor_plan';
  if (keywordSet.has('section')) return 'section';
  if (keywordSet.has('elevation')) return 'elevation';
  if (keywordSet.has('site plan')) return 'site_plan';
  if (keywordSet.has('sketch')) return 'sketch';
  if (keywordSet.has('detail')) return 'detail';
  if (keywordSet.has('diagram')) return 'diagram';
  if (keywordSet.has('axonometric') || keywordSet.has('isometric')) return 'diagram';

  return 'unknown';
}

/**
 * Generate helpful suggestion message
 */
function generateSuggestion(result: DetectionResult): string {
  switch (result.suggestedAction) {
    case 'offer_conversion':
      return `Architectural ${result.category.replace('_', ' ')} detected. Would you like me to:
1. **Convert to tactile** (TactileConversion) - Process the image for PIAF printing
2. **Generate simplified version** (TactileGeneration) - AI-create a cleaner tactile graphic
3. **Describe the image** (AccessibleDescription) - Provide detailed verbal description

Recommended preset: ${result.suggestedPreset}`;

    case 'analyze_with_vision':
      return `Image detected. Let me analyze if this is an architectural drawing that could be converted to tactile format.`;

    default:
      return '';
  }
}

/**
 * Main hook entry point
 */
async function main(): Promise<void> {
  try {
    // Read input from stdin
    const inputText = await Bun.stdin.text();

    if (!inputText || inputText.trim() === '') {
      // No input - silent exit
      console.error('[ImageDetector] No input received');
      process.exit(0);
    }

    let input: HookInput;
    try {
      input = JSON.parse(inputText);
    } catch (parseError) {
      // Might be plain text message
      input = { message: inputText };
    }

    // Analyze the input
    const result = analyzeInput(input);

    // Log detection if relevant
    if (result.detected || result.category !== 'non_architectural') {
      const log: DetectionLog = {
        timestamp: new Date().toISOString(),
        session_id: input.session_id || 'unknown',
        category: result.category,
        confidence: result.confidence,
        user_accepted: null, // Will be updated by feedback hook
        preset_used: result.suggestedPreset
      };
      logDetection(log);
    }

    // Output result for the agent to use
    const output = {
      ...result,
      suggestion: generateSuggestion(result)
    };

    console.log(JSON.stringify(output, null, 2));

    process.exit(0);
  } catch (error) {
    console.error(`[ImageDetector] Error: ${error}`);
    // Output error but don't block
    console.log(JSON.stringify({
      detected: false,
      category: 'error',
      confidence: 'low',
      suggestedAction: 'none',
      reasoning: `Error during detection: ${error}`
    }));
    process.exit(0); // Non-blocking exit
  }
}

main();

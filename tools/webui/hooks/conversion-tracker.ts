#!/usr/bin/env bun
/**
 * ConversionTracker.ts - Track Tactile Conversion Results
 *
 * PURPOSE:
 * Integrates with the TactileConversion skill to track all conversion
 * attempts, recording settings used, success/failure, and adjustments
 * made. Feeds data to the memory system for learning.
 *
 * TRIGGER: PostToolUse (after tactile conversion tools run)
 *
 * INPUT:
 * - stdin: Hook input JSON with tool_name, tool_input, tool_output
 *
 * OUTPUT:
 * - stdout: JSON confirmation of tracking
 * - stderr: Status messages
 *
 * TRACKED TOOLS:
 * - mcp__tactile__image_to_piaf
 * - TactileConvert (TypeScript wrapper)
 * - tactile CLI commands
 */

import { join } from 'path';
import { writeFileSync, mkdirSync, existsSync } from 'fs';
import memory from './lib/memory';

// Constants
const MEMORY_DIR = process.env.RADICAL_ACCESSIBILITY_MEMORY_DIR ||
  join(process.env.HOME || '', '.radical-accessibility', 'memory');
const RECENT_CONVERSION_FILE = join(MEMORY_DIR, 'recent_conversion.json');

/**
 * Save the most recent conversion ID for feedback capture
 */
function saveRecentConversion(conversionId: string, imageType: string): void {
  if (!existsSync(MEMORY_DIR)) {
    mkdirSync(MEMORY_DIR, { recursive: true });
  }
  writeFileSync(RECENT_CONVERSION_FILE, JSON.stringify({
    conversion_id: conversionId,
    image_type: imageType,
    timestamp: new Date().toISOString()
  }));
}

// Types
interface HookInput {
  session_id?: string;
  tool_name?: string;
  tool_input?: Record<string, any>;
  tool_output?: {
    success?: boolean;
    output_path?: string;
    error?: string;
    metadata?: Record<string, any>;
    duration_ms?: number;
  };
}

// Tools to track
const TRACKED_TOOLS = [
  'mcp__tactile__image_to_piaf',
  'mcp__tactile__analyze_image',
  'TactileConvert'
];

/**
 * Extract image type from input parameters
 */
function inferImageType(input: Record<string, any>): string {
  // Check preset
  if (input.preset) return input.preset;

  // Check image path for hints
  const imagePath = input.image_path || input.source || '';
  const lowerPath = imagePath.toLowerCase();

  if (lowerPath.includes('floor') || lowerPath.includes('plan')) return 'floor_plan';
  if (lowerPath.includes('section')) return 'section';
  if (lowerPath.includes('elevation') || lowerPath.includes('elev')) return 'elevation';
  if (lowerPath.includes('site')) return 'site_plan';
  if (lowerPath.includes('sketch')) return 'sketch';
  if (lowerPath.includes('detail')) return 'detail';
  if (lowerPath.includes('diagram')) return 'diagram';

  return 'unknown';
}

/**
 * Identify adjustments from defaults
 */
function identifyAdjustments(input: Record<string, any>): string[] {
  const adjustments: string[] = [];

  // Non-default settings
  if (input.threshold !== undefined && input.threshold !== null) {
    adjustments.push(`threshold=${input.threshold}`);
  }
  if (input.paper_size && input.paper_size !== 'letter') {
    adjustments.push(`paper_size=${input.paper_size}`);
  }
  if (input.braille_grade && input.braille_grade !== 2) {
    adjustments.push(`braille_grade=${input.braille_grade}`);
  }
  if (input.detect_text === false) {
    adjustments.push('detect_text=false');
  }
  if (input.auto_scale === false) {
    adjustments.push('auto_scale=false');
  }
  if (input.scale_percent) {
    adjustments.push(`scale_percent=${input.scale_percent}`);
  }
  if (input.max_scale_factor) {
    adjustments.push(`max_scale_factor=${input.max_scale_factor}`);
  }
  if (input.zoom_region || input.zoom_regions) {
    adjustments.push('zoom_used');
  }
  if (input.sticker_workflow) {
    adjustments.push('sticker_workflow');
  }

  return adjustments;
}

/**
 * Main hook entry point
 */
async function main(): Promise<void> {
  try {
    // Read input from stdin
    const inputText = await Bun.stdin.text();

    if (!inputText || inputText.trim() === '') {
      process.exit(0);
    }

    let input: HookInput;
    try {
      input = JSON.parse(inputText);
    } catch {
      console.error('[ConversionTracker] Invalid JSON input');
      process.exit(0);
    }

    // Check if this is a tracked tool
    if (!input.tool_name || !TRACKED_TOOLS.some(t => input.tool_name?.includes(t))) {
      // Not a conversion tool - silent exit
      process.exit(0);
    }

    const toolInput = input.tool_input || {};
    const toolOutput = input.tool_output || {};

    // Record the conversion
    const conversionId = memory.recordConversion({
      session_id: input.session_id || 'unknown',
      image_type: inferImageType(toolInput),
      preset_used: toolInput.preset || 'floor_plan',
      settings: {
        threshold: toolInput.threshold,
        paper_size: toolInput.paper_size,
        detect_text: toolInput.detect_text,
        braille_grade: toolInput.braille_grade,
        auto_scale: toolInput.auto_scale,
        scale_percent: toolInput.scale_percent,
        max_scale_factor: toolInput.max_scale_factor,
        use_abbreviation_key: toolInput.use_abbreviation_key,
        sticker_workflow: toolInput.sticker_workflow
      },
      source_path: toolInput.image_path,
      output_path: toolOutput.output_path,
      success: toolOutput.success !== false && !toolOutput.error,
      error_message: toolOutput.error,
      duration_ms: toolOutput.duration_ms,
      adjustments_made: identifyAdjustments(toolInput)
    });

    console.error(`[ConversionTracker] Recorded conversion ${conversionId}`);

    // Save as recent conversion for feedback capture
    saveRecentConversion(conversionId, inferImageType(toolInput));

    // Output confirmation
    console.log(JSON.stringify({
      tracked: true,
      conversion_id: conversionId,
      image_type: inferImageType(toolInput),
      success: toolOutput.success !== false && !toolOutput.error
    }));

    process.exit(0);
  } catch (error) {
    console.error(`[ConversionTracker] Error: ${error}`);
    process.exit(0); // Non-blocking
  }
}

main();

#!/usr/bin/env bun
/**
 * memory.ts - Radical Accessibility Memory Integration
 *
 * PURPOSE:
 * Tracks successful conversions, learns preferred settings, and captures
 * student feedback to improve recommendations over time.
 *
 * STORAGE FORMAT:
 * Uses JSONL files for easy appending and streaming reads:
 * - conversions.jsonl: Records of all conversion attempts
 * - preferences.jsonl: Learned settings preferences by image type
 * - feedback.jsonl: Student ratings and comments
 *
 * LEARNING:
 * - Aggregates success rates by preset and image type
 * - Identifies commonly adjusted settings
 * - Surfaces patterns in student feedback
 */

import {
  readFileSync,
  writeFileSync,
  appendFileSync,
  existsSync,
  mkdirSync
} from 'fs';
import { join } from 'path';

// Types
export interface ConversionRecord {
  id: string;
  timestamp: string;
  session_id: string;
  image_type: string;
  preset_used: string;
  settings: Record<string, any>;
  source_path?: string;
  output_path?: string;
  success: boolean;
  error_message?: string;
  duration_ms?: number;
  adjustments_made: string[]; // Settings user changed from defaults
}

export interface PreferenceRecord {
  timestamp: string;
  image_type: string;
  preset: string;
  setting_key: string;
  setting_value: any;
  frequency: number; // Times this preference was used
  success_rate: number; // 0-1
}

export interface FeedbackRecord {
  timestamp: string;
  conversion_id: string;
  rating: number; // 1-5
  comment?: string;
  useful_for_learning: boolean;
  tags?: string[]; // e.g., 'too_dense', 'missing_labels', 'perfect'
}

export interface LearningInsight {
  image_type: string;
  recommended_preset: string;
  recommended_settings: Record<string, any>;
  confidence: number;
  based_on_samples: number;
  common_issues: string[];
}

// Constants
const DEFAULT_MEMORY_DIR = join(process.env.HOME || '', '.radical-accessibility', 'memory');
const MEMORY_DIR = process.env.RADICAL_ACCESSIBILITY_MEMORY_DIR || DEFAULT_MEMORY_DIR;

const FILES = {
  conversions: join(MEMORY_DIR, 'conversions.jsonl'),
  preferences: join(MEMORY_DIR, 'preferences.jsonl'),
  feedback: join(MEMORY_DIR, 'feedback.jsonl'),
  learnings: join(MEMORY_DIR, 'learnings.json')
};

/**
 * Ensure memory directory and files exist
 */
export function ensureMemorySetup(): void {
  if (!existsSync(MEMORY_DIR)) {
    mkdirSync(MEMORY_DIR, { recursive: true });
  }
}

/**
 * Generate unique ID for records
 */
function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

/**
 * Read all records from a JSONL file
 */
function readJsonl<T>(filepath: string): T[] {
  if (!existsSync(filepath)) return [];

  const content = readFileSync(filepath, 'utf-8');
  const lines = content.trim().split('\n').filter(line => line);

  return lines.map(line => {
    try {
      return JSON.parse(line) as T;
    } catch {
      return null;
    }
  }).filter((item): item is T => item !== null);
}

/**
 * Append a record to a JSONL file
 */
function appendJsonl<T>(filepath: string, record: T): void {
  ensureMemorySetup();
  const line = JSON.stringify(record) + '\n';
  appendFileSync(filepath, line);
}

// ============================================================
// CONVERSION TRACKING
// ============================================================

/**
 * Record a conversion attempt
 */
export function recordConversion(params: {
  session_id: string;
  image_type: string;
  preset_used: string;
  settings: Record<string, any>;
  source_path?: string;
  output_path?: string;
  success: boolean;
  error_message?: string;
  duration_ms?: number;
  adjustments_made?: string[];
}): string {
  const id = generateId();

  const record: ConversionRecord = {
    id,
    timestamp: new Date().toISOString(),
    session_id: params.session_id,
    image_type: params.image_type,
    preset_used: params.preset_used,
    settings: params.settings,
    source_path: params.source_path,
    output_path: params.output_path,
    success: params.success,
    error_message: params.error_message,
    duration_ms: params.duration_ms,
    adjustments_made: params.adjustments_made || []
  };

  appendJsonl(FILES.conversions, record);

  // If successful, update preferences
  if (params.success && params.adjustments_made && params.adjustments_made.length > 0) {
    updatePreferences(params.image_type, params.preset_used, params.settings);
  }

  return id;
}

/**
 * Get conversion history for an image type
 */
export function getConversionHistory(imageType?: string): ConversionRecord[] {
  const records = readJsonl<ConversionRecord>(FILES.conversions);

  if (imageType) {
    return records.filter(r => r.image_type === imageType);
  }

  return records;
}

/**
 * Get success rate for a preset
 */
export function getPresetSuccessRate(preset: string): number {
  const records = readJsonl<ConversionRecord>(FILES.conversions)
    .filter(r => r.preset_used === preset);

  if (records.length === 0) return 0;

  const successful = records.filter(r => r.success).length;
  return successful / records.length;
}

// ============================================================
// PREFERENCE LEARNING
// ============================================================

/**
 * Update learned preferences based on successful conversion
 */
function updatePreferences(
  imageType: string,
  preset: string,
  settings: Record<string, any>
): void {
  const existingPrefs = readJsonl<PreferenceRecord>(FILES.preferences);

  // Track each setting that differs from defaults
  for (const [key, value] of Object.entries(settings)) {
    const existing = existingPrefs.find(
      p => p.image_type === imageType && p.setting_key === key
    );

    if (existing) {
      // Update frequency and success rate
      const updatedRecord: PreferenceRecord = {
        ...existing,
        timestamp: new Date().toISOString(),
        setting_value: value,
        frequency: existing.frequency + 1,
        success_rate: (existing.success_rate * existing.frequency + 1) / (existing.frequency + 1)
      };

      // Rewrite file with updated record (simple approach for small files)
      const updatedPrefs = existingPrefs.map(p =>
        (p.image_type === imageType && p.setting_key === key) ? updatedRecord : p
      );
      writeFileSync(FILES.preferences, updatedPrefs.map(p => JSON.stringify(p)).join('\n') + '\n');
    } else {
      // New preference
      const newRecord: PreferenceRecord = {
        timestamp: new Date().toISOString(),
        image_type: imageType,
        preset,
        setting_key: key,
        setting_value: value,
        frequency: 1,
        success_rate: 1.0
      };
      appendJsonl(FILES.preferences, newRecord);
    }
  }
}

/**
 * Get recommended settings for an image type
 */
export function getRecommendedSettings(imageType: string): Record<string, any> {
  const preferences = readJsonl<PreferenceRecord>(FILES.preferences)
    .filter(p => p.image_type === imageType)
    .filter(p => p.frequency >= 2 && p.success_rate >= 0.7) // Only use well-tested prefs
    .sort((a, b) => b.success_rate - a.success_rate);

  const settings: Record<string, any> = {};

  for (const pref of preferences) {
    if (!(pref.setting_key in settings)) {
      settings[pref.setting_key] = pref.setting_value;
    }
  }

  return settings;
}

// ============================================================
// FEEDBACK TRACKING
// ============================================================

/**
 * Record student feedback
 */
export function recordFeedback(params: {
  conversion_id: string;
  rating: number;
  comment?: string;
  tags?: string[];
}): void {
  const record: FeedbackRecord = {
    timestamp: new Date().toISOString(),
    conversion_id: params.conversion_id,
    rating: params.rating,
    comment: params.comment,
    useful_for_learning: params.rating <= 2 || params.rating >= 4, // Extremes are most useful
    tags: params.tags
  };

  appendJsonl(FILES.feedback, record);

  // Update conversion success based on feedback
  if (params.rating <= 2) {
    // Mark as unsuccessful if user rated poorly
    markConversionFailed(params.conversion_id);
  }
}

/**
 * Mark a conversion as failed based on feedback
 */
function markConversionFailed(conversionId: string): void {
  const records = readJsonl<ConversionRecord>(FILES.conversions);
  const updated = records.map(r => {
    if (r.id === conversionId) {
      return { ...r, success: false, error_message: 'Marked unsuccessful by user feedback' };
    }
    return r;
  });

  writeFileSync(FILES.conversions, updated.map(r => JSON.stringify(r)).join('\n') + '\n');
}

/**
 * Get feedback statistics
 */
export function getFeedbackStats(): {
  total: number;
  average_rating: number;
  common_issues: { tag: string; count: number }[];
} {
  const feedback = readJsonl<FeedbackRecord>(FILES.feedback);

  if (feedback.length === 0) {
    return { total: 0, average_rating: 0, common_issues: [] };
  }

  const total = feedback.length;
  const average_rating = feedback.reduce((sum, f) => sum + f.rating, 0) / total;

  // Count tags
  const tagCounts: Record<string, number> = {};
  for (const record of feedback) {
    for (const tag of record.tags || []) {
      tagCounts[tag] = (tagCounts[tag] || 0) + 1;
    }
  }

  const common_issues = Object.entries(tagCounts)
    .map(([tag, count]) => ({ tag, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);

  return { total, average_rating, common_issues };
}

// ============================================================
// LEARNING INSIGHTS
// ============================================================

/**
 * Generate learning insights for an image type
 */
export function generateInsights(imageType: string): LearningInsight | null {
  const conversions = getConversionHistory(imageType);

  if (conversions.length < 3) {
    // Not enough data
    return null;
  }

  // Find most successful preset
  const presetStats: Record<string, { success: number; total: number }> = {};
  for (const conv of conversions) {
    if (!presetStats[conv.preset_used]) {
      presetStats[conv.preset_used] = { success: 0, total: 0 };
    }
    presetStats[conv.preset_used].total++;
    if (conv.success) presetStats[conv.preset_used].success++;
  }

  const bestPreset = Object.entries(presetStats)
    .map(([preset, stats]) => ({
      preset,
      rate: stats.success / stats.total,
      samples: stats.total
    }))
    .sort((a, b) => b.rate - a.rate)[0];

  // Get recommended settings
  const settings = getRecommendedSettings(imageType);

  // Identify common issues from feedback
  const feedback = readJsonl<FeedbackRecord>(FILES.feedback);
  const conversionIds = new Set(conversions.map(c => c.id));
  const relevantFeedback = feedback.filter(f => conversionIds.has(f.conversion_id));

  const issues: Record<string, number> = {};
  for (const fb of relevantFeedback) {
    if (fb.rating <= 2) {
      for (const tag of fb.tags || []) {
        issues[tag] = (issues[tag] || 0) + 1;
      }
    }
  }

  const commonIssues = Object.entries(issues)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([tag]) => tag);

  return {
    image_type: imageType,
    recommended_preset: bestPreset?.preset || 'floor_plan',
    recommended_settings: settings,
    confidence: bestPreset?.rate || 0,
    based_on_samples: conversions.length,
    common_issues: commonIssues
  };
}

/**
 * Save current learnings to file for quick access
 */
export function saveLearnings(): void {
  const imageTypes = ['floor_plan', 'section', 'elevation', 'site_plan', 'sketch', 'diagram', 'detail'];

  const learnings: Record<string, LearningInsight> = {};

  for (const imageType of imageTypes) {
    const insight = generateInsights(imageType);
    if (insight) {
      learnings[imageType] = insight;
    }
  }

  writeFileSync(FILES.learnings, JSON.stringify(learnings, null, 2));
}

/**
 * Load saved learnings
 */
export function loadLearnings(): Record<string, LearningInsight> {
  if (!existsSync(FILES.learnings)) {
    return {};
  }

  try {
    return JSON.parse(readFileSync(FILES.learnings, 'utf-8'));
  } catch {
    return {};
  }
}

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

/**
 * Get memory statistics summary
 */
export function getMemoryStats(): {
  total_conversions: number;
  successful_conversions: number;
  total_feedback: number;
  learned_preferences: number;
  image_types_tracked: string[];
} {
  const conversions = readJsonl<ConversionRecord>(FILES.conversions);
  const feedback = readJsonl<FeedbackRecord>(FILES.feedback);
  const preferences = readJsonl<PreferenceRecord>(FILES.preferences);

  const imageTypes = [...new Set(conversions.map(c => c.image_type))];

  return {
    total_conversions: conversions.length,
    successful_conversions: conversions.filter(c => c.success).length,
    total_feedback: feedback.length,
    learned_preferences: preferences.length,
    image_types_tracked: imageTypes
  };
}

/**
 * Clear all memory (for testing/reset)
 */
export function clearMemory(): void {
  if (existsSync(FILES.conversions)) writeFileSync(FILES.conversions, '');
  if (existsSync(FILES.preferences)) writeFileSync(FILES.preferences, '');
  if (existsSync(FILES.feedback)) writeFileSync(FILES.feedback, '');
  if (existsSync(FILES.learnings)) writeFileSync(FILES.learnings, '{}');
}

// Export for use by other modules
export default {
  ensureMemorySetup,
  recordConversion,
  getConversionHistory,
  getPresetSuccessRate,
  getRecommendedSettings,
  recordFeedback,
  getFeedbackStats,
  generateInsights,
  saveLearnings,
  loadLearnings,
  getMemoryStats,
  clearMemory
};

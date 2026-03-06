#!/usr/bin/env bun
/**
 * FeedbackCapture.ts - Capture Student Feedback on Conversions
 *
 * PURPOSE:
 * Captures student feedback and ratings for tactile conversions.
 * This feedback is used to improve the learning system and refine
 * recommendations for future conversions.
 *
 * TRIGGER: UserPromptSubmit (when user provides rating/feedback)
 *
 * INPUT:
 * - stdin: Hook input JSON containing user message
 *
 * OUTPUT:
 * - stdout: JSON with feedback captured status
 * - stderr: Status messages
 *
 * DETECTION PATTERNS:
 * - Explicit ratings: "rate 4", "4/5 stars", "rating: 3"
 * - Thumbs feedback: "thumbs up", "thumbs down", "+1", "-1"
 * - Sentiment words: "perfect", "good", "bad", "terrible", etc.
 * - Issue tags: "too dense", "missing labels", "hard to read"
 */

import { readFileSync, existsSync } from 'fs';
import { join } from 'path';
import memory from './lib/memory';

// Types
interface HookInput {
  session_id?: string;
  message?: string;
}

interface FeedbackExtraction {
  rating?: number;
  comment?: string;
  tags: string[];
  isExplicitFeedback: boolean;
}

// Memory path for tracking recent conversions
const MEMORY_DIR = process.env.RADICAL_ACCESSIBILITY_MEMORY_DIR ||
  join(process.env.HOME || '', '.radical-accessibility', 'memory');
const RECENT_CONVERSION_FILE = join(MEMORY_DIR, 'recent_conversion.json');

// Sentiment mappings
const POSITIVE_WORDS = [
  'perfect', 'great', 'excellent', 'good', 'nice', 'helpful',
  'clear', 'readable', 'works', 'love', 'amazing', 'fantastic'
];

const NEGATIVE_WORDS = [
  'bad', 'terrible', 'awful', 'poor', 'wrong', 'broken',
  'unclear', 'confusing', 'hard', 'difficult', 'useless', 'hate'
];

// Issue tags (problems users might mention)
const ISSUE_PATTERNS: { pattern: RegExp; tag: string }[] = [
  { pattern: /too\s+dens/i, tag: 'too_dense' },
  { pattern: /too\s+sparse/i, tag: 'too_sparse' },
  { pattern: /missing\s+label/i, tag: 'missing_labels' },
  { pattern: /hard\s+to\s+read/i, tag: 'hard_to_read' },
  { pattern: /wrong\s+scale/i, tag: 'wrong_scale' },
  { pattern: /too\s+small/i, tag: 'too_small' },
  { pattern: /too\s+big/i, tag: 'too_big' },
  { pattern: /braille.*wrong/i, tag: 'braille_issue' },
  { pattern: /can'?t\s+feel/i, tag: 'tactile_unclear' },
  { pattern: /overlapping/i, tag: 'overlapping_elements' },
  { pattern: /cut\s*off/i, tag: 'content_cutoff' },
  { pattern: /blurry|fuzzy/i, tag: 'blurry' }
];

/**
 * Extract rating from text
 */
function extractRating(text: string): number | undefined {
  const lowerText = text.toLowerCase();

  // Explicit numeric rating patterns
  const patterns = [
    /rate[d]?\s*(\d)/i,           // "rate 4", "rated 3"
    /rating[:\s]*(\d)/i,          // "rating: 4", "rating 3"
    /(\d)\s*(?:out of\s*)?(?:\/|of)\s*5/i,  // "4/5", "4 out of 5"
    /(\d)\s*stars?/i,             // "4 stars", "4 star"
    /^(\d)\s*$/                   // Just a number
  ];

  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) {
      const rating = parseInt(match[1], 10);
      if (rating >= 1 && rating <= 5) return rating;
    }
  }

  // Thumbs patterns
  if (/thumbs?\s*up|\+1|👍/i.test(text)) return 4;
  if (/thumbs?\s*down|-1|👎/i.test(text)) return 2;

  // Sentiment-based inference
  const hasPositive = POSITIVE_WORDS.some(w => lowerText.includes(w));
  const hasNegative = NEGATIVE_WORDS.some(w => lowerText.includes(w));

  if (hasPositive && !hasNegative) return 4;
  if (hasNegative && !hasPositive) return 2;
  if (hasPositive && hasNegative) return 3; // Mixed

  return undefined;
}

/**
 * Extract issue tags from text
 */
function extractTags(text: string): string[] {
  const tags: string[] = [];

  for (const { pattern, tag } of ISSUE_PATTERNS) {
    if (pattern.test(text)) {
      tags.push(tag);
    }
  }

  return tags;
}

/**
 * Check if message is likely feedback about a conversion
 */
function isFeedbackMessage(text: string): boolean {
  const lowerText = text.toLowerCase();

  // Contains feedback keywords
  const feedbackKeywords = [
    'rate', 'rating', 'stars', 'score',
    'feedback', 'review', 'think', 'thought',
    'looks', 'feels', 'worked', 'output', 'result',
    'tactile', 'piaf', 'conversion', 'braille'
  ];

  const hasFeedbackKeyword = feedbackKeywords.some(k => lowerText.includes(k));
  const hasRating = extractRating(text) !== undefined;
  const hasTags = extractTags(text).length > 0;
  const hasSentiment = POSITIVE_WORDS.some(w => lowerText.includes(w)) ||
    NEGATIVE_WORDS.some(w => lowerText.includes(w));

  return hasFeedbackKeyword || hasRating || hasTags || hasSentiment;
}

/**
 * Get the most recent conversion ID
 */
function getRecentConversionId(): string | null {
  if (!existsSync(RECENT_CONVERSION_FILE)) return null;

  try {
    const data = JSON.parse(readFileSync(RECENT_CONVERSION_FILE, 'utf-8'));
    return data.conversion_id || null;
  } catch {
    return null;
  }
}

/**
 * Extract feedback from message
 */
function extractFeedback(text: string): FeedbackExtraction {
  return {
    rating: extractRating(text),
    comment: text.length > 10 ? text : undefined,
    tags: extractTags(text),
    isExplicitFeedback: isFeedbackMessage(text)
  };
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
      // Might be plain text
      input = { message: inputText };
    }

    const message = input.message || '';

    // Check if this looks like feedback
    const feedback = extractFeedback(message);

    if (!feedback.isExplicitFeedback) {
      // Not feedback - silent exit
      process.exit(0);
    }

    // Get the recent conversion to attach feedback to
    const conversionId = getRecentConversionId();

    if (!conversionId && feedback.rating !== undefined) {
      console.error('[FeedbackCapture] No recent conversion to attach feedback to');
      // Still output that we detected feedback
      console.log(JSON.stringify({
        feedback_detected: true,
        captured: false,
        reason: 'no_recent_conversion',
        extracted: feedback
      }));
      process.exit(0);
    }

    if (conversionId && (feedback.rating !== undefined || feedback.tags.length > 0)) {
      // Record the feedback
      memory.recordFeedback({
        conversion_id: conversionId,
        rating: feedback.rating || 3, // Default to neutral if only tags
        comment: feedback.comment,
        tags: feedback.tags
      });

      console.error(`[FeedbackCapture] Recorded feedback for ${conversionId}`);

      console.log(JSON.stringify({
        feedback_detected: true,
        captured: true,
        conversion_id: conversionId,
        rating: feedback.rating,
        tags: feedback.tags
      }));
    } else {
      console.log(JSON.stringify({
        feedback_detected: true,
        captured: false,
        reason: 'insufficient_feedback_data',
        extracted: feedback
      }));
    }

    process.exit(0);
  } catch (error) {
    console.error(`[FeedbackCapture] Error: ${error}`);
    process.exit(0); // Non-blocking
  }
}

main();

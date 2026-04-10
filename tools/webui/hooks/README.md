# Radical Accessibility Hooks

This directory contains optional hooks for integrating Radical Accessibility with PAI or Claude Code. These hooks enable proactive features like:

- **Automatic image detection** - Offers tactile conversion when architectural images are detected
- **Conversion tracking** - Records all conversion attempts for learning
- **Feedback capture** - Captures student ratings to improve recommendations

## Hook Overview

| Hook | Trigger | Purpose |
|------|---------|---------|
| `image-detector.ts` | UserPromptSubmit | Detects architectural images and offers conversion options |
| `conversion-tracker.ts` | PostToolUse | Records conversion attempts and settings |
| `feedback-capture.ts` | UserPromptSubmit | Captures student ratings and feedback |

## Installation

### For PAI Users

Add hooks to your `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "*",
        "hooks": [
          { "type": "command", "command": "tools/webui/hooks/image-detector.ts" },
          { "type": "command", "command": "tools/webui/hooks/feedback-capture.ts" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "mcp__tact__*",
        "hooks": [
          { "type": "command", "command": "tools/webui/hooks/conversion-tracker.ts" }
        ]
      }
    ]
  }
}
```

### For Claude Code Users (No PAI)

Claude Code supports hooks via `.claude/settings.json` in your project or home directory:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "mcp__tact__*",
        "hooks": [
          { "type": "command", "command": "bun tools/webui/hooks/conversion-tracker.ts" }
        ]
      }
    ]
  }
}
```

## Memory Storage

Hooks store learning data in `~/.radical-accessibility/memory/` by default. Customize with:

```bash
export RADICAL_ACCESSIBILITY_MEMORY_DIR="/custom/path/to/memory"
```

### Memory Files

| File | Contents |
|------|----------|
| `conversions.jsonl` | All conversion attempts with settings and results |
| `preferences.jsonl` | Learned settings preferences by image type |
| `feedback.jsonl` | Student ratings and comments |
| `learnings.json` | Aggregated insights for quick access |
| `detections.jsonl` | Image detection history |
| `recent_conversion.json` | Most recent conversion ID for feedback linking |

## Hook Behavior

### image-detector

Runs on every user message. Checks for:
1. Image attachments (looks at MIME type and file extension)
2. Architectural keywords in message text
3. Context clues about drawing type

Outputs suggestion for Claude to present to user if architectural content detected.

### conversion-tracker

Runs after any `mcp__tact__*` tool call. Records:
- Image type (preset or inferred from filename)
- All settings used
- Success/failure status
- Adjustments made from defaults

### feedback-capture

Listens for feedback patterns in user messages:
- Explicit ratings: "rate 4", "4/5 stars"
- Thumbs: "thumbs up", "+1"
- Sentiment: "perfect", "terrible"
- Issues: "too dense", "missing labels"

Links feedback to most recent conversion.

## Viewing Memory Data

Use the memory module to query stored data:

```typescript
import memory from './lib/memory';

// Get stats
const stats = memory.getMemoryStats();
console.log(stats);

// Get recommendations for floor plans
const settings = memory.getRecommendedSettings('floor_plan');
console.log(settings);

// Generate insights
const insights = memory.generateInsights('floor_plan');
console.log(insights);
```

## Privacy

All memory data is stored locally. Nothing is sent to external services. Students can:

1. View their data: Check `~/.radical-accessibility/memory/`
2. Clear data: `memory.clearMemory()` or delete the memory directory
3. Disable hooks: Remove from settings.json

## Dependencies

- **Bun** - TypeScript runtime (hooks use `#!/usr/bin/env bun`)
- **Node.js** - Alternative: change shebang to `#!/usr/bin/env npx ts-node`

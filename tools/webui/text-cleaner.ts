// text-cleaner.ts — Strip ANSI, markdown, and emoji from Claude responses
// Produces plain text suitable for JAWS screen reader output

// ANSI escape codes (colors, cursor movement, etc.)
const ANSI_RE = /\x1b\[[0-9;]*[A-Za-z]|\x1b\].*?\x07|\x1b\[.*?[@-~]/g

// Markdown patterns — order matters, process fenced blocks first
const FENCED_CODE_RE = /```[^\n]*\n([\s\S]*?)```/g
const INLINE_CODE_RE = /`([^`]+)`/g
const HEADING_RE = /^#{1,6}\s+/gm
const BOLD_ITALIC_RE = /(\*{1,3}|_{1,3})([^\n*_]+?)\1/g
const STRIKETHROUGH_RE = /~~([^~]+)~~/g
const LINK_RE = /\[([^\]]+)\]\([^)]+\)/g
const IMAGE_RE = /!\[([^\]]*)\]\([^)]+\)/g
const BLOCKQUOTE_RE = /^>\s?/gm
const HR_RE = /^[-*_]{3,}\s*$/gm
const BULLET_RE = /^[\s]*[-*+]\s+/gm
const NUMBERED_RE = /^[\s]*\d+\.\s+/gm
const HTML_TAG_RE = /<\/?[^>]+>/g

// Emoji: Unicode emoji ranges (supplementary + common symbols)
const EMOJI_RE =
  /[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{FE00}-\u{FE0F}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{200D}\u{20E3}\u{E0020}-\u{E007F}]/gu

// PAI response format markers (strip the emoji prefixes)
const PAI_MARKER_RE =
  /^[\u{1F4CB}\u{1F50D}\u{26A1}\u{2705}\u{1F4CA}\u{1F4C1}\u{27A1}\u{1F4D6}\u{2B50}\u{1F5E3}]\uFE0F?\s*/gmu

export function cleanText(raw: string): string {
  let text = raw

  // Strip ANSI escape codes
  text = text.replace(ANSI_RE, "")

  // Strip PAI format markers (emoji prefixes on lines like "SUMMARY:", "ANALYSIS:")
  text = text.replace(PAI_MARKER_RE, "")

  // Fenced code blocks: keep the content, drop the fences
  text = text.replace(FENCED_CODE_RE, "$1")

  // Inline code: keep the text
  text = text.replace(INLINE_CODE_RE, "$1")

  // Images: replace with alt text or drop
  text = text.replace(IMAGE_RE, (_, alt) => (alt ? alt : ""))

  // Links: keep the link text
  text = text.replace(LINK_RE, "$1")

  // Bold/italic: keep the text
  text = text.replace(BOLD_ITALIC_RE, "$2")

  // Strikethrough: keep the text
  text = text.replace(STRIKETHROUGH_RE, "$1")

  // Headings: strip the # prefix
  text = text.replace(HEADING_RE, "")

  // Blockquotes: strip > prefix
  text = text.replace(BLOCKQUOTE_RE, "")

  // Horizontal rules: remove entirely
  text = text.replace(HR_RE, "")

  // Bullets and numbered lists: strip the marker, keep text
  text = text.replace(BULLET_RE, "")
  text = text.replace(NUMBERED_RE, "")

  // HTML tags
  text = text.replace(HTML_TAG_RE, "")

  // Emoji
  text = text.replace(EMOJI_RE, "")

  // Collapse multiple blank lines into one
  text = text.replace(/\n{3,}/g, "\n\n")

  // Trim leading/trailing whitespace
  text = text.trim()

  return text
}

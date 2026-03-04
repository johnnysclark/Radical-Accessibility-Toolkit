# Tactile Core

A Python library for converting images to tactile-ready formats for PIAF (Picture In A Flash) printing. Part of the **Radical Accessibility** project for making architectural graphics accessible to blind and low-vision students.

## Installation

```bash
# From the Radical-Accessibility-Toolkit root
pip install -e ./tools/tact

# Or with MCP server support
pip install -e "./tools/tact[mcp]"
```

### System Dependencies

The library requires some system-level dependencies:

**Tesseract OCR** (for text detection):
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from https://github.com/UB-Mannheim/tesseract/wiki
```

**Poppler** (for PDF processing):
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler

# Windows
# Download from https://github.com/oschwartz10612/poppler-windows/releases
```

**LibLouis** (optional, for Grade 2 Braille):
```bash
# Ubuntu/Debian
sudo apt-get install liblouis-dev python3-louis liblouis-data

# macOS
brew install liblouis
pip install liblouis
```

## CLI Usage

```bash
# Basic conversion
tact convert input.jpg

# With preset
tact convert input.jpg --preset floor_plan

# With Braille labels
tact convert input.jpg --detect-text --braille-grade 2

# List available presets
tact presets
```

## Python API

```python
from tactile_core import ImageProcessor, PIAFPDFGenerator

# Process an image
processor = ImageProcessor()
result = processor.process("input.jpg", threshold=128)

# Generate PIAF-ready PDF
generator = PIAFPDFGenerator()
generator.generate(
    image_path="processed.png",
    output_path="output.pdf",
    paper_size="letter"
)
```

## Features

- **High-contrast processing** - Converts images to black/white with configurable threshold
- **Text detection** - OCR with Tesseract to identify labels and dimensions
- **Braille conversion** - Convert text to Braille (Grade 1 or Grade 2)
- **Auto-scaling** - Automatically scale images to fit Braille labels
- **Abbreviation keys** - Generate key pages for abbreviated labels
- **Multi-page output** - Split large images across multiple pages
- **Presets** - Optimized settings for floor plans, sections, sketches, etc.

## License

MIT

# Swell Print Tool — Placeholder

This folder is reserved for the swell-print image translator tool.
The tool converts architectural drawings into tactile swell paper
graphics that can be printed on a swell-form machine for blind users.

Status: Not yet implemented. The reference implementation lives in
Ethan Childs' fabric-accessible-graphics repository.

When this tool is built, it will:
- Accept a state.json or image file as input
- Generate high-contrast black-and-white line art
- Output PDF or PNG sized for swell paper (11x11.5 inches)
- Include braille labels at correct dot spacing
- Follow the project's accessibility-first IO conventions

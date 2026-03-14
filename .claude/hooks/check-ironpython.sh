#!/bin/bash
# Hook: Check IronPython 2.7 compatibility for files in tools/rhino/
# Called by PostToolUse hook when Python files in tools/rhino/ are edited.
# Exit 0 = OK, Exit 2 = block with warning.

# Read tool input from stdin (JSON with file_path)
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null)

# Only check files in tools/rhino/
case "$FILE_PATH" in
  */tools/rhino/*.py) ;;
  *) exit 0 ;;
esac

# Check if file exists
if [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

ISSUES=""

# Check for f-strings
FSTRINGS=$(grep -n 'f"' "$FILE_PATH" 2>/dev/null | head -5)
FSTRINGS2=$(grep -n "f'" "$FILE_PATH" 2>/dev/null | head -5)
if [ -n "$FSTRINGS" ] || [ -n "$FSTRINGS2" ]; then
  ISSUES="${ISSUES}f-string found (IronPython 2.7 incompatible, use .format()):\n${FSTRINGS}${FSTRINGS2}\n"
fi

# Check for pathlib
PATHLIB=$(grep -n 'from pathlib' "$FILE_PATH" 2>/dev/null)
PATHLIB2=$(grep -n 'import pathlib' "$FILE_PATH" 2>/dev/null)
if [ -n "$PATHLIB" ] || [ -n "$PATHLIB2" ]; then
  ISSUES="${ISSUES}pathlib import found (IronPython 2.7 incompatible, use os.path):\n${PATHLIB}${PATHLIB2}\n"
fi

# Check for type hints (basic patterns)
TYPEHINTS=$(grep -nE 'def \w+\(.*: (int|str|float|bool|list|dict|Optional|List|Dict|Tuple)' "$FILE_PATH" 2>/dev/null | head -3)
if [ -n "$TYPEHINTS" ]; then
  ISSUES="${ISSUES}Type hints found (IronPython 2.7 incompatible):\n${TYPEHINTS}\n"
fi

# Check for walrus operator
WALRUS=$(grep -n ':=' "$FILE_PATH" 2>/dev/null | head -3)
if [ -n "$WALRUS" ]; then
  ISSUES="${ISSUES}Walrus operator found (IronPython 2.7 incompatible):\n${WALRUS}\n"
fi

if [ -n "$ISSUES" ]; then
  echo -e "IronPython 2.7 compatibility issues in $FILE_PATH:\n$ISSUES" >&2
  exit 2
fi

exit 0

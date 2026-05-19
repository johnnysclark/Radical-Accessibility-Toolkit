"""
Screen-reader friendly logging system.

Provides clear, descriptive output formatted for accessibility.
All messages follow the pattern: [STATUS]: [Message]
"""

import sys
from typing import Optional


class AccessibleLogger:
    """
    Logger designed for screen reader compatibility.

    Features:
    - Clear, descriptive messages
    - No emojis or visual-only symbols
    - Consistent formatting
    - Real-time output (no buffering)
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize logger with verbosity level.

        Args:
            verbose: If True, output detailed progress messages
        """
        self.verbose = verbose

    def _output(self, message: str, force: bool = False):
        """
        Output message to stdout with immediate flush.

        Args:
            message: Message to output
            force: If True, output even if not verbose
        """
        if self.verbose or force:
            print(message, flush=True)

    def progress(self, message: str):
        """
        Output a progress update.

        Format: "Processing: [action]"

        Args:
            message: Description of current action
        """
        self._output(f"Processing: {message}")

    def loading(self, message: str):
        """
        Output a loading message.

        Format: "Loading: [item]"

        Args:
            message: Description of what is being loaded
        """
        self._output(f"Loading: {message}")

    def checking(self, message: str):
        """
        Output a checking/validation message.

        Format: "Checking: [what]"

        Args:
            message: Description of what is being checked
        """
        self._output(f"Checking: {message}")

    def found(self, message: str):
        """
        Output a discovery message.

        Format: "Found: [what was found]"

        Args:
            message: Description of what was found
        """
        self._output(f"Found: {message}")

    def generating(self, message: str):
        """
        Output a generation message.

        Format: "Generating: [what]"

        Args:
            message: Description of what is being generated
        """
        self._output(f"Generating: {message}")

    def success(self, message: str):
        """
        Output a success message (always shown, even if not verbose).

        Format: "Success: [message]"

        Args:
            message: Success message
        """
        self._output(f"Success: {message}", force=True)

    def complete(self, message: str):
        """
        Output a completion message (always shown).

        Format: "Complete: [message]"

        Args:
            message: Completion message
        """
        self._output(f"Complete: {message}", force=True)

    def warning(self, message: str):
        """
        Output a warning message (always shown).

        Format: "Warning: [message]"

        Args:
            message: Warning message
        """
        self._output(f"Warning: {message}", force=True)

    def error(self, message: str, exception: Optional[Exception] = None):
        """
        Output an error message to stderr (always shown).

        Format: "Error: [message]"
        If exception provided: "Details: [exception]"

        Args:
            message: Error message
            exception: Optional exception object for details
        """
        print(f"Error: {message}", file=sys.stderr, flush=True)
        if exception:
            print(f"Details: {str(exception)}", file=sys.stderr, flush=True)

    def solution(self, message: str):
        """
        Output a suggested solution (always shown).

        Format: "Solution: [message]"

        Args:
            message: Suggested solution
        """
        self._output(f"Solution: {message}", force=True)

    def info(self, message: str):
        """
        Output an informational message.

        Args:
            message: Information to display
        """
        self._output(message)

    def blank_line(self):
        """Output a blank line for readability."""
        if self.verbose:
            print(flush=True)

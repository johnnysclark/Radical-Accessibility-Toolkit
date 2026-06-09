"""jig: accessibility-first semantic layout controller for Rhino 8 on macOS.

This top-level __init__ must stay dependency-free and import nothing heavy:
the in-Rhino watcher bundle copies the whole package and imports only
jig.model and jig.geometry.
"""

__version__ = "0.1.0"
SCHEMA_VERSION = "jig_v4"

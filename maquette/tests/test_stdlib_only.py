"""The engine must run with zero pip installs.

Walk every module under src/maquette and assert its imports are
stdlib or maquette itself. Only the clearly separated optional
layers may import third-party packages.
"""

import ast
import os
import sys

SRC = os.path.join(os.path.dirname(__file__), "..", "src", "maquette")

THIRD_PARTY_ALLOWED = {
    "backends/headless.py": {"rhino3dm"},
    "mcp_server.py": {"mcp"},
    "chat.py": {"claude_agent_sdk"},
    # The listener runs inside Rhino; its host-only imports are guarded.
    "listener/maquette_listener.py": {"Rhino", "rhinoscriptsyntax",
                                      "scriptcontext", "System"},
}


def iter_modules():
    for root, _dirs, files in os.walk(os.path.abspath(SRC)):
        for name in files:
            if name.endswith(".py"):
                path = os.path.join(root, name)
                rel = os.path.relpath(path, os.path.abspath(SRC))
                yield rel.replace(os.sep, "/"), path


def top_level_imports(path):
    """Unconditional module-level imports only. Imports inside functions
    or try/except ImportError guards are the sanctioned lazy pattern for
    optional layers and do not count."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    found = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            if node.module:
                found.add(node.module.split(".")[0])
    return found


def test_engine_is_stdlib_only():
    stdlib = set(sys.stdlib_module_names)
    problems = []
    for rel, path in iter_modules():
        allowed = THIRD_PARTY_ALLOWED.get(rel, set())
        for module in top_level_imports(path):
            if module == "maquette" or module in stdlib or module in allowed:
                continue
            problems.append("{0} imports {1}".format(rel, module))
    assert not problems, "; ".join(sorted(problems))

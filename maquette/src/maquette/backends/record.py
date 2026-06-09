"""Record backend: journal the intent, realize nothing.

Always available (stdlib only). The scene's analytic fingerprints do
all the describing; a later rebuild against headless or live makes
the geometry real. This is also the degradation target whenever a
more capable backend cannot handle an op.
"""

from __future__ import annotations

from maquette.backends.base import BackendAPI, recorded


class RecordBackend(BackendAPI):
    name = "record"

    def apply(self, entry: dict, scene) -> dict:
        return recorded(self.name)

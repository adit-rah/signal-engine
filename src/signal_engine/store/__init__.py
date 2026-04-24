"""Signal Store (ARCHITECTURE.md component 9).

V1 uses a file-based store. The abstract interface below lets a future
version swap in a different implementation without touching the Fusion
Engine or the review surface.
"""

from signal_engine.store.filesystem import FilesystemSignalStore
from signal_engine.store.interface import SignalStore

__all__ = ["SignalStore", "FilesystemSignalStore"]

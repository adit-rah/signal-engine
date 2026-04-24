"""Command-line entry points.

Each module here exposes a `main()` function that re-uses library code
under `signal_engine/`. Legacy bin/scripts/ paths are preserved as thin
shims that import and call these `main()` functions.
"""

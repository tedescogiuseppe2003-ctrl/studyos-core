#!/usr/bin/env python3
"""Deprecated compatibility wrapper for the StudyOS output exporter.

This script is kept in the core repo only for legacy direct callers. It is not
installed into StudyOS workspaces by default. Use export_outputs.py instead.
"""

from __future__ import annotations

import sys

from export_outputs import main


if __name__ == "__main__":
    print(
        "Deprecated: export_final_pack.py is a legacy compatibility wrapper. "
        "Use export_outputs.py; final review packs are not generated.",
        file=sys.stderr,
    )
    raise SystemExit(main())

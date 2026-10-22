#!/usr/bin/env python3
"""Compatibility entry point for the per-user desktop installer."""

from pathlib import Path
import runpy


if __name__ == '__main__':
    installer = Path(__file__).resolve().parent / 'scripts' / 'install.py'
    runpy.run_path(str(installer), run_name='__main__')

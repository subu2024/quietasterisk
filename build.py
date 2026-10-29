#!/usr/bin/env python3
"""Entry point:  python build.py [--theme NAME] [--strict] [--serve] ..."""
import sys

from qa.cli import main

if __name__ == "__main__":
    sys.exit(main())

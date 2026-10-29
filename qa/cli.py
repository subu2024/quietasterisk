"""Command line interface: python build.py [options]"""

import argparse
import functools
import http.server
import logging
import socketserver
import sys
from datetime import date
from pathlib import Path

from . import __version__
from .build import BuildOptions, build
from .theme import ThemeError


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build the Quiet Asterisk site.")
    ap.add_argument("--root", default=".", help="project folder (default: current)")
    ap.add_argument("--content", help="content folder (default: <root>/content)")
    ap.add_argument("--themes", help="themes folder (default: <root>/themes)")
    ap.add_argument("--output", help="output folder (default: <root>/dist)")
    ap.add_argument("--theme", help="theme name (default: site.json 'theme')")
    ap.add_argument("--strict", action="store_true",
                    help="treat any warning as a failure and leave the existing output untouched")
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--hide-future", dest="hide_future", action="store_true", default=None,
                       help="do not publish entries dated after today")
    group.add_argument("--include-future", dest="hide_future", action="store_false",
                       help="publish future-dated entries even if site.json hides them")
    ap.add_argument("--today", help="pretend today is YYYY-MM-DD (for testing scheduled publishing)")
    ap.add_argument("--serve", type=int, nargs="?", const=8000, metavar="PORT",
                    help="after building, serve the output on http://localhost:PORT")
    ap.add_argument("--version", action="version", version=f"qa {__version__}")
    args = ap.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
    opts = BuildOptions(
        root=Path(args.root), content_dir=Path(args.content) if args.content else None,
        themes_dir=Path(args.themes) if args.themes else None,
        output_dir=Path(args.output) if args.output else None,
        theme=args.theme, strict=args.strict, hide_future=args.hide_future,
        today=date.fromisoformat(args.today) if args.today else None,
    )
    try:
        result = build(opts)
    except ThemeError as e:
        print(f"Theme error: {e}", file=sys.stderr)
        return 2
    if not result.ok:
        print(f"\nBuild failed (strict mode): {len(result.warnings)} warning(s):", file=sys.stderr)
        for message in result.warnings:
            print(f"  - {message}", file=sys.stderr)
        return 1

    if args.serve:
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(result.output))
        with socketserver.TCPServer(("", args.serve), handler) as httpd:
            print(f"Serving {result.output} at http://localhost:{args.serve}  (Ctrl+C to stop)")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                pass
    return 0

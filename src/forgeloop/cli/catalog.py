"""Search real public block metadata without an API key or model runtime."""

import argparse
import json
from pathlib import Path
from urllib.error import URLError

from ..public_sources import (
    DEFAULT_CATALOG,
    load_catalog,
    refresh_catalog,
    search_blocks,
)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", default="", help="Block name, ID, or role")
    parser.add_argument("--type", dest="kind", help="Filter by exact public role")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument(
        "--refresh",
        type=Path,
        metavar="DESTINATION",
        help="Download pinned public data into a cache; no key needed",
    )
    parser.add_argument(
        "--json", action="store_true", help="Include provenance in JSON output"
    )
    args = parser.parse_args(argv)
    try:
        catalog = (
            refresh_catalog(args.refresh)
            if args.refresh
            else load_catalog(args.catalog)
        )
        matches = search_blocks(catalog, args.query, args.kind)
    except (OSError, ValueError, URLError) as error:
        parser.exit(2, f"Catalog error: {error}\n")
    if args.json:
        print(json.dumps({**catalog, "blocks": matches}, indent=2))
    else:
        print(
            f"{len(matches)} matching blocks (public metadata; no physics validation)"
        )
        for block in matches:
            print(f"{block['id']:>4}  {block['name']:<30} {block['type']}")
        print(f"Source: {catalog.get('source', 'unspecified')}")
        print(f"License: {catalog['license']}")
        print(f"Attribution: {catalog['attribution']}")
        print(f"Limitations: {catalog['limitations']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

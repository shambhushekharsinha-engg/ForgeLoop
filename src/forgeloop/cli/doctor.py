"""Inspect local ForgeLoop readiness without network calls or game claims."""

import argparse
import importlib.metadata
import importlib.util
import json
import platform
import sys
from pathlib import Path

from ..public_sources import DEFAULT_CATALOG, load_catalog

ANALYSIS_PACKAGES = ("numpy", "pandas", "matplotlib", "rich")


def _dependency_check(name):
    try:
        found = importlib.util.find_spec(name) is not None
        version = importlib.metadata.version(name) if found else None
    except (ImportError, ValueError, importlib.metadata.PackageNotFoundError):
        found, version = False, None
    return {
        "name": name,
        "status": "available" if found else "missing",
        "required": False,
        "detail": f"{version}; installation detected, runtime import not tested"
        if found
        else 'Install with: python -m pip install -e ".[analysis]"',
    }


def check_environment(catalog_path=DEFAULT_CATALOG):
    """Return an offline, JSON-compatible report; do not import optional packages."""
    python_ok = sys.version_info >= (3, 10)
    checks = [
        {
            "name": "python",
            "status": "available" if python_ok else "unsupported",
            "required": True,
            "detail": f"{platform.python_version()} (requires 3.10 or newer)",
        }
    ]
    try:
        catalog = load_catalog(catalog_path)
        checks.append(
            {
                "name": "catalog",
                "status": "available",
                "required": True,
                "detail": f"{len(catalog['blocks'])} blocks; pinned revision {catalog['revision']}",
            }
        )
    except (OSError, ValueError) as error:
        checks.append(
            {
                "name": "catalog",
                "status": "invalid",
                "required": True,
                "detail": str(error),
            }
        )
    dependencies = [_dependency_check(name) for name in ANALYSIS_PACKAGES]
    checks.extend(dependencies)
    return {
        "platform": platform.system(),
        "machine": platform.machine(),
        "python_executable": sys.executable,
        "catalog_path": str(catalog_path),
        "core_ready": all(
            check["status"] == "available" for check in checks if check["required"]
        ),
        "analysis_available": all(
            check["status"] == "available" for check in dependencies
        ),
        "checks": checks,
        "limitations": "Offline checks only. Optional dependency imports, game installation, game connectivity, "
        "AI providers, flight performance, and competition eligibility are not verified.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--catalog",
        type=Path,
        default=DEFAULT_CATALOG,
        help="Local catalog to validate",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable readiness report"
    )
    parser.add_argument(
        "--require-analysis",
        action="store_true",
        help="Fail if optional analysis dependencies are absent",
    )
    args = parser.parse_args(argv)
    report = check_environment(args.catalog)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"ForgeLoop environment: {report['platform']} / {report['machine']}")
        for check in report["checks"]:
            print(f"[{check['status']}] {check['name']}: {check['detail']}")
        print(report["limitations"])
    return (
        0
        if report["core_ready"]
        and (not args.require_analysis or report["analysis_available"])
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())

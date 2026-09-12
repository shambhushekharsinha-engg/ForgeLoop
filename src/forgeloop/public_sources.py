"""Key-free access to a pinned, attributed BuildArena block-role catalog."""

import hashlib
import json
import math
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

try:
    import tomllib
except ImportError:  # Python 3.10
    import tomli as tomllib

REVISION = "fc5ef3bd6be30a69bb7bc7b0c1f2b53ea794ddbc"
SOURCE_URL = f"https://raw.githubusercontent.com/build-arena/BuildArena-2.0/{REVISION}/blocks/block_roles.toml"
LICENSE_URL = f"https://github.com/build-arena/BuildArena-2.0/blob/{REVISION}/LICENSE"
DEFAULT_CATALOG = Path(__file__).with_name("resources") / "block_catalog.json"
SCHEMA_VERSION = 1
MAX_BYTES = 1_000_000
MAX_BLOCKS = 4096


def _text(value, field, limit=1024):
    if (
        not isinstance(value, str)
        or not value.strip()
        or len(value) > limit
        or any(ord(char) < 32 or ord(char) == 127 for char in value)
    ):
        raise ValueError(
            f"Invalid catalog {field}: expected bounded nonempty text without control characters"
        )


def _validate_blocks(blocks):
    if not isinstance(blocks, list) or not 1 <= len(blocks) <= MAX_BLOCKS:
        raise ValueError(f"Invalid catalog: expected 1 to {MAX_BLOCKS} blocks")
    seen = set()
    for block in blocks:
        if not isinstance(block, dict):
            raise TypeError("Invalid catalog block")
        block_id = block.get("id")
        if (
            type(block_id) is not int
            or not 0 <= block_id <= 2**31 - 1
            or block_id in seen
        ):
            raise ValueError(
                "Invalid catalog block ID: IDs must be unique nonnegative integers"
            )
        seen.add(block_id)
        _text(block.get("name"), "block name", 256)
        _text(block.get("type"), "block type", 64)
        if "pointer_axis" in block:
            axis = block["pointer_axis"]
            if (
                not isinstance(axis, list)
                or len(axis) != 3
                or any(
                    type(value) not in (int, float)
                    or abs(value) > 1e12
                    or not math.isfinite(value)
                    for value in axis
                )
            ):
                raise ValueError(
                    "Invalid catalog pointer_axis: expected three finite numbers"
                )


def validate_catalog(catalog: dict) -> dict:
    """Validate the pinned catalog format, including provenance; return it unchanged.

    Legacy bundled catalogs without schema_version are version 1. The recorded
    source hash is provenance metadata, not proof that a local file is authentic.
    """
    if not isinstance(catalog, dict):
        raise TypeError("Invalid catalog: expected an object")
    version = catalog.get("schema_version", 1)
    if type(version) is not int or version != SCHEMA_VERSION:
        raise ValueError("Unsupported catalog schema_version")
    for field, expected in [
        ("source", SOURCE_URL),
        ("revision", REVISION),
        ("license", "CC-BY-NC-4.0"),
        ("license_url", LICENSE_URL),
    ]:
        if catalog.get(field) != expected:
            raise ValueError(
                f"Invalid catalog provenance: {field} does not match the pinned source"
            )
    for field in ("attribution", "limitations", "retrieved_at"):
        _text(catalog.get(field), field)
    digest = catalog.get("source_sha256")
    if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise ValueError("Invalid catalog source_sha256")
    try:
        retrieved = datetime.fromisoformat(
            catalog["retrieved_at"].replace("Z", "+00:00")
        )
    except ValueError as error:
        raise ValueError("Invalid catalog retrieved_at timestamp") from error
    if retrieved.tzinfo is None:
        raise ValueError("Invalid catalog retrieved_at: timezone is required")
    _validate_blocks(catalog.get("blocks"))
    return catalog


def parse_roles(payload: bytes) -> list[dict]:
    """Normalize public roles; these are not collision geometry or physics data."""
    if len(payload) > MAX_BYTES:
        raise ValueError("Public source exceeds size limit")
    roles = tomllib.loads(payload.decode("utf-8")).get("roles")
    if not isinstance(roles, dict) or not 1 <= len(roles) <= MAX_BLOCKS:
        raise ValueError("Public source has missing or excessive block roles")
    blocks = []
    for block_id, role in roles.items():
        if not re.fullmatch(r"[0-9]{1,10}", str(block_id)) or not isinstance(
            role, dict
        ):
            raise ValueError("Invalid block role")
        block = {
            "id": int(block_id),
            "name": role.get("block_name"),
            "type": role.get("type"),
        }
        if "pointer_axis" in role:
            block["pointer_axis"] = role["pointer_axis"]
        blocks.append(block)
    _validate_blocks(blocks)
    return sorted(blocks, key=lambda block: block["id"])


def refresh_catalog(destination: Path) -> dict:
    """Fetch the pinned source, validate, then atomically replace a local cache.

    Concurrent refreshes use independent temporary files. The last completed
    refresh wins; readers always see a complete catalog. Failed writes are removed.
    """
    request = Request(
        SOURCE_URL, headers={"User-Agent": "ForgeLoop-public-catalog/1.0"}
    )
    with urlopen(request, timeout=20) as response:
        payload = response.read(MAX_BYTES + 1)
    if len(payload) > MAX_BYTES:
        raise ValueError("Public source exceeds size limit")
    catalog = {
        "schema_version": SCHEMA_VERSION,
        "source": SOURCE_URL,
        "revision": REVISION,
        "license": "CC-BY-NC-4.0",
        "license_url": LICENSE_URL,
        "attribution": "BuildArena contributors; normalized from blocks/block_roles.toml",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": hashlib.sha256(payload).hexdigest(),
        "limitations": "Names and roles only. Game assets, collider dumps, flight evidence and an LLM are not included.",
        "blocks": parse_roles(payload),
    }
    validate_catalog(catalog)
    encoded = (json.dumps(catalog, indent=2, allow_nan=False) + "\n").encode("utf-8")
    if len(encoded) > MAX_BYTES:
        raise ValueError("Normalized catalog exceeds size limit")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return catalog


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate catalog JSON key: {key}")
        result[key] = value
    return result


def load_catalog(path: Path = DEFAULT_CATALOG) -> dict:
    with Path(path).open("rb") as stream:
        payload = stream.read(MAX_BYTES + 1)
    if len(payload) > MAX_BYTES:
        raise ValueError("Catalog exceeds size limit")
    try:
        catalog = json.loads(payload.decode("utf-8"), object_pairs_hook=_unique_object)
    except RecursionError as error:
        raise ValueError("Catalog nesting exceeds supported depth") from error
    return validate_catalog(catalog)


def search_blocks(
    catalog: dict, query: str = "", kind: str | None = None
) -> list[dict]:
    validate_catalog(catalog)
    if len(query) > 1024 or (kind is not None and len(kind) > 64):
        raise ValueError("Catalog query exceeds size limit")
    terms = query.casefold().split()
    return [
        block
        for block in catalog["blocks"]
        if (kind is None or block["type"].casefold() == kind.casefold())
        and all(
            term in f"{block['id']} {block['name']} {block['type']}".casefold()
            for term in terms
        )
    ]

"""Conservative structural checks, not competition eligibility verification.

BSG field layout checked against organizer source at commit
fc5ef3bd6be30a69bb7bc7b0c1f2b53ea794ddbc:
https://github.com/build-arena/BuildArena-2.0/blob/fc5ef3bd6be30a69bb7bc7b0c1f2b53ea794ddbc/buildarena/xml_builder.py
https://github.com/build-arena/BuildArena-2.0/blob/fc5ef3bd6be30a69bb7bc7b0c1f2b53ea794ddbc/buildarena/build.py
"""

import math
import xml.etree.ElementTree as ET
from uuid import UUID


def _one_child(parent, tag):
    children = parent.findall(tag)
    if len(children) != 1:
        raise ValueError(f"BSG {parent.tag} requires exactly one {tag}")
    return children[0]


def _vector(parent, tag, axes):
    node = _one_child(parent, tag)
    try:
        values = tuple(float(node.attrib[axis]) for axis in axes)
    except (KeyError, ValueError) as exc:
        raise ValueError(f"BSG {tag} requires numeric {axes} attributes") from exc
    if not all(math.isfinite(value) for value in values):
        raise ValueError(f"BSG {tag} contains nonfinite values")
    if tag == "Rotation" and not any(values):
        raise ValueError("BSG Rotation cannot be a zero quaternion")
    return values


def validate_bsg_structure(content: bytes):
    """Require the basic organizer XML shape and meaningful block transforms.

    Additional game-specific data and mod settings are intentionally not interpreted.
    No authenticity, geometry equivalence, or vanilla range guarantees are made.
    """
    # Organizer output is UTF-8 and does not use DTDs/entities. Reject declarations
    # before parsing so arbitrary XML entities cannot expand inside this checker.
    text = content.decode("utf-8-sig")
    if "<!DOCTYPE" in text.upper() or "<!ENTITY" in text.upper():
        raise ValueError("BSG DTD and entity declarations are unsupported")
    root = ET.fromstring(text)
    if root.tag != "Machine":
        raise ValueError("BSG root must be Machine")
    global_node = _one_child(root, "Global")
    _vector(global_node, "Position", "xyz")
    _vector(global_node, "Rotation", "xyzw")
    blocks_node = _one_child(root, "Blocks")
    blocks = list(blocks_node)
    if not blocks or any(block.tag != "Block" for block in blocks):
        raise ValueError("BSG Blocks requires one or more Block elements")
    seen = set()
    for block in blocks:
        try:
            block_id = int(block.attrib["id"])
            guid = UUID(block.attrib["guid"])
        except (KeyError, ValueError) as exc:
            raise ValueError("BSG Block requires an integer id and UUID guid") from exc
        if block_id < 0 or guid in seen:
            raise ValueError("BSG Block ids must be nonnegative and GUIDs unique")
        seen.add(guid)
        transform = _one_child(block, "Transform")
        _vector(transform, "Position", "xyz")
        _vector(transform, "Rotation", "xyzw")
        _vector(transform, "Scale", "xyz")
        _one_child(block, "Data")
    return root


def validate_no_geometry_changes(machine_raw, machine_tuned):
    """Fail explicitly: connector geometry also lives inside block Data payloads."""
    raise NotImplementedError(
        "Geometry validation requires a verified BSG schema; "
        "structural sanity checks cannot establish unchanged geometry."
    )

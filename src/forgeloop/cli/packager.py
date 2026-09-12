"""Package existing evidence without fabricating or rewriting artifacts."""

import csv
import errno
import io
import json
import math
import os
import stat
import shutil
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET
import zipfile

from ..data.validators import validate_bsg_structure


def _finite_json_float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("History contains a nonfinite number")
    return result


def _reject_json_constant(value):
    raise ValueError(f"History contains a nonstandard JSON constant: {value}")


def _unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"History contains duplicate key: {key}")
        result[key] = value
    return result


def _publish_without_overwrite(temporary, output):
    # Linux filesystems with hard links publish the completed archive atomically.
    # Some removable filesystems and Android runtimes lack hard links; there an
    # exclusive create still protects existing evidence, but publication is a copy.
    if hasattr(os, "link"):
        try:
            os.link(temporary, output)
            return
        except OSError as exc:
            if exc.errno not in (errno.ENOSYS, errno.EOPNOTSUPP, errno.EPERM, errno.EXDEV):
                raise
    with output.open("xb") as target:
        try:
            with temporary.open("rb") as source:
                shutil.copyfileobj(source, target)
        except BaseException:
            output.unlink(missing_ok=True)
            raise


class SubmissionPackager:
    # Repository artifact convention; confirm current competition requirements.
    REQUIRED_FILES = [
        "machine_raw.bsg",
        "build_history.json",
        "build_history_full.json",
        "machine_tuned.bsg",
        "trajectory.csv",
        "chat_transcript.md",
    ]

    def __init__(self, source_dir="submissions/latest", output_name="ForgeLoop_Submission.zip",
                 *, overwrite=False, max_artifact_bytes=64 * 1024 * 1024,
                 max_total_bytes=128 * 1024 * 1024):
        self.source_dir = Path(source_dir)
        self.output_name = output_name
        self.overwrite = overwrite
        for limit in (max_artifact_bytes, max_total_bytes):
            if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
                raise ValueError("Artifact size limits must be positive integers")
        self.max_artifact_bytes = max_artifact_bytes
        self.max_total_bytes = max_total_bytes

    def _read_bounded(self, path, remaining):
        # O_NOFOLLOW and fstat close the symlink/check-then-read race on Linux.
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        with os.fdopen(os.open(path, flags), "rb") as handle:
            info = os.fstat(handle.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise ValueError(f"Non-regular artifact: {path.name}")
            limit = min(self.max_artifact_bytes, remaining)
            if info.st_size > limit:
                raise ValueError(f"Artifact exceeds configured size limit: {path.name}")
            content = handle.read(limit + 1)
            if len(content) > limit:
                raise ValueError(f"Artifact exceeds configured size limit: {path.name}")
            return content

    def _read_artifacts(self):
        artifacts = {}
        total_bytes = 0
        for name in self.REQUIRED_FILES:
            path = self.source_dir / name
            if path.is_symlink() or not path.is_file():
                raise ValueError(f"Missing or non-regular artifact: {name}")
            content = self._read_bounded(path, self.max_total_bytes - total_bytes)
            total_bytes += len(content)
            if not content.strip():
                raise ValueError(f"Empty artifact: {name}")
            if name.endswith(".json"):
                data = json.loads(content, parse_float=_finite_json_float,
                                  parse_constant=_reject_json_constant,
                                  object_pairs_hook=_unique_json_object)
                if not isinstance(data, (dict, list)) or not data:
                    raise ValueError(f"History must be a nonempty JSON object or array: {name}")
            elif name.endswith(".bsg"):
                validate_bsg_structure(content)
            elif name.endswith(".csv"):
                rows = csv.reader(io.StringIO(content.decode("utf-8-sig")), strict=True)
                header = next(rows, [])
                if len(header) < 2:
                    raise ValueError("Trajectory requires at least two columns")
                normalized = [field.strip() for field in header]
                if any(not field for field in normalized) or len(set(normalized)) != len(header):
                    raise ValueError("Trajectory column names must be nonempty and unique")
                row_count = 0
                for row in rows:
                    row_count += 1
                    if len(row) != len(header) or any(not cell.strip() for cell in row):
                        raise ValueError("Trajectory contains incomplete rows")
                    for cell in row:
                        # Actual tracker variants may include text metadata, but
                        # nonfinite numerical telemetry is never usable evidence.
                        try:
                            value = float(cell)
                        except ValueError:
                            continue
                        if not math.isfinite(value):
                            raise ValueError("Trajectory contains nonfinite values")
                if row_count == 0:
                    raise ValueError("Trajectory requires data rows")
            else:
                content.decode("utf-8")
            artifacts[name] = content
        return artifacts

    def package(self) -> bool:
        """Check basic formats and zip original bytes, without clobbering.

        Publication is atomic on Linux filesystems supporting hard links; other
        filesystems use exclusive creation and copy the completed archive.

        Existing archives require explicit overwrite=True. Size limits are local
        resource safeguards, configurable independently of competition limits.

        These checks do not establish authenticity, machine geometry integrity,
        official telemetry compatibility, or acceptance by competition judges.
        """
        temporary = None
        try:
            output = Path(self.output_name)
            if any(output.resolve() == (self.source_dir / name).resolve() for name in self.REQUIRED_FILES):
                raise ValueError("Archive output cannot overwrite a source artifact")
            if not self.overwrite and (output.exists() or output.is_symlink()):
                raise ValueError("Archive already exists; choose a new path or set overwrite=True")
            artifacts = self._read_artifacts()
            with tempfile.NamedTemporaryFile(dir=output.parent, suffix=".zip", delete=False) as handle:
                temporary = Path(handle.name)
            with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as archive:
                for name, content in artifacts.items():
                    archive.writestr(name, content)
            if self.overwrite:
                os.replace(temporary, output)
            else:
                _publish_without_overwrite(temporary, output)
        except (OSError, ValueError, ET.ParseError, csv.Error, RecursionError) as exc:
            print(f"[ERROR] Cannot package artifacts: {exc}")
            return False
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        print(f"[SUCCESS] Packaged {len(artifacts)} artifacts into {self.output_name}; basic format checks only.")
        return True

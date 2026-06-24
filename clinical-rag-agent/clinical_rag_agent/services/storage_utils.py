"""Small filesystem helpers for the local persistence layer.

Writes are atomic (write to a temp file, then ``os.replace``) so an interrupted
write cannot leave a half-written, unparseable record, and failures are logged
loudly and re-raised rather than silently swallowed.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger("clinical_rag_agent.storage")


def write_json_atomic(path: Path, data: Any) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        os.replace(tmp_path, path)
    except OSError:
        logger.exception("Failed to write %s", path)
        tmp_path.unlink(missing_ok=True)
        raise


def append_line(path: Path, line: str) -> None:
    try:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.write("\n")
    except OSError:
        logger.exception("Failed to append to %s", path)
        raise

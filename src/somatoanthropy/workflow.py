"""Explicit local inputs for the extracted research analysis functions."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any

import numpy as np

from somatoanthropy.data.phase01_nomo import atomic_bytes, atomic_json


class RecordStore:
    """Keep licensed inputs read-only and write analyses to a separate directory.

    Source roots map experiment names to supplied frozen record folders. Their
    keys are input contracts used by the original analysis functions; they are
    never resolved against another checkout or downloaded automatically.
    """

    def __init__(
        self,
        root: str | Path,
        output: str | Path,
        sources: dict[str, str] | None = None,
        public_sources: dict[str, str] | None = None,
        input_pins: dict[str, str] | None = None,
    ) -> None:
        self.root = Path(root).resolve()
        self.private = Path(output).resolve()
        self.public = self.private / "tables"
        if self.private == self.root or self.root.is_relative_to(self.private):
            raise ValueError("OUTPUT_MUST_NOT_CONTAIN_INPUT_ROOT")
        self.sources = sources or {}
        self.public_sources = public_sources or {}
        self.input_pins = {str((self.root / k).resolve()): v for k, v in (input_pins or {}).items()}

    def pin(self, name: str | Path, expected: str | None = None) -> Path:
        path = Path(str(name).replace("\\", "/"))
        path = (self.root / path).resolve() if not path.is_absolute() else path.resolve()
        if not path.is_relative_to(self.root):
            raise ValueError("INPUT_ESCAPES_DECLARED_ROOT")
        if not path.is_file():
            raise FileNotFoundError(path.name)
        expected = expected or self.input_pins.get(str(path))
        if self.input_pins and expected is None:
            raise ValueError("UNPINNED_INPUT:" + path.name)
        if expected is not None and hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("INPUT_HASH_MISMATCH:" + path.name)
        return path

    def read(self, name: str | Path) -> Any:
        return json.loads(self.pin(name).read_text(encoding="utf-8"))

    def arrays(self, name: str | Path) -> dict[str, Any]:
        with np.load(self.pin(name), allow_pickle=False) as archive:
            return {k: archive[k] for k in archive.files}

    def source(self, experiment: str, name: str = "", public: bool = False) -> Path:
        roots = self.public_sources if public else self.sources
        if experiment not in roots:
            raise ValueError("MISSING_EXPERIMENT_SOURCE:" + experiment)
        return self.pin(Path(roots[experiment]) / name)

    def src(self, experiment: str, name: str, public: bool = False) -> Any:
        return json.loads(self.source(experiment, name, public).read_text(encoding="utf-8"))

    load_source = src

    def src_table(self, name: str) -> Any:
        return json.loads((self.public / (name + ".json")).read_text(encoding="utf-8"))

    def load(self, name: str) -> Any:
        return json.loads((self.private / name).read_text(encoding="utf-8"))

    def save(self, name: str, value: Any) -> None:
        atomic_json(self.private / name, value)

    def table(self, name: str, rows: list[dict[str, Any]], *args: Any, **kwargs: Any) -> None:
        del args, kwargs
        atomic_json(self.public / (name + ".json"), rows)
        columns = list(dict.fromkeys(k for row in rows for k in row))
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        atomic_bytes(self.public / (name + ".csv"), stream.getvalue().encode("utf-8"))

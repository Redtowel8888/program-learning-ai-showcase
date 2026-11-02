# Excerpt from Program Learning AI (src/program_learning_ai/sandbox.py), unmodified.
# Creates verified disposable copies of protected inputs. Every file is hashed,
# and the trusted manifest lives outside the folder an experiment can change.

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class SandboxFile:
    source: str
    relative_path: str
    sha256: str
    size: int


@dataclass(frozen=True, slots=True)
class SandboxManifest:
    version: int
    sandbox_id: str
    created_at: str
    status: str
    files: list[SandboxFile]
    parent_sandbox_id: str | None = None


class SandboxManager:
    """Creates verified disposable copies while treating inputs as read-only."""

    MANIFEST_NAME = "sandbox-manifest.json"

    def __init__(self, root: str | Path = "data/sandboxes"):
        self.root = Path(root).resolve()

    def create(self, sources: list[str | Path], label: str = "experiment") -> Path:
        if not sources:
            raise ValueError("At least one source path is required")
        source_paths = [Path(item).resolve(strict=True) for item in sources]
        self._validate_sources(source_paths)

        sandbox_id = f"{_safe_label(label)}-{uuid4().hex[:8]}"
        destination = (self.root / sandbox_id).resolve()
        if not destination.is_relative_to(self.root):
            raise ValueError("Sandbox destination escaped the configured root")
        destination.mkdir(parents=True, exist_ok=False)

        records: list[SandboxFile] = []
        for index, source in enumerate(source_paths, start=1):
            container = destination / "inputs" / f"{index:02d}-{_safe_label(source.name)}"
            if source.is_dir():
                for file_path in sorted(path for path in source.rglob("*") if path.is_file()):
                    relative = file_path.relative_to(source)
                    copied = container / relative
                    _copy_file(file_path, copied)
                    records.append(_record(file_path, copied.relative_to(destination)))
            else:
                copied = container / source.name
                _copy_file(source, copied)
                records.append(_record(source, copied.relative_to(destination)))

        manifest = SandboxManifest(
            version=1,
            sandbox_id=sandbox_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            status="ready",
            files=records,
        )
        _write_manifest(destination / self.MANIFEST_NAME, manifest)
        _write_manifest(self._trusted_manifest_path(sandbox_id), manifest)
        if not self.verify(destination):
            raise RuntimeError("Sandbox verification failed immediately after creation")
        return destination

    def verify(self, sandbox: str | Path) -> bool:
        sandbox_path = Path(sandbox).resolve(strict=True)
        if not sandbox_path.is_relative_to(self.root):
            raise ValueError("Refusing to verify a directory outside the sandbox root")
        manifest_path = self._trusted_manifest_path(sandbox_path.name)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest["sandbox_id"] != sandbox_path.name:
            return False
        for record in manifest["files"]:
            copied = (sandbox_path / record["relative_path"]).resolve(strict=True)
            if not copied.is_relative_to(sandbox_path):
                return False
            if copied.stat().st_size != record["size"] or _sha256(copied) != record["sha256"]:
                return False
        return True

    def derive(self, parent: str | Path, label: str = "experiment") -> Path:
        parent_path = Path(parent).resolve(strict=True)
        if not parent_path.is_relative_to(self.root):
            raise ValueError("Parent must be inside the configured sandbox root")
        if not self.verify(parent_path):
            raise ValueError("Parent sandbox does not match its protected baseline")

        sandbox_id = f"{_safe_label(label)}-{uuid4().hex[:8]}"
        destination = (self.root / sandbox_id).resolve()
        if not destination.is_relative_to(self.root):
            raise ValueError("Child destination escaped the configured root")
        destination.mkdir(parents=True, exist_ok=False)

        records: list[SandboxFile] = []
        for file_path in sorted(path for path in (parent_path / "inputs").rglob("*") if path.is_file()):
            relative = file_path.relative_to(parent_path / "inputs")
            copied = destination / "workspace" / relative
            _copy_file(file_path, copied)
            records.append(_record(file_path, copied.relative_to(destination)))

        manifest = SandboxManifest(
            version=1,
            sandbox_id=sandbox_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            status="ready",
            files=records,
            parent_sandbox_id=parent_path.name,
        )
        _write_manifest(destination / self.MANIFEST_NAME, manifest)
        _write_manifest(self._trusted_manifest_path(sandbox_id), manifest)
        if not self.verify(destination):
            raise RuntimeError("Child sandbox verification failed immediately after creation")
        return destination

    def _validate_sources(self, sources: list[Path]) -> None:
        for source in sources:
            if source == self.root or source.is_relative_to(self.root):
                raise ValueError("A sandbox or the sandbox root cannot be used as protected input")

    def _trusted_manifest_path(self, sandbox_id: str) -> Path:
        manifest_directory = self.root / ".manifests"
        manifest_directory.mkdir(parents=True, exist_ok=True)
        return manifest_directory / f"{sandbox_id}.json"


def _copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def _record(source: Path, relative_path: Path) -> SandboxFile:
    return SandboxFile(
        source=str(source),
        relative_path=relative_path.as_posix(),
        sha256=_sha256(source),
        size=source.stat().st_size,
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _safe_label(value: str) -> str:
    normalized = "".join(character.lower() if character.isalnum() else "-" for character in value)
    normalized = "-".join(part for part in normalized.split("-") if part)
    return normalized[:48] or "sandbox"


def _write_manifest(path: Path, manifest: SandboxManifest) -> None:
    data = asdict(manifest)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

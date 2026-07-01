"""Seed archive inventory helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from zipfile import ZipFile


@dataclass(frozen=True)
class SeedArchiveEntry:
    """Inventory entry for a file inside a seed archive."""

    path: str
    size: int
    category: str
    disposition: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable entry dictionary."""
        return {
            "path": self.path,
            "size": self.size,
            "category": self.category,
            "disposition": self.disposition,
        }


@dataclass(frozen=True)
class SeedArchiveInventory:
    """Inventory for one seed archive."""

    path: str
    entries: tuple[SeedArchiveEntry, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable inventory dictionary."""
        return {
            "path": self.path,
            "entries": [entry.to_dict() for entry in self.entries],
        }


def inventory_seed_archive(path: Path) -> SeedArchiveInventory:
    """Return a categorized inventory for a seed zip archive."""
    entries: list[SeedArchiveEntry] = []
    with ZipFile(path) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            category = categorize_seed_path(info.filename)
            entries.append(
                SeedArchiveEntry(
                    path=info.filename,
                    size=info.file_size,
                    category=category,
                    disposition=disposition_for_category(category),
                )
            )
    return SeedArchiveInventory(path=str(path), entries=tuple(entries))


def categorize_seed_path(path: str) -> str:
    """Categorize a seed archive path by public-safety and content type."""
    normalized = path.lower().replace("\\", "/")
    suffix = Path(normalized).suffix
    if "/data/raw/" in normalized or suffix in {".pdf", ".png", ".jpg", ".jpeg"}:
        return "raw_source_artifact"
    if suffix in {".xlsx", ".xlsm"}:
        return "workbook"
    if suffix == ".csv":
        return "schema_or_table_seed"
    if suffix in {".md", ".rst", ".txt"}:
        return "documentation"
    if suffix in {".py", ".toml", ".yml", ".yaml"}:
        return "legacy_code_or_config"
    return "other"


def disposition_for_category(category: str) -> str:
    """Return the default tracking disposition for a seed entry category."""
    if category == "raw_source_artifact":
        return "ignored_pending_review"
    if category in {"documentation", "schema_or_table_seed", "workbook"}:
        return "candidate_clean_derivative_or_already_tracked"
    if category == "legacy_code_or_config":
        return "implementation_seed_only"
    return "defer"

"""Structured validation diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class Severity(StrEnum):
    """Diagnostic severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class Diagnostic:
    """A structured validation or inspection diagnostic."""

    code: str
    message: str
    severity: Severity = Severity.ERROR
    row_number: int | None = None
    field: str | None = None
    value: str | None = None
    context: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable diagnostic dictionary."""
        data: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
        }
        if self.row_number is not None:
            data["row_number"] = self.row_number
        if self.field is not None:
            data["field"] = self.field
        if self.value is not None:
            data["value"] = self.value
        if self.context:
            data["context"] = self.context
        return data

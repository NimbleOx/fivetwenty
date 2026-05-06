"""Auditable waivers for known OANDA parity drift."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Generic, Protocol, TypeVar, cast

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_WAIVERS_PATH = REPO_ROOT / "docs_validation" / "config" / "parity-waivers.yml"


class IssueLike(Protocol):
    severity: str
    code: str
    model: str | None
    field: str | None


IssueT = TypeVar("IssueT", bound=IssueLike)


@dataclass(frozen=True)
class ParityWaiver:
    """A reviewed exception for one known parity issue."""

    code: str
    target: str
    reason: str
    source_url: str
    expires: str
    severity: str | None = None

    def expiry_date(self) -> date:
        return _parse_date(self.expires)

    def matches(self, issue: IssueLike) -> bool:
        if self.code != issue.code:
            return False
        if self.severity is not None and self.severity != issue.severity:
            return False
        return self.target == issue_target(issue)


@dataclass(frozen=True)
class WaivedIssue(Generic[IssueT]):
    issue: IssueT
    waiver: ParityWaiver


@dataclass(frozen=True)
class WaiverResult(Generic[IssueT]):
    active_issues: list[IssueT]
    waived_issues: list[WaivedIssue[IssueT]]
    unused_waivers: list[ParityWaiver]
    expired_waivers: list[ParityWaiver]


def issue_target(issue: IssueLike) -> str:
    """Return the target string used by waiver entries."""
    if issue.model is None:
        return "global"
    if issue.field is None:
        return issue.model
    return f"{issue.model}.{issue.field}"


def load_waivers(path: Path = DEFAULT_WAIVERS_PATH) -> list[ParityWaiver]:
    """Load parity waivers from YAML.

    Missing files are treated as no waivers so local validation can run before a
    waiver file exists. Malformed files fail loudly because silent suppressions
    would undermine the parity report.
    """
    if not path.exists():
        return []

    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if payload is None:
        return []
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a mapping with a 'waivers' list.")

    raw_waivers = payload.get("waivers", [])
    if not isinstance(raw_waivers, list):
        raise TypeError(f"{path} field 'waivers' must be a list.")

    waivers: list[ParityWaiver] = []
    for index, raw in enumerate(raw_waivers, start=1):
        if not isinstance(raw, dict):
            raise TypeError(f"{path} waiver #{index} must be a mapping.")
        data = cast("dict[str, Any]", raw)
        missing = [key for key in ("code", "target", "reason", "source_url", "expires") if not data.get(key)]
        if missing:
            raise ValueError(f"{path} waiver #{index} is missing required field(s): {', '.join(missing)}.")
        severity = data.get("severity")
        if severity is not None and severity not in {"P0", "P1", "P2", "P3"}:
            raise ValueError(f"{path} waiver #{index} has invalid severity {severity!r}.")

        expires = data["expires"]
        waiver = ParityWaiver(
            code=str(data["code"]),
            target=str(data["target"]),
            reason=str(data["reason"]),
            source_url=str(data["source_url"]),
            expires=expires.isoformat() if isinstance(expires, date) else str(expires),
            severity=str(severity) if severity is not None else None,
        )
        _parse_date(waiver.expires)
        waivers.append(waiver)

    return waivers


def split_waived_issues(issues: list[IssueT], waivers: list[ParityWaiver], *, today: date | None = None) -> WaiverResult[IssueT]:
    """Separate active issues from waived issues and audit stale waivers."""
    today = today or datetime.now(tz=timezone.utc).date()
    active_issues: list[IssueT] = []
    waived_issues: list[WaivedIssue[IssueT]] = []
    used_waivers: set[ParityWaiver] = set()
    expired_waivers = [waiver for waiver in waivers if waiver.expiry_date() < today]
    active_waivers = [waiver for waiver in waivers if waiver.expiry_date() >= today]

    for issue in issues:
        matching_waiver = next((waiver for waiver in active_waivers if waiver.matches(issue)), None)
        if matching_waiver is None:
            active_issues.append(issue)
            continue
        waived_issues.append(WaivedIssue(issue=issue, waiver=matching_waiver))
        used_waivers.add(matching_waiver)

    unused_waivers = [waiver for waiver in active_waivers if waiver not in used_waivers]
    return WaiverResult(
        active_issues=active_issues,
        waived_issues=waived_issues,
        unused_waivers=unused_waivers,
        expired_waivers=expired_waivers,
    )


def _parse_date(value: str) -> date:
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError(f"Expected ISO date YYYY-MM-DD, got {value!r}.")
    return parsed

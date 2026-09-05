"""Validation discovers defects and surfaces tool failures through the real engine."""

from pathlib import Path

import httpx
import pytest

from docs_validation.src import cli
from docs_validation.src.base import BaseValidator, ValidatorRegistry
from docs_validation.src.config import ValidationConfig, ValidatorConfig
from docs_validation.src.engine import ValidationEngine
from docs_validation.src.models import FileInfo
from docs_validation.src.validators.external_links import ExternalLinkValidator
from docs_validation.src.validators.security import SecurityValidator


@pytest.mark.parametrize("parallel", [False, True])
def test_document_discovery_exclusions_and_diagnostics(tmp_path, parallel):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "good.md").write_text("# Guide\n\nUse precise arithmetic.\n")
    (docs / "bad.md").write_text("# Guide\n\n```python\nprice = float('1.25')\n```\n")
    (docs / "ignored.md").write_text("```python\nprice = float('1.25')\n```\n")
    (tmp_path / "outside.md").write_text("price = float('1.25')")
    config = ValidationConfig(file_patterns=["docs/**/*.md"], exclude_patterns=["docs/ignored.md"], parallel_execution=parallel, validators={"financial_precision": ValidatorConfig(), "python_syntax": ValidatorConfig()})
    engine = ValidationEngine(config, tmp_path)
    discovered = engine.discover_files()
    assert {file.path.name for file in discovered} == {"good.md", "bad.md"}
    summary = engine.validate()
    assert summary.total_files == 2
    assert summary.failed_files == 1
    assert summary.passed_files == 1
    assert {issue.rule_id for result in summary.results for issue in result.issues} == {"financial_precision_float"}
    incremental = engine.validate_incremental([docs / "bad.md"])
    assert incremental.total_files == 1
    assert incremental.has_errors


@pytest.mark.parametrize("parallel", [False, True])
def test_validator_crashes_are_counted_as_errors_and_fail_cli(monkeypatch, tmp_path, parallel):
    class BrokenValidator(BaseValidator):
        def supports_file(self, file_path):
            return True

        def validate_file(self, file_info, content, options):
            raise RuntimeError("validator defect")

    registry = ValidatorRegistry()
    registry.register(BrokenValidator("broken", "Simulate a validator failure"))
    files = [(FileInfo(path=tmp_path / f"{name}.md", size_bytes=0, modified_time=0), "text") for name in ["a", "b"]]
    summary = registry.validate_files(files, ["broken"], {}, parallel=parallel)
    assert summary.error_count == 2
    assert summary.failed_files == 2
    assert all("validator defect" in result.issues[0].message for result in summary.results)
    monkeypatch.setattr(cli, "_generate_markdown_report", lambda summary: [])
    assert cli._display_results(summary) == 1


def test_secret_scanner_reports_and_masks_a_synthetic_token():
    token = "v20-" + "A1b2" * 10
    info = FileInfo(path=Path("credentials.md"), size_bytes=0, modified_time=0)
    result = SecurityValidator().validate_file(info, f'credential = "{token}"', {})
    assert not result.passed
    assert result.error_count == 1
    assert result.issues[0].rule_id == "security_exposed_secret"
    assert token not in result.issues[0].context
    assert "***" in result.issues[0].context
    assert SecurityValidator().validate_file(info, 'token = "your-api-token"', {}).passed


def test_external_links_deduplicate_requests_handle_head_fallback_and_ignore_code(monkeypatch):
    requests = []
    actual_client = httpx.AsyncClient

    def respond(request):
        requests.append((request.method, request.url.path))
        status = 405 if request.url.path == "/fallback" and request.method == "HEAD" else 404 if request.url.path == "/missing" else 200
        return httpx.Response(status)

    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: actual_client(**kwargs, transport=httpx.MockTransport(respond)))
    content = "[one](https://offline.test/fallback)\n[two](https://offline.test/fallback)\n[bad](https://offline.test/missing)\n[excluded](https://skip.test/page)\n```python\nurl = 'https://offline.test/code'\n```"
    info = FileInfo(path=Path("links.md"), size_bytes=0, modified_time=0)
    result = ExternalLinkValidator().validate_file(info, content, {"exclude_urls": ["https://skip.test"]})
    assert sorted(requests) == [("GET", "/fallback"), ("HEAD", "/fallback"), ("HEAD", "/missing")]
    assert [(issue.rule_id, issue.line) for issue in result.issues] == [("external_link_http_error", 3)]

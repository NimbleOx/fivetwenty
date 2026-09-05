"""Use small documents to verify actionable diagnostics and valid-code boundaries."""

import pytest

from docs_validation.src.models import FileInfo, IssueSeverity
from docs_validation.src.validators.cross_references import CrossReferenceValidator
from docs_validation.src.validators.markdown import MarkdownSyntaxValidator
from docs_validation.src.validators.sdk_methods import SDKMethodsValidator


def validate(validator, path, content):
    path.write_text(content)
    return validator.validate_file(FileInfo(path=path, size_bytes=len(content), modified_time=0), content, {})


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("#Title", {("markdown_header_space", 1, IssueSeverity.WARNING)}),
        ("# ", {("markdown_header_space", 1, IssueSeverity.WARNING), ("markdown_empty_header", 1, IssueSeverity.ERROR)}),
        ("[](url)\n[title]()\n[ ][ref]", {("markdown_empty_link_text", 1, IssueSeverity.WARNING), ("markdown_empty_link_url", 2, IssueSeverity.ERROR), ("markdown_empty_ref_link", 3, IssueSeverity.WARNING)}),
        ("- \n1. ", {("markdown_empty_list_item", 1, IssueSeverity.WARNING), ("markdown_empty_numbered_item", 2, IssueSeverity.WARNING)}),
        ("Follow these steps:\n- Start", {("markdown_list_spacing", 2, IssueSeverity.WARNING)}),
        ("```python\nprint('open')", {("markdown_unclosed_code_block", 1, IssueSeverity.ERROR)}),
        ("```\nprint('closed')\n```", {("markdown_code_block_language", 1, IssueSeverity.INFO)}),
    ],
)
def test_markdown_diagnostics_have_correct_rule_location_and_severity(tmp_path, content, expected):
    result = validate(MarkdownSyntaxValidator(), tmp_path / "guide.md", content)
    assert {(issue.rule_id, issue.line, issue.severity) for issue in result.issues} == expected


def test_markdown_ignores_syntax_examples_inside_fenced_code(tmp_path):
    content = "# Guide\n\n```text\n#Title\n[](url)\n- \n1. \n```\n\n- Valid item\n- Another item\n"
    assert validate(MarkdownSyntaxValidator(), tmp_path / "guide.md", content).passed


def test_cross_references_resolve_relative_root_and_anchor_targets(tmp_path):
    (tmp_path / "pyproject.toml").touch()
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "other.md").write_text("# Target\n")
    content = "# Guide\n\n[relative](other.md?view=1#target)\n[root](/docs/other.md#target)\n[section](#api-reference)\n[external](https://example.test/page)\n[email](mailto:test@example.test)\n\n## API Reference\n\n```text\n[example](missing.md)\n```\n"
    assert validate(CrossReferenceValidator(), docs / "guide.md", content).passed


def test_cross_references_report_missing_files_and_anchors(tmp_path):
    result = validate(CrossReferenceValidator(), tmp_path / "guide.md", "# Guide\n[file](missing.md)\n[anchor](#missing)\n[ ][]\n")
    assert {(issue.rule_id, issue.line) for issue in result.issues} == {("cross_ref_broken_link", 2), ("cross_ref_broken_anchor", 3), ("cross_ref_empty_reference", 4)}
    assert result.error_count == 1
    assert result.warning_count == 2


def test_sdk_method_discovery_checks_public_sync_and_async_calls(tmp_path):
    endpoints = tmp_path / "fivetwenty" / "endpoints"
    endpoints.mkdir(parents=True)
    (endpoints / "orders.py").write_text("class OrderEndpoints:\n    async def get_orders(self): pass\n    def cancel_order(self): pass\n    def _helper(self): pass\n")
    docs = tmp_path / "docs"
    docs.mkdir()
    validator = SDKMethodsValidator()
    path = docs / "guide.md"
    assert validate(validator, path, "client.orders.get_orders()\nclient.orders.cancel_order()\n").passed
    result = validate(validator, path, "client.orders.obsolete()\nclient.orders.obsolete()\n")
    assert [(issue.rule_id, issue.line) for issue in result.issues] == [("sdk_invalid_method_reference", 1), ("sdk_invalid_method_reference", 2)]
    reference = docs / "reference"
    reference.mkdir()
    result = validate(validator, reference / "complete-api.md", "client.orders.get_orders()\n")
    assert len(result.issues) == 1
    assert result.issues[0].rule_id == "sdk_undocumented_method"
    assert "cancel_order" in result.issues[0].message
    assert "_helper" not in result.issues[0].message


def test_sdk_discovery_includes_defined_sync_stream_adapter(tmp_path):
    endpoints = tmp_path / "fivetwenty" / "endpoints"
    endpoints.mkdir(parents=True)
    (endpoints / "pricing.py").write_text("class PricingEndpoints:\n    async def get_pricing(self): pass\n")
    (endpoints.parent / "client.py").write_text("class _SyncPricingProxy:\n    def stream_iter(self): yield 1\n")
    validator = SDKMethodsValidator()
    result = validate(validator, tmp_path / "guide.md", "client.pricing.stream_iter()\nclient.pricing.fake_stream()")
    assert [(issue.rule_id, issue.line) for issue in result.issues] == [("sdk_invalid_method_reference", 2)]


def test_external_links_ignore_literal_inline_endpoints_but_keep_real_links(tmp_path):
    from docs_validation.src.validators.external_links import ExternalLinkValidator

    path = tmp_path / "guide.md"
    content = "`https://api.example.test/v3` and ``https://literal.example.test``\n[docs](https://docs.example.test/page)\nhttps://bare.example.test/page\n"
    info = FileInfo(path=path, size_bytes=len(content), modified_time=0)
    links = ExternalLinkValidator()._extract_external_links(content, info)
    assert {link["url"] for link in links} == {"https://docs.example.test/page", "https://bare.example.test/page"}

"""Rendered Python fences must reach every code validator with accurate locations."""

import markdown
import pytest

from docs_validation.src.models import FileInfo
from docs_validation.src.validators.code_execution import CodeExecutionValidator
from docs_validation.src.validators.code_linting import CodeLintingValidator
from docs_validation.src.validators.code_typing import CodeTypingValidator
from docs_validation.src.validators.python import PythonSyntaxValidator

VALIDATORS = [CodeExecutionValidator, CodeLintingValidator, CodeTypingValidator, PythonSyntaxValidator]


def validate(validator_type, tmp_path, content):
    path = tmp_path / "example.md"
    path.write_text(content)
    return validator_type().validate_file(FileInfo(path=path, size_bytes=len(content), modified_time=0), content, {})


@pytest.mark.parametrize(
    "header",
    ['python title="example.py"', 'py linenums="1"', 'python {hl_lines="1" title="example.py"}', '{.python #example title="example.py"}', "{#example .python .extra}", '.python title="example.py"'],
)
def test_rendered_python_fence_options_do_not_bypass_execution(tmp_path, header):
    content = f'# Example\n\n```{header}\nraise RuntimeError("review probe")\n```\n'
    rendered = markdown.markdown(content, extensions=["attr_list", "pymdownx.superfences", "pymdownx.highlight"])
    assert 'class="k">raise' in rendered, "The documentation renderer must recognize this as Python"
    result = validate(CodeExecutionValidator, tmp_path, content)
    assert not result.passed
    assert result.metadata["executed_block_count"] == 1
    assert result.metadata["skipped_block_count"] == 0
    assert result.issues[0].line == 4
    assert result.issues[0].rule_id == "code_runtime_error"


@pytest.mark.parametrize("validator_type", VALIDATORS)
@pytest.mark.parametrize(("fence", "header"), [("```", 'python title="example.py"'), ("~~~~", '{.python #example title="example.py"}')])
def test_attributed_fences_reach_each_validator_with_original_line_numbers(tmp_path, validator_type, fence, header):
    content = f"# Example\n\n{fence}{header}\nvalue = 1\nif\n{fence}\n"
    result = validate(validator_type, tmp_path, content)
    assert not result.passed
    assert len(result.issues) == 1
    assert result.issues[0].line == 5
    assert result.metadata["skipped_block_count"] == 0


@pytest.mark.parametrize("validator_type", VALIDATORS)
def test_unclosed_attributed_python_fences_are_reported(tmp_path, validator_type):
    result = validate(validator_type, tmp_path, '# Example\n\n```python title="example.py"\nvalue = 1\n')
    assert not result.passed
    assert result.issues[0].rule_id.endswith("unclosed_block")
    assert result.issues[0].line == 3


@pytest.mark.parametrize("validator_type", VALIDATORS)
def test_non_python_fences_and_nested_fence_examples_are_ignored(tmp_path, validator_type):
    content = """```text title="python"
if
```

~~~{.text title=".python"}
if
~~~

````text
```python title="example.py"
if
```
````
"""
    result = validate(validator_type, tmp_path, content)
    assert result.passed, result.issues
    assert result.metadata["skipped_block_count"] == 0
    if validator_type is CodeExecutionValidator:
        assert result.metadata["executed_block_count"] == 0


@pytest.mark.parametrize("validator_type", VALIDATORS)
def test_attributed_fences_keep_explicit_skip_accounting(tmp_path, validator_type):
    content = '<!-- validation: skip -->\n```python title="example.py"\nif\n```\n'
    result = validate(validator_type, tmp_path, content)
    assert result.passed, result.issues
    assert result.metadata["skipped_block_count"] == 1
    assert result.metadata["skipped_blocks"][0]["code_start_line"] == 3


def test_indented_fences_preserve_function_indentation_and_error_lines(tmp_path):
    content = '!!! note\n\n    ```python title="example.py"\n    def fail():\n        raise RuntimeError("nested")\n    fail()\n    ```\n'
    result = validate(CodeExecutionValidator, tmp_path, content)
    assert not result.passed
    assert "RuntimeError: nested" in result.issues[0].message
    assert result.issues[0].line == 5


@pytest.mark.parametrize(
    ("validator_type", "code", "rule"),
    [(CodeLintingValidator, "missing_name()", "code_lint_f821"), (CodeTypingValidator, 'count: int = "wrong"', "code_typing_assignment")],
)
def test_real_tools_check_valid_syntax_inside_titled_fences(tmp_path, validator_type, code, rule):
    result = validate(validator_type, tmp_path, f'```python title="example.py"\n{code}\n```\n')
    assert not result.passed
    assert any(issue.rule_id == rule and issue.line == 2 for issue in result.issues), result.issues

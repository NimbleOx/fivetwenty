#!/usr/bin/env python3
"""Generate API reference documentation from docstrings."""

from pathlib import Path

# Template for each endpoint documentation page
endpoint_template = """
# {title} API

::: fivetwenty.endpoints.{module}
    options:
      show_source: true
      show_root_heading: true
      members_order: source
"""

# Template for client documentation
client_template = """
# Client API

::: fivetwenty.client
    options:
      show_source: true
      show_root_heading: true
      members_order: source
"""

# Template for models documentation
models_template = """
# Data Models

::: fivetwenty.models
    options:
      show_source: true
      show_root_heading: true
      members_order: source
      show_submodules: true
"""

# Template for exceptions documentation
exceptions_template = """
# Exceptions

::: fivetwenty.exceptions
    options:
      show_source: true
      show_root_heading: true
      members_order: source
"""


def main() -> None:
    """Generate API reference documentation."""
    api_ref_dir = Path("docs/api-reference")
    api_ref_dir.mkdir(exist_ok=True)

    # Generate client documentation
    client_doc = Path("docs/api-reference/client.md")
    client_doc.write_text(client_template.strip())
    print(f"Generated {client_doc}")

    # Generate models documentation
    models_doc = Path("docs/api-reference/models.md")
    models_doc.write_text(models_template.strip())
    print(f"Generated {models_doc}")

    # Generate exceptions documentation
    exceptions_doc = Path("docs/api-reference/exceptions.md")
    exceptions_doc.write_text(exceptions_template.strip())
    print(f"Generated {exceptions_doc}")

    # Generate documentation for each endpoint
    endpoints_dir = Path("fivetwenty/endpoints")
    if endpoints_dir.exists():
        for endpoint_file in endpoints_dir.glob("*.py"):
            if endpoint_file.stem != "__init__":
                title = endpoint_file.stem.replace("_", " ").title()
                content = endpoint_template.format(title=title, module=endpoint_file.stem).strip()

                doc_path = Path(f"docs/api-reference/{endpoint_file.stem}.md")
                doc_path.write_text(content)
                print(f"Generated {doc_path}")

    print("✅ API documentation generated!")


if __name__ == "__main__":
    main()

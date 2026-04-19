"""Test the deliverable extraction and workspace save pipeline."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from agents.api import (
    _extract_code_deliverables,
    _save_deliverables_to_workspace,
    _apply_deliverables_to_codebase,
    _find_developer_agent,
)


def test_extract_inline_filepath():
    """Test extraction from ```lang // path format."""
    text = (
        "Here is the fix:\n\n"
        "```html // src/frontend/cms-health.html\n"
        "<!DOCTYPE html>\n"
        "<html><body><h1>CMS</h1></body></html>\n"
        "```\n"
    )
    results = _extract_code_deliverables(text)
    assert len(results) == 1
    assert results[0]["path"] == "src/frontend/cms-health.html"
    assert "<!DOCTYPE html>" in results[0]["content"]
    print(f"  ✅ inline filepath: {results[0]['path']}")


def test_extract_bold_filepath():
    """Test extraction from **path** before code block."""
    text = (
        "Modified file:\n\n"
        "**src/backend/channels/foo.py**\n\n"
        "```python\n"
        "class Foo:\n"
        "    pass\n"
        "```\n"
    )
    results = _extract_code_deliverables(text)
    assert len(results) == 1
    assert results[0]["path"] == "src/backend/channels/foo.py"
    print(f"  ✅ bold filepath: {results[0]['path']}")


def test_extract_header_filepath():
    """Test extraction from ## `path` before code block."""
    text = (
        "## `src/frontend/digital-twin/main.js`\n\n"
        "```js\n"
        "const app = new App();\n"
        "app.start();\n"
        "```\n"
    )
    results = _extract_code_deliverables(text)
    assert len(results) == 1
    assert results[0]["path"] == "src/frontend/digital-twin/main.js"
    print(f"  ✅ header filepath: {results[0]['path']}")


def test_extract_multiple_files():
    """Test extraction of multiple code blocks."""
    text = (
        "Changes:\n\n"
        "```python // src/backend/main.py\n"
        "from fastapi import FastAPI\napp = FastAPI()\n"
        "```\n\n"
        "```html // src/frontend/index.html\n"
        "<html><body>Hello</body></html>\n"
        "```\n\n"
        "```css // src/frontend/style.css\n"
        "body { margin: 0; }\n"
        "```\n"
    )
    results = _extract_code_deliverables(text)
    assert len(results) == 3
    paths = [r["path"] for r in results]
    assert "src/backend/main.py" in paths
    assert "src/frontend/index.html" in paths
    assert "src/frontend/style.css" in paths
    print(f"  ✅ multiple files: {paths}")


def test_skip_shell_blocks():
    """Shell/terminal blocks without file paths should be skipped."""
    text = (
        "Run this:\n\n"
        "```bash\n"
        "pytest tests/ -q\n"
        "```\n\n"
        "Output:\n\n"
        "```\n"
        "3 passed\n"
        "```\n"
    )
    results = _extract_code_deliverables(text)
    assert len(results) == 0
    print("  ✅ shell blocks skipped")


def test_skip_path_traversal():
    """Paths with .. should be rejected."""
    text = (
        "```python // ../../etc/passwd\n"
        "malicious content\n"
        "```\n"
    )
    results = _extract_code_deliverables(text)
    assert len(results) == 0
    print("  ✅ path traversal rejected")


def test_strip_project_root():
    """Absolute project paths should be normalized."""
    text = (
        "```python // /Users/panglaohu/Downloads/DoubleBoatClawSystem/src/backend/foo.py\n"
        "class Foo: pass\n"
        "```\n"
    )
    results = _extract_code_deliverables(text)
    assert len(results) == 1
    assert results[0]["path"] == "src/backend/foo.py"
    print(f"  ✅ path normalized: {results[0]['path']}")


def test_find_developer_agent():
    """Test finding developer agent from workflow."""
    wf = [
        {"key": "pm_decompose", "agent_id": "pm-1", "agent_role": "project_manager"},
        {"key": "develop", "agent_id": "dev-1", "agent_role": "developer"},
        {"key": "deploy", "agent_id": "ops-1", "agent_role": "devops"},
    ]
    assert _find_developer_agent("team1", wf) == "dev-1"
    assert _find_developer_agent("team1", [{"key": "test", "agent_id": "qa-1"}]) == ""
    print("  ✅ find_developer_agent works")


if __name__ == "__main__":
    print("Testing deliverable extraction pipeline...")
    test_extract_inline_filepath()
    test_extract_bold_filepath()
    test_extract_header_filepath()
    test_extract_multiple_files()
    test_skip_shell_blocks()
    test_skip_path_traversal()
    test_strip_project_root()
    test_find_developer_agent()
    print("\n✅ All tests passed!")

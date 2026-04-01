"""tests/unit/test_html_structure.py — 前端 HTML 文件结构正确性测试

验证 src/frontend/ 下所有 HTML 文件的基本结构:
- DOCTYPE 在文件开头
- 闭合标签完整
- 无 script 出现在 DOCTYPE 之前
- charset 声明存在
"""

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "src" / "frontend"


def _collect_html_files():
    """收集 src/frontend/ 下所有 .html 文件."""
    files = sorted(FRONTEND_DIR.rglob("*.html"))
    assert files, f"No HTML files found in {FRONTEND_DIR}"
    return files


def _html_ids():
    """为 parametrize 生成可读的测试 ID."""
    return [str(f.relative_to(PROJECT_ROOT)) for f in _collect_html_files()]


HTML_FILES = _collect_html_files()


@pytest.mark.parametrize("html_file", HTML_FILES, ids=_html_ids())
class TestHtmlStructure:
    """每个 HTML 文件独立运行的结构验证."""

    def test_starts_with_doctype(self, html_file: Path):
        """文件实际内容（忽略开头空行/空白）以 <!DOCTYPE 开头."""
        content = html_file.read_text(encoding="utf-8")
        stripped = content.lstrip()
        assert stripped.upper().startswith("<!DOCTYPE"), (
            f"{html_file.name}: 内容不以 <!DOCTYPE 开头, "
            f"实际开头: {stripped[:80]!r}"
        )

    def test_has_closing_tags(self, html_file: Path):
        """包含 </html> 和 </body> 闭合标签."""
        content = html_file.read_text(encoding="utf-8").lower()
        assert "</html>" in content, f"{html_file.name}: 缺少 </html>"
        assert "</body>" in content, f"{html_file.name}: 缺少 </body>"

    def test_no_script_before_doctype(self, html_file: Path):
        """<script 标签不出现在 <!DOCTYPE 之前."""
        content = html_file.read_text(encoding="utf-8")
        stripped = content.lstrip()
        upper = stripped.upper()
        doctype_pos = upper.find("<!DOCTYPE")
        if doctype_pos == -1:
            pytest.skip("无 DOCTYPE 声明 (由其他用例覆盖)")
        before_doctype = upper[:doctype_pos]
        assert "<SCRIPT" not in before_doctype, (
            f"{html_file.name}: <script 出现在 <!DOCTYPE 之前"
        )

    def test_has_charset(self, html_file: Path):
        """包含 charset 声明."""
        content = html_file.read_text(encoding="utf-8").lower()
        assert "charset" in content, (
            f"{html_file.name}: 缺少 charset 声明"
        )


class TestWorldmonitorArCasPro:
    """专门验证 worldmonitor-ar-cas-pro.html 的结构."""

    TARGET = FRONTEND_DIR / "worldmonitor-ar-cas-pro.html"

    def test_no_misplaced_doctype(self):
        """<!DOCTYPE html> 只出现一次，且在第一个非空行."""
        content = self.TARGET.read_text(encoding="utf-8")

        # 只出现一次
        count = len(re.findall(r"<!DOCTYPE\s+html>", content, re.IGNORECASE))
        assert count == 1, (
            f"<!DOCTYPE html> 出现 {count} 次，预期 1 次"
        )

        # 在第一个非空行
        for line in content.splitlines():
            if line.strip():
                assert line.strip().upper().startswith("<!DOCTYPE"), (
                    f"第一个非空行不是 DOCTYPE: {line.strip()!r}"
                )
                break


class TestDigitalTwinCaptainCockpitBindings:
    """验证数字孪生页面的嵌入式 Captain Cockpit 关键节点被脚本绑定."""

    TARGET = FRONTEND_DIR / "digital-twin.html"

    def test_captain_cockpit_ids_exist_and_are_bound(self):
        content = self.TARGET.read_text(encoding="utf-8")
        required_ids = [
            "captain-loop-state",
            "captain-runs",
            "captain-last-cycle",
            "captain-memory-availability",
            "captain-decision-summary",
            "cockpit-risk-level",
            "cockpit-compliance-status",
            "cockpit-event-count",
            "cockpit-action-count",
            "cockpit-captain-cycle",
            "cockpit-memory-store",
            "cockpit-cloud-sync",
            "cockpit-analytics-state",
            "cockpit-fusion-count",
            "cockpit-task-nodes",
            "cockpit-scene-type",
            "cockpit-summary-text",
            "cockpit-last-sync",
        ]

        for node_id in required_ids:
            assert f'id="{node_id}"' in content, f"digital-twin.html: 缺少 DOM 节点 {node_id}"
            assert f"setTextContent('{node_id}'" in content, (
                f"digital-twin.html: 缺少 {node_id} 的脚本赋值绑定"
            )

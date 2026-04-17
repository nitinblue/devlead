"""Tests for src/devlead/render.py — markdown → HTML for devlead_docs/.

FEATURES-0024. Verifies the markdown subset renders correctly + the directory
walk produces files for each MD plus an index page.
"""
from __future__ import annotations

from pathlib import Path

from devlead.render import (
    VIEWS_DIRNAME,
    render_dir,
    render_md_to_full_html,
    render_md_to_html,
)


# --- inline transforms ----------------------------------------------------

def test_renders_paragraph():
    out = render_md_to_html("a single paragraph here.")
    assert "<p>a single paragraph here.</p>" in out


def test_renders_bold():
    out = render_md_to_html("This is **bold** text.")
    assert "<strong>bold</strong>" in out


def test_renders_italic_star():
    out = render_md_to_html("This is *italic* text.")
    assert "<em>italic</em>" in out


def test_renders_inline_code():
    out = render_md_to_html("Run `pip install devlead` to get started.")
    assert "<code>pip install devlead</code>" in out


def test_renders_link():
    out = render_md_to_html("See [the docs](https://example.com) for more.")
    assert '<a href="https://example.com">the docs</a>' in out


def test_escapes_html_in_text():
    out = render_md_to_html("Use <script> tags carefully.")
    # Should escape the <script> so it doesn't execute
    assert "<script>" not in out
    assert "&lt;script&gt;" in out


# --- block-level ---------------------------------------------------------

def test_renders_h1_through_h4():
    out = render_md_to_html("# H1\n\n## H2\n\n### H3\n\n#### H4")
    for n in (1, 2, 3, 4):
        assert f"<h{n}>" in out


def test_renders_unordered_list():
    out = render_md_to_html("- one\n- two\n- three")
    assert "<ul>" in out
    assert "<li>one</li>" in out
    assert "<li>two</li>" in out


def test_renders_ordered_list():
    out = render_md_to_html("1. first\n2. second")
    assert "<ol>" in out
    assert "<li>first</li>" in out


def test_renders_nested_list():
    out = render_md_to_html("- parent\n  - child\n  - child2\n- sibling")
    assert "<ul>" in out
    assert "<li>parent" in out
    # Nested ul should be inside the parent li
    parent_idx = out.find("<li>parent")
    nested_idx = out.find("<ul>", parent_idx + 1)
    assert nested_idx > parent_idx


def test_renders_code_block():
    out = render_md_to_html("```\nprint('hello')\n```")
    assert "<pre>" in out
    assert "print" in out


def test_renders_blockquote():
    out = render_md_to_html("> This is a quote\n> across two lines")
    assert "<blockquote>" in out
    assert "across two lines" in out


def test_renders_horizontal_rule():
    out = render_md_to_html("text above\n\n---\n\ntext below")
    assert "<hr>" in out


def test_preserves_html_comments():
    """SOT blocks live inside HTML comments and must survive verbatim."""
    md = "<!-- devlead:sot\n  purpose: \"foo\"\n-->\n\n## Heading"
    out = render_md_to_html(md)
    assert "<!-- devlead:sot" in out
    assert "purpose: \"foo\"" in out


# --- full-page wrapper --------------------------------------------------

def test_full_html_includes_doctype_and_styles():
    out = render_md_to_full_html("# Hello", title="Test page")
    assert "<!doctype html>" in out
    assert "<title>Test page</title>" in out
    assert "<style>" in out
    assert "<h1>Hello</h1>" in out


def test_full_html_escapes_title():
    out = render_md_to_full_html("# x", title="Test <script>")
    assert "<title>Test <script></title>" not in out
    assert "&lt;script&gt;" in out


# --- directory walk -----------------------------------------------------

def test_render_dir_writes_html_per_md(tmp_path: Path):
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    (docs / "_resume.md").write_text("# Resume\n\nbody", encoding="utf-8")
    (docs / "_intake_features.md").write_text("# Intake\n\n- item", encoding="utf-8")
    out_dir = tmp_path / "out"
    rendered = render_dir(docs, out_dir)
    assert "_resume.md" in rendered
    assert "_intake_features.md" in rendered
    assert (out_dir / "_resume.html").exists()
    assert (out_dir / "_intake_features.html").exists()


def test_render_dir_creates_index(tmp_path: Path):
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    (docs / "_resume.md").write_text("# R\n", encoding="utf-8")
    (docs / "_intake_bugs.md").write_text("# B\n", encoding="utf-8")
    out_dir = tmp_path / "out"
    render_dir(docs, out_dir)
    index = out_dir / "index.html"
    assert index.exists()
    text = index.read_text(encoding="utf-8")
    assert "_resume.md" in text
    assert "_intake_bugs.md" in text
    assert 'href="_resume.html"' in text


def test_render_dir_default_out_dir(tmp_path: Path):
    """Default out_dir is `<docs_dir>/../docs/views/`."""
    repo = tmp_path
    docs = repo / "devlead_docs"
    docs.mkdir()
    (docs / "_resume.md").write_text("# x", encoding="utf-8")
    rendered = render_dir(docs)
    expected_out = repo / "docs" / VIEWS_DIRNAME / "_resume.html"
    assert expected_out.exists()
    assert "_resume.md" in rendered


def test_render_dir_handles_empty_docs(tmp_path: Path):
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    out_dir = tmp_path / "out"
    rendered = render_dir(docs, out_dir)
    assert rendered == {}
    # Index still produced
    assert (out_dir / "index.html").exists()


def test_render_dir_skips_intake_templates(tmp_path: Path):
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    (docs / "_intake_templates_default.md").write_text("# template", encoding="utf-8")
    (docs / "_resume.md").write_text("# r", encoding="utf-8")
    out_dir = tmp_path / "out"
    rendered = render_dir(docs, out_dir)
    assert "_resume.md" in rendered
    assert "_intake_templates_default.md" not in rendered


def test_render_live_devlead_docs_does_not_crash():
    """Smoke: render this repo's actual devlead_docs/ end-to-end."""
    docs = Path(__file__).resolve().parents[1] / "devlead_docs"
    if not docs.exists():
        import pytest
        pytest.skip("live devlead_docs/ not present")
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "views"
        rendered = render_dir(docs, out)
        # At least the canonical files should render
        assert "_resume.md" in rendered
        assert "_project_hierarchy.md" in rendered
        assert (out / "_resume.html").exists()
        assert (out / "index.html").exists()
        # Index should mention every rendered file
        index_text = (out / "index.html").read_text(encoding="utf-8")
        for name in rendered:
            assert name in index_text

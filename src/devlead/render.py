"""Markdown → HTML renderer for devlead_docs/ files.

FEATURES-0024 — foundation of the MD↔HTML loop. Every `devlead_docs/*.md`
gets a rendered HTML view at `docs/views/<filename>.html`. Stdlib only;
no external markdown parser dependency.

Supported markdown subset (covers ~95% of devlead_docs/ content):
  - Headings (#, ##, ###, ####, h1..h4)
  - Paragraphs (blank-line separated)
  - Bullet lists (- prefix; nesting by indentation)
  - Ordered lists (1., 2.)
  - Inline code (`code`)
  - Bold (**text**)
  - Italic (*text* or _text_)
  - Code blocks (``` fences)
  - Links ([text](url))
  - Blockquotes (>)
  - Horizontal rules (---)
  - HTML comments preserved (so SOT blocks survive)

Not supported (intentional — keeps stdlib renderer simple):
  - Tables (already rich in dashboard tabs)
  - Inline HTML other than comments
  - Footnotes, task-list checkboxes (rendered as plain text)

The richer per-file-type views (intake cards, hierarchy tree, etc.) are
FEATURES-0028+, layered on top of this base renderer.
"""
from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from pathlib import Path

VIEWS_DIRNAME = "views"


# --- inline markdown ------------------------------------------------------

_INLINE_CODE_RE = re.compile(r"`([^`]+)`")
_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC_STAR_RE = re.compile(r"(?<![*])\*([^*\s][^*]*?)\*(?![*])")
_ITALIC_UNDERSCORE_RE = re.compile(r"(?<![\w_])_([^_\s][^_]*?)_(?![\w_])")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _inline(text: str) -> str:
    """Apply inline markdown transforms after escaping HTML."""
    out = html.escape(text, quote=False)
    # Order matters: code first (so its contents aren't transformed), then bold/italic, then links.
    out = _INLINE_CODE_RE.sub(r"<code>\1</code>", out)
    out = _BOLD_RE.sub(r"<strong>\1</strong>", out)
    out = _ITALIC_STAR_RE.sub(r"<em>\1</em>", out)
    out = _ITALIC_UNDERSCORE_RE.sub(r"<em>\1</em>", out)
    out = _LINK_RE.sub(r'<a href="\2">\1</a>', out)
    return out


# --- block-level renderer -------------------------------------------------

def render_md_to_html(md: str) -> str:
    """Convert a markdown string to an HTML body fragment.

    Returns the inner HTML — no <html>/<head>/<body> wrapper.
    Use `render_md_to_full_html()` for a complete page.
    """
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # HTML comments — emit verbatim (preserve SOT blocks etc.)
        if stripped.startswith("<!--"):
            block = []
            while i < n:
                block.append(lines[i])
                if "-->" in lines[i]:
                    i += 1
                    break
                i += 1
            out.append("\n".join(block))
            continue

        # Code fence ``` ... ```
        if stripped.startswith("```"):
            i += 1
            block: list[str] = []
            while i < n and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            out.append("<pre>" + html.escape("\n".join(block), quote=False) + "</pre>")
            continue

        # Horizontal rule
        if stripped in ("---", "***", "___"):
            out.append("<hr>")
            i += 1
            continue

        # Headings
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # Bullet list (-)
        if re.match(r"^\s*-\s+", line):
            list_lines: list[tuple[int, str]] = []
            while i < n and re.match(r"^\s*-\s+", lines[i]):
                m = re.match(r"^(\s*)-\s+(.*)$", lines[i])
                indent = len(m.group(1))
                list_lines.append((indent, m.group(2)))
                i += 1
            out.append(_render_list(list_lines, ordered=False))
            continue

        # Ordered list (1. 2. ...)
        if re.match(r"^\s*\d+\.\s+", line):
            list_lines = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                m = re.match(r"^(\s*)\d+\.\s+(.*)$", lines[i])
                indent = len(m.group(1))
                list_lines.append((indent, m.group(2)))
                i += 1
            out.append(_render_list(list_lines, ordered=True))
            continue

        # Blockquote
        if stripped.startswith(">"):
            quote_lines: list[str] = []
            while i < n and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip()[1:].strip())
                i += 1
            out.append("<blockquote>" + _inline(" ".join(quote_lines)) + "</blockquote>")
            continue

        # Blank line
        if not stripped:
            i += 1
            continue

        # Paragraph: gather contiguous non-blank lines that aren't another block
        para: list[str] = []
        while i < n:
            cur = lines[i]
            cur_stripped = cur.strip()
            if not cur_stripped:
                break
            if cur_stripped.startswith(("#", "```", ">", "<!--", "---", "***", "___")):
                break
            if re.match(r"^\s*-\s+", cur) or re.match(r"^\s*\d+\.\s+", cur):
                break
            para.append(cur_stripped)
            i += 1
        if para:
            out.append("<p>" + _inline(" ".join(para)) + "</p>")

    return "\n".join(out)


def _render_list(items: list[tuple[int, str]], ordered: bool) -> str:
    """Render a (possibly nested) list. Indent levels in items are pixel-counts of leading whitespace."""
    tag = "ol" if ordered else "ul"
    if not items:
        return ""
    base_indent = items[0][0]
    out = [f"<{tag}>"]
    i = 0
    while i < len(items):
        indent, text = items[i]
        if indent == base_indent:
            # Look ahead: if next item is more indented, it's a nested list
            sub: list[tuple[int, str]] = []
            j = i + 1
            while j < len(items) and items[j][0] > indent:
                sub.append(items[j])
                j += 1
            if sub:
                out.append(f"<li>{_inline(text)}\n{_render_list(sub, ordered)}</li>")
            else:
                out.append(f"<li>{_inline(text)}</li>")
            i = j
        else:
            i += 1
    out.append(f"</{tag}>")
    return "\n".join(out)


# --- page wrapper ---------------------------------------------------------

_PAGE_CSS = """
:root {
  --bg: #0b0d10; --panel: #11151a; --line: #222a33;
  --ink: #e6edf3; --ink-dim: #9aa7b3; --ink-faint: #6b7785;
  --accent: #7ee787; --accent-2: #79c0ff;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: var(--bg); color: var(--ink);
  font: 15px/1.55 ui-sans-serif, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
body { padding: 30px 40px; max-width: 960px; margin: 0 auto; }
a { color: var(--accent-2); text-decoration: none; }
a:hover { text-decoration: underline; }
code { font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace; font-size: 13px;
  background: #0a0d11; padding: 1px 5px; border-radius: 4px; border: 1px solid var(--line); }
pre { background: #0a0d11; border: 1px solid var(--line); border-radius: 6px;
  padding: 12px 14px; overflow-x: auto; font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  font-size: 13px; line-height: 1.5; }
pre code { background: transparent; border: 0; padding: 0; }
h1, h2, h3, h4 { letter-spacing: -0.01em; margin-top: 1.4em; margin-bottom: 0.4em; }
h1 { font-size: 28px; border-bottom: 1px solid var(--line); padding-bottom: 8px; }
h2 { font-size: 22px; }
h3 { font-size: 17px; color: var(--ink); }
h4 { font-size: 14px; color: var(--ink-dim); text-transform: uppercase; letter-spacing: 0.06em; }
p { margin: 8px 0; }
ul, ol { padding-left: 24px; }
li { margin: 3px 0; }
blockquote { border-left: 3px solid var(--accent-2); margin: 14px 0; padding: 6px 14px;
  color: var(--ink-dim); background: #10161c; border-radius: 0 6px 6px 0; }
hr { border: 0; border-top: 1px solid var(--line); margin: 22px 0; }
.footer { margin-top: 48px; padding-top: 16px; border-top: 1px solid var(--line);
  color: var(--ink-faint); font-size: 12px; }
.footer a { color: var(--ink-faint); }
"""


def render_md_to_full_html(md: str, title: str = "DevLead document") -> str:
    """Wrap the rendered body in a full HTML page with dashboard styling."""
    body = render_md_to_html(md)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{_PAGE_CSS}</style>
</head>
<body>
{body}
<div class="footer">Auto-generated by <code>devlead render</code> on {now} · <a href="index.html">← back to index</a></div>
</body>
</html>
"""


# --- multi-file render --------------------------------------------------

def render_dir(docs_dir: Path, out_dir: Path | None = None) -> dict[str, Path]:
    """Render every `*.md` file in docs_dir to HTML in out_dir.

    Returns {source_filename: rendered_path}. Also generates index.html.
    Default out_dir is `<docs_dir>/../docs/views/`.
    """
    docs_dir = Path(docs_dir)
    if out_dir is None:
        out_dir = docs_dir.parent / "docs" / VIEWS_DIRNAME
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rendered: dict[str, Path] = {}
    for md_path in sorted(docs_dir.glob("*.md")):
        if md_path.name.startswith("_intake_templates"):
            continue
        try:
            text = md_path.read_text(encoding="utf-8")
        except Exception:
            continue
        title = md_path.stem.lstrip("_").replace("_", " ").title()
        html_str = render_md_to_full_html(text, title=title)
        out_path = out_dir / (md_path.stem + ".html")
        out_path.write_text(html_str, encoding="utf-8")
        rendered[md_path.name] = out_path

    # Index page
    index_html = _render_index(rendered, docs_dir)
    (out_dir / "index.html").write_text(index_html, encoding="utf-8")
    return rendered


def _render_index(rendered: dict[str, Path], docs_dir: Path) -> str:
    """One-page index linking to every rendered file with metadata."""
    rows: list[str] = []
    for name in sorted(rendered.keys()):
        src = docs_dir / name
        try:
            line_count = sum(1 for _ in src.open("r", encoding="utf-8"))
        except Exception:
            line_count = 0
        rows.append(
            f'<tr><td><a href="{html.escape(rendered[name].name)}">{html.escape(name)}</a></td>'
            f'<td>{line_count}</td></tr>'
        )
    table = (
        "<table><thead><tr><th>File</th><th>Lines</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )
    body = f"<h1>devlead_docs/ index</h1>\n<p>Rendered views of every Markdown file in this DevLead project.</p>\n{table}"
    css = _PAGE_CSS + """
table { width: 100%; border-collapse: collapse; margin-top: 14px; font-size: 14px; }
th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); }
th { color: var(--ink-dim); font-weight: 600; font-size: 13px; }
"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>devlead_docs/ index</title>
<style>{css}</style>
</head>
<body>
{body}
<div class="footer">Auto-generated by <code>devlead render</code> on {now}</div>
</body>
</html>
"""

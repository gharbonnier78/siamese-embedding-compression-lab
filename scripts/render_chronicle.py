"""Render append-only Chronicle YAML into deterministic human-readable Markdown/LaTeX.

The YAML files remain authoritative. This renderer is navigation/review only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

BANNER = "Generated view. The append-only structured Chronicle is authoritative."


def _flatten(value: Any, prefix: str = "") -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key in sorted(value):
            child = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(_flatten(value[key], child))
    elif isinstance(value, list):
        rows.append((prefix, json.dumps(value, ensure_ascii=False, sort_keys=True)))
    else:
        rows.append((prefix, "null" if value is None else str(value)))
    return rows


def _escape_tex(text: str) -> str:
    repl = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(repl.get(ch, ch) for ch in text)


def _load(source: Path) -> list[tuple[Path, dict[str, Any]]]:
    entries: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(source.glob("*.yaml"), key=lambda p: p.name):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise TypeError(f"{path}: top-level Chronicle entry must be a mapping")
        entries.append((path, data))
    return entries


def render_markdown(entries: list[tuple[Path, dict[str, Any]]]) -> str:
    out = ["# Study Chronicle", "", f"> **{BANNER}**", "", "Ordering rule: lexical order of Chronicle source filenames.", ""]
    for index, (path, data) in enumerate(entries, 1):
        title = data.get("entry_type") or data.get("analysis_id") or data.get("study_id") or path.stem
        out += [f"## {index}. {title}", "", f"**Source:** `{path.as_posix()}`", ""]
        for key, value in _flatten(data):
            out.append(f"- **{key}:** `{value}`")
        out.append("")
    return "\n".join(out) + "\n"


def render_tex(entries: list[tuple[Path, dict[str, Any]]]) -> str:
    body = []
    for index, (path, data) in enumerate(entries, 1):
        title = str(data.get("entry_type") or data.get("analysis_id") or data.get("study_id") or path.stem)
        body += [rf"\section*{{{index}. {_escape_tex(title)}}}", rf"\textbf{{Source:}} \texttt{{{_escape_tex(path.as_posix())}}}", r"\begin{itemize}"]
        for key, value in _flatten(data):
            body.append(rf"\item \textbf{{{_escape_tex(key)}:}} \texttt{{{_escape_tex(value)}}}")
        body += [r"\end{itemize}"]
    return "\n".join([
        r"\documentclass[10pt,a4paper]{article}",
        r"\usepackage[margin=1.8cm]{geometry}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage{lmodern}",
        r"\usepackage{microtype}",
        r"\usepackage[hidelinks]{hyperref}",
        r"\setlength{\parindent}{0pt}",
        r"\begin{document}",
        r"\begin{center}\LARGE Study Chronicle\\[4pt]\normalsize " + _escape_tex(BANNER) + r"\end{center}",
        r"\vspace{1em}\textit{Ordering rule: lexical order of Chronicle source filenames.}",
        *body,
        r"\end{document}",
        "",
    ])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("protocol/chronicle"))
    parser.add_argument("--out-dir", type=Path, default=Path("artifacts/chronicle"))
    args = parser.parse_args()
    entries = _load(args.source)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "Chronicle.md").write_text(render_markdown(entries), encoding="utf-8")
    (args.out_dir / "Chronicle.tex").write_text(render_tex(entries), encoding="utf-8")
    print(json.dumps({"entries": len(entries), "markdown": str(args.out_dir / "Chronicle.md"), "latex": str(args.out_dir / "Chronicle.tex")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

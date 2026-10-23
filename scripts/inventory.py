#!/usr/bin/env python3
"""Read-only local SKILL.md inventory. Python 3.11+, standard library only.

This is lexical candidate retrieval, not a skill executor or host registry.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tomllib

MAX_HEADER = 65536
MAX_DIRS = 10000
MAX_MANIFESTS = 5000
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}
FIELDS = {"name", "description"}


def canonical(path: Path) -> str:
    return os.path.normcase(str(path.resolve()))


def read_header(path: Path) -> list[str]:
    """Stop at the closing frontmatter delimiter; do not read the skill body."""
    with path.open("r", encoding="utf-8-sig", newline=None) as stream:
        first = stream.readline(MAX_HEADER + 1)
        if first.strip() != "---":
            raise ValueError("missing YAML frontmatter")
        size = len(first)
        lines = []
        while size <= MAX_HEADER:
            line = stream.readline(MAX_HEADER + 1 - size)
            if not line:
                break
            size += len(line)
            if line.strip() in {"---", "..."}:
                return lines
            lines.append(line.rstrip("\r\n"))
    raise ValueError("unclosed or oversized frontmatter")


def scalar(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if value.startswith('"'):
        # JSON string syntax is a safe subset of common YAML double quotes.
        parsed, end = json.JSONDecoder().raw_decode(value)
        if not isinstance(parsed, str) or (value[end:].strip() and not value[end:].lstrip().startswith("#")):
            raise ValueError("unsupported quoted scalar")
        return parsed
    if value.startswith("'"):
        match = re.fullmatch(r"'((?:[^']|'')*)'\s*(?:#.*)?", value)
        if not match:
            raise ValueError("unsupported single-quoted scalar")
        return match.group(1).replace("''", "'")
    if value[0] in "&*!{[|>":
        raise ValueError("unsupported YAML construct; inspect metadata with host tools")
    value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
    if value.lower() in {"null", "~", "true", "false"} or re.fullmatch(r"[+-]?\d+(?:\.\d+)?", value):
        raise ValueError("name/description must be strings")
    return value


def metadata(path: Path) -> dict[str, str]:
    """Parse common string fields, including folded/literal/continued values.

    Deliberately rejects complex YAML rather than silently inventing metadata.
    """
    lines = read_header(path)
    result = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        index += 1
        match = re.match(r"^(name|description):\s*(.*)$", line)
        if not match:
            continue
        key, raw = match.groups()
        if key in result:
            raise ValueError(f"duplicate {key} field")
        continuation = []
        while index < len(lines) and (not lines[index].strip() or lines[index][0].isspace()):
            continuation.append(lines[index])
            index += 1
        block = re.fullmatch(r"([>|])[-+]?\s*(?:#.*)?", raw)
        if block:
            joiner = " " if block.group(1) == ">" else "\n"
            value = joiner.join(part.strip() for part in continuation).strip()
        else:
            combined = " ".join([raw, *(part.strip() for part in continuation)]).strip()
            value = scalar(combined)
        if not value:
            raise ValueError(f"empty {key} field")
        result[key] = value
    if set(result) != FIELDS:
        raise ValueError("missing name or description string")
    return result


def project_levels(cwd: Path) -> list[Path]:
    cwd = cwd.resolve()
    levels = [cwd, *cwd.parents]
    for index, level in enumerate(levels):
        if (level / ".git").exists():
            return levels[: index + 1]
    return [cwd]


def default_roots(agent: str, cwd: Path, home: Path, codex_home: Path) -> list[Path]:
    levels = project_levels(cwd)
    roots = [home / ".agents" / "skills"]
    roots += [level / ".agents" / "skills" for level in levels]
    if agent in {"codex", "all"}:
        roots += [codex_home / "skills"]
        roots += [level / ".codex" / "skills" for level in levels]
        if os.name != "nt":
            roots += [Path("/etc/codex/skills")]
    for target in ("claude", "gemini"):
        if agent in {target, "all"}:
            roots += [home / f".{target}" / "skills"]
            roots += [level / f".{target}" / "skills" for level in levels]
    return roots


def disabled_paths(config: Path, warnings: list[dict]) -> set[str]:
    if not config.exists():
        return set()
    try:
        data = tomllib.loads(config.read_text(encoding="utf-8-sig"))
        entries = data.get("skills", {}).get("config", [])
        if not isinstance(entries, list):
            raise ValueError("skills.config must be an array")
        disabled = set()
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("enabled") is not False:
                continue
            raw = entry.get("path")
            if not isinstance(raw, str):
                raise ValueError("disabled skill has no string path")
            path = Path(raw).expanduser()
            if not path.is_absolute():
                warnings.append({"path": str(config), "reason": "relative disabled path cannot be resolved reliably"})
                continue
            disabled.add(canonical(path))
        return disabled
    except (OSError, UnicodeError, ValueError, TypeError, AttributeError):
        warnings.append({"path": str(config), "reason": "cannot parse disable settings; verify with host"})
        return set()


def tokenize(text: str) -> set[str]:
    terms = set()
    for part in re.findall(r"[a-z0-9]+|[\u3400-\u9fff]+", text.lower()):
        if re.fullmatch(r"[a-z0-9]+", part):
            terms.add(part)
        elif len(part) == 1:
            terms.add(part)
        else:
            terms.update(part[index : index + 2] for index in range(len(part) - 1))
    return terms


def retrieve(skills: list[dict], query: str, top: int) -> list[dict]:
    query_terms = tokenize(query)
    documents = [tokenize(skill["name"] + " " + skill["description"]) for skill in skills]
    frequency = {term: sum(term in document for document in documents) for term in query_terms}
    ranked = []
    for skill, document in zip(skills, documents):
        overlap = query_terms & document
        if not overlap:
            continue
        names = tokenize(skill["name"])
        score = sum((2 if term in names else 1) * (1 + math.log((len(skills) + 1) / (frequency[term] + 1))) for term in overlap)
        ranked.append({**skill, "lexical_score": round(score, 4)})
    return sorted(ranked, key=lambda item: (-item["lexical_score"], item["name"].casefold(), item["path"]))[:top]


def inventory(roots: list[Path], disabled: set[str] | None = None, max_dirs: int = MAX_DIRS, max_manifests: int = MAX_MANIFESTS) -> dict:
    disabled = disabled or set()
    skills, warnings, checked = [], [], []
    seen_dirs, seen_files, seen_roots = set(), set(), set()
    excluded_disabled = excluded_self = 0
    exhausted = False
    for root in roots:
        root = root.expanduser().absolute()
        try:
            root_key = canonical(root)
        except (OSError, RuntimeError):
            warnings.append({"path": str(root), "reason": "cannot resolve root"})
            continue
        if root_key in seen_roots:
            continue
        seen_roots.add(root_key)
        if not root.exists():
            continue
        checked.append(str(root))
        stack = [root]
        while stack:
            directory = stack.pop()
            try:
                key = canonical(directory)
                if key in seen_dirs:
                    continue
                if len(seen_dirs) >= max_dirs:
                    exhausted = True
                    break
                seen_dirs.add(key)
                entries = sorted(directory.iterdir(), key=lambda p: p.name.casefold())
                manifests = [p for p in entries if p.name.casefold() == "skill.md" and p.is_file()]
                if manifests:
                    # A skill's references/assets may contain examples; do not recurse there.
                    for path in manifests:
                        file_key = canonical(path)
                        if file_key in seen_files:
                            continue
                        if len(seen_files) >= max_manifests:
                            exhausted = True
                            break
                        seen_files.add(file_key)
                        if file_key in disabled or canonical(path.parent) in disabled:
                            excluded_disabled += 1
                            continue
                        try:
                            fields = metadata(path)
                            if fields["name"] == "skill-selector":
                                excluded_self += 1
                                continue
                            skills.append({
                                "id": hashlib.sha256(file_key.encode("utf-8")).hexdigest()[:16],
                                **fields,
                                "path": str(path.resolve()),
                                "source_root": str(root),
                                "availability": "disk_only",
                            })
                        except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
                            warnings.append({"path": str(path), "reason": str(exc)})
                    if exhausted:
                        break
                else:
                    stack.extend(reversed([p for p in entries if p.name not in SKIP_DIRS and p.is_dir()]))
            except (OSError, RuntimeError) as exc:
                warnings.append({"path": str(directory), "reason": type(exc).__name__})
        if exhausted:
            warnings.append({"path": str(root), "reason": "scan limit reached; inventory is incomplete"})
            break
    return {
        "schema_version": 1,
        "availability_note": "Disk inventory only. Verify host enablement and dependencies before recommending execution.",
        "checked_roots": checked,
        "excluded_disabled": excluded_disabled,
        "excluded_self": excluded_self,
        "total_skills": len(skills),
        "skills": sorted(skills, key=lambda item: (item["name"].casefold(), item["path"])),
        "warnings": warnings,
    }


def positive(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return number


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", choices=["codex", "claude", "gemini", "all"], default="codex")
    parser.add_argument("--cwd", type=Path, default=Path.cwd(), help="Task working directory, not the skill directory")
    parser.add_argument("--root", action="append", type=Path, default=[], help="Additional verified skill directory; repeatable")
    parser.add_argument("--only-roots", action="store_true", help="Do not scan default directories or default Codex config")
    parser.add_argument("--config", type=Path, help="Explicit Codex TOML config for disabled-skill filtering")
    parser.add_argument("--query", help="Optional lexical retrieval; Agent must rerank semantically")
    parser.add_argument("--top", type=positive, default=15)
    args = parser.parse_args(argv)
    if args.only_roots and not args.root:
        parser.error("--only-roots requires at least one --root")
    if not args.cwd.is_dir():
        parser.error("--cwd must be an existing directory")
    home = Path.home()
    codex_home = Path(os.environ.get("CODEX_HOME") or home / ".codex").expanduser()
    roots = [] if args.only_roots else default_roots(args.agent, args.cwd, home, codex_home)
    roots.extend(args.root)
    warnings = [{"path": str(path), "reason": "explicit root does not exist"} for path in args.root if not path.expanduser().exists()]
    config = args.config
    if config is None and not args.only_roots and args.agent in {"codex", "all"}:
        config = codex_home / "config.toml"
    if config is not None and not config.expanduser().exists():
        if args.config is not None:
            warnings.append({"path": str(config), "reason": "explicit config does not exist"})
        config = None
    disabled = disabled_paths(config.expanduser(), warnings) if config is not None else set()
    result = inventory(roots, disabled)
    result["warnings"][:0] = warnings
    result["agent"] = args.agent
    result["retrieval"] = "lexical_only; use semantic reranking and full inventory if needed" if args.query is not None else "all_metadata"
    if args.query is not None:
        result["skills"] = retrieve(result["skills"], args.query, args.top)
        if not result["skills"]:
            result["warnings"].append({"reason": "no lexical match; inspect all metadata for semantic/cross-language matches"})
    result["returned_skills"] = len(result["skills"])
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

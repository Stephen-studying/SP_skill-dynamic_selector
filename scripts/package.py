#!/usr/bin/env python3
"""Package the portable skill and optionally install to an explicitly named folder."""

import argparse
import hashlib
from pathlib import Path
import shutil
import zipfile


def files(source):
    result = [source / "SKILL.md", source / "agents" / "openai.yaml", source / "scripts" / "inventory.py", source / "references" / "platforms.md", source / "LICENSE"]
    for path in result:
        if not path.is_file():
            raise ValueError(f"required skill file missing: {path}")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--install", type=Path)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    paths = files(source)
    if args.install is not None:
        target = args.install.resolve()
        if target == source or source in target.parents or target in source.parents:
            parser.error("installation must be separate from source")
        if target.name != "skill-selector":
            parser.error("installation folder must be named skill-selector")
        if target.exists():
            expected = {path.relative_to(source).as_posix(): path.read_bytes() for path in paths}
            actual = {path.relative_to(target).as_posix(): path.read_bytes() for path in target.rglob("*") if path.is_file() and "__pycache__" not in path.parts}
            if actual != expected:
                parser.error("target exists with different contents; inspect it before updating")
    output = args.output.resolve()
    if output in paths:
        parser.error("output cannot overwrite a source file")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in paths:
            archive.write(path, "skill-selector/" + path.relative_to(source).as_posix())
    with zipfile.ZipFile(output) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"bad ZIP member: {bad}")
    if args.install is not None:
        for path in paths:
            destination = target / path.relative_to(source)
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not destination.exists():
                shutil.copy2(path, destination)
    print(f"ZIP: {output}")
    print(f"SHA256: {hashlib.sha256(output.read_bytes()).hexdigest()}")
    if args.install is not None:
        print(f"Installed: {target}")


if __name__ == "__main__":
    main()

"""Restore course materials using the repository manifest and verified Release assets.

Requires Python 3.10+. GitHub CLI is needed only with --download.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import zipfile

REPO = Path(__file__).resolve().parents[1]
META = REPO / "docs/archive"


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for data in iter(lambda: f.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()


def safe_path(base: Path, relative: str):
    posix = PurePosixPath(relative.replace("\\", "/"))
    if posix.is_absolute() or ".." in posix.parts or any(":" in p for p in posix.parts):
        raise ValueError(f"Unsafe path in manifest: {relative}")
    candidate = base.joinpath(*posix.parts).resolve()
    if not candidate.is_relative_to(base.resolve()):
        raise ValueError(f"Path outside output directory: {relative}")
    return candidate


def select_rows(rows, scope):
    if scope == "all":
        return rows
    return [r for r in rows if "!/" not in r["source_path"] and
            r["source_path"].split("/", 1)[0][:2] in {f"{i:02d}" for i in range(8)}]


def asset_location(row):
    if row.get("original_source"):
        return row["original_source"]
    if row["storage"] == "release":
        return {k: row[k] for k in ("asset", "member") if k in row}
    return None


def restore(rows, output: Path, assets_dir: Path, download=False):
    summary = json.loads((META / "summary.json").read_text(encoding="utf-8"))
    asset_info = {a["name"]: a for a in json.loads((META / "release-assets.json").read_text(encoding="utf-8"))}
    needed = sorted({loc["asset"] for r in rows if (loc := asset_location(r))})
    assets_dir.mkdir(parents=True, exist_ok=True)
    for name in needed:
        source = safe_path(assets_dir, name)
        if not source.is_file():
            if not download:
                raise FileNotFoundError(f"Missing {source}; download Release assets or pass --download")
            subprocess.run(["gh", "release", "download", summary["tag"], "--repo", summary["repository"],
                            "--dir", str(assets_dir), "--pattern", name], check=True)
        if digest(source) != asset_info[name]["sha256"]:
            raise ValueError(f"Release checksum mismatch: {name}")
        print(f"Verified {name}", flush=True)
    output = output.resolve()
    if output == REPO or REPO.is_relative_to(output):
        raise ValueError("Choose a dedicated restored-materials directory, outside the repository root")
    output.mkdir(parents=True, exist_ok=True)
    packs = {}
    restored, unchanged = 0, 0
    try:
        for row in rows:
            relative = row["source_path"].replace("!/", ".contents/")
            target = safe_path(output, relative)
            if target.exists():
                if target.is_file() and digest(target) == row["sha256"]:
                    unchanged += 1
                    continue
                raise FileExistsError(f"Refusing to overwrite a different existing file: {target}")
            target.parent.mkdir(parents=True, exist_ok=True)
            temp = target.with_name(target.name + ".archive-partial")
            location = asset_location(row)
            if location:
                archive = safe_path(assets_dir, location["asset"])
                if location.get("member"):
                    if location["asset"] not in packs:
                        packs[location["asset"]] = zipfile.ZipFile(archive)
                    with packs[location["asset"]].open(location["member"]) as source, temp.open("wb") as dest:
                        shutil.copyfileobj(source, dest, 1024 * 1024)
                else:
                    shutil.copyfile(archive, temp)
            else:
                source = safe_path(REPO, row["git_path"])
                shutil.copyfile(source, temp)
            if digest(temp) != row["sha256"]:
                raise ValueError(f"Restored checksum mismatch: {row['source_path']}")
            temp.replace(target)
            restored += 1
            if restored % 250 == 0:
                print(f"Restored {restored}/{len(rows)} files", flush=True)
    finally:
        for pack in packs.values():
            pack.close()
    return {"restored": restored, "already_identical": unchanged, "output": str(output)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=REPO.parent / "course-restored")
    parser.add_argument("--assets-dir", type=Path, default=REPO / ".archive-downloads")
    parser.add_argument("--scope", choices=["current", "all"], default="current")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    all_rows = [json.loads(line) for line in (META / "file-manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    rows = select_rows(all_rows, args.scope)
    if args.list:
        needed = sorted({loc["asset"] for r in rows if (loc := asset_location(r))})
        print(json.dumps({"scope": args.scope, "files": len(rows), "assets": needed}, ensure_ascii=False, indent=2))
        return
    print(json.dumps(restore(rows, args.output, args.assets_dir, args.download), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

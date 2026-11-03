"""Stage 2 conformance build for v46: the implemented Case page in the mockup's frame.

Takes the routed Case page as the Pegasus implementation renders it (captured by the scratch
capture Facts into captured-routed/case, from the same fixtures as the Stage 1 captures) with the
implementation's own CSS and JS (copied from the task worktree's src/Pegasus.Web/wwwroot), and
builds it through ../build/build-v46.py with no proposal patches and no script corrections. Each
state is then the implementation alone, for side-by-side comparison with the Stage 1 Proposal.

Run: python -X utf8 conformance/build-conformance.py <task worktree>
"""
from __future__ import annotations

import importlib.util
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
BUILD = HERE.parent / "build"
CAPTURED = HERE / "captured-routed"
WWWROOT = CAPTURED / "_source" / "wwwroot"


def copy_assets(worktree: pathlib.Path) -> None:
    source = worktree / "src" / "Pegasus.Web" / "wwwroot"
    if WWWROOT.exists():
        shutil.rmtree(WWWROOT)
    for name in ("css", "js", "images", "fonts"):
        if (source / name).exists():
            shutil.copytree(source / name, WWWROOT / name)
    (CAPTURED / "_source" / "source.txt").write_text(
        f"src/Pegasus.Web/wwwroot of {worktree.name}\n", encoding="utf-8")


def main() -> None:
    copy_assets(pathlib.Path(sys.argv[1]).resolve())
    sys.path.insert(0, str(BUILD))
    spec = importlib.util.spec_from_file_location("build_v46", BUILD / "build-v46.py")
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    build.CAPTURED = CAPTURED
    build.SOURCE = CAPTURED / "_source"
    build.WWWROOT = WWWROOT
    build.OUT = HERE / "pegasus_v46_routed.html"
    build.JS_CORRECTIONS = {}
    build.proposals.apply = lambda key, body, state: []
    # The Stage 1 build records its changes beside itself; keep that record as it is.
    changes = BUILD / "v46-changes.json"
    kept = changes.read_text(encoding="utf-8") if changes.exists() else None
    try:
        build.build()
    finally:
        if kept is not None:
            changes.write_text(kept, encoding="utf-8")


if __name__ == "__main__":
    main()

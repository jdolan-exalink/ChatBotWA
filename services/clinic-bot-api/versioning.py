from pathlib import Path
import subprocess


DEFAULT_APP_VERSION = "2.3.6"


def _normalize_version(raw_version: str) -> str:
    version = (raw_version or "").strip()
    if not version:
        return DEFAULT_APP_VERSION

    if "-" in version:
        version = version.split("-", 1)[0]

    version = version.lstrip("vV").strip()
    return version or DEFAULT_APP_VERSION


def get_app_version() -> str:
    current_file = Path(__file__).resolve()
    repo_roots: list[Path] = []

    for repo_root in (Path("/app"), Path.cwd(), current_file.parent, *current_file.parents):
        if repo_root not in repo_roots:
            repo_roots.append(repo_root)

    for repo_root in repo_roots:
        if not (repo_root / ".git").exists():
            continue

        for git_args in (
            ["describe", "--tags", "--abbrev=0"],
            ["describe", "--tags", "--always"],
        ):
            try:
                raw_version = subprocess.check_output(
                    ["git", "-C", str(repo_root), *git_args],
                    stderr=subprocess.DEVNULL,
                ).decode("utf-8").strip()
                return _normalize_version(raw_version)
            except Exception:
                continue

    return DEFAULT_APP_VERSION

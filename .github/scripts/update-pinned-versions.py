#!/usr/bin/env python3
"""Scan workflow files for # auto-update annotations and propose version bumps.

Annotation format (place directly above the version line):

    # auto-update: source=github-releases repo=owner/repo
    version: v1.2.3

Optional range= constraint controls which updates are allowed:

    range=major   — allow all updates (default)
    range=minor   — allow minor and patch (v2.x.x but not v3.x.x)
    range=patch   — allow patch only (v2.15.x but not v2.16.x)
    range=minor+patch — same as minor (explicit alias)
    range=major+minor — allow major and minor, skip patch-only bumps
    range=major+patch — allow major and patch, skip minor-only bumps

Examples:

    # auto-update: source=github-releases repo=goreleaser/goreleaser range=minor
    version: v2.15.3

    # auto-update: source=github-releases repo=actions/checkout range=patch
    version: v6.0.2

Requirements:
    - Versions must be strict semver (v0.0.0), no pre-release suffixes
    - The version must appear exactly once on the line following the annotation
    - Only github-releases (not raw tags) are supported as a source
    - Python 3.8+ (available on all GitHub Actions ubuntu runners)
"""

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

SEMVER_RE = re.compile(r"\bv(\d+)\.(\d+)\.(\d+)\b")
ANNOTATION_RE = re.compile(r"#\s*auto-update:\s*(.*)")
KV_RE = re.compile(r"(\w+)=(\S+)")

VALID_RANGES = {"major", "minor", "patch", "minor+patch", "major+minor", "major+patch"}
REPO_RE = re.compile(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")


@dataclass
class SemVer:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, s: str) -> "SemVer | None":
        m = SEMVER_RE.search(s)
        if not m:
            return None
        return cls(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    def __str__(self) -> str:
        return f"v{self.major}.{self.minor}.{self.patch}"

    def __gt__(self, other: "SemVer") -> bool:
        return (self.major, self.minor, self.patch) > (
            other.major,
            other.minor,
            other.patch,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SemVer):
            return NotImplemented
        return (self.major, self.minor, self.patch) == (
            other.major,
            other.minor,
            other.patch,
        )


def bump_type(current: SemVer, latest: SemVer) -> str | None:
    """Return 'major', 'minor', or 'patch' describing what changed, or None if equal."""
    if latest.major != current.major:
        return "major"
    if latest.minor != current.minor:
        return "minor"
    if latest.patch != current.patch:
        return "patch"
    return None


def is_allowed(current: SemVer, latest: SemVer, range_str: str) -> bool:
    """Check if the update from current to latest is allowed by the range constraint."""
    bt = bump_type(current, latest)
    if bt is None:
        return False
    if range_str == "major":
        return True
    if range_str in ("minor", "minor+patch"):
        return bt in ("minor", "patch")
    if range_str == "patch":
        return bt == "patch"
    if range_str == "major+minor":
        return bt in ("major", "minor")
    if range_str == "major+patch":
        return bt in ("major", "patch")
    return True


def warn(msg: str) -> None:
    print(f"::warning::{msg}", flush=True)


def gh_api(endpoint: str) -> str | None:
    """Call gh api and return stdout, or None on error."""
    result = subprocess.run(
        ["gh", "api", endpoint, "--jq", ".tag_name"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


@dataclass
class Update:
    repo: str
    current: SemVer
    latest: SemVer
    file: str
    line_no: int
    range_str: str


@dataclass
class ScanResult:
    updates: list[Update] = field(default_factory=list)


def parse_annotation(line: str) -> dict[str, str] | None:
    """Parse a # auto-update: key=value key=value line into a dict."""
    m = ANNOTATION_RE.search(line)
    if not m:
        return None
    return dict(KV_RE.findall(m.group(1)))


def scan_file(filepath: Path) -> list[Update]:
    """Scan a single file for auto-update annotations."""
    updates = []
    lines = filepath.read_text().splitlines()

    for i, line in enumerate(lines):
        attrs = parse_annotation(line)
        if attrs is None:
            continue
        if attrs.get("source") != "github-releases":
            continue

        repo = attrs.get("repo", "")
        if not repo or not REPO_RE.match(repo):
            warn(f"Invalid repo '{repo}' in annotation at {filepath}:{i + 1}")
            continue

        range_str = attrs.get("range", "major")
        if range_str not in VALID_RANGES:
            warn(
                f"Invalid range '{range_str}' at {filepath}:{i + 1}, "
                f"must be one of: {', '.join(sorted(VALID_RANGES))}"
            )
            continue

        # Version is on the next line
        version_line_no = i + 1
        if version_line_no >= len(lines):
            warn(f"Annotation at {filepath}:{i + 1} has no following line")
            continue

        version_line = lines[version_line_no]
        m = SEMVER_RE.search(version_line)
        if not m:
            warn(
                f"No semver found on line {version_line_no + 1} of {filepath} "
                f"(annotation for {repo})"
            )
            continue
        current = SemVer(int(m.group(1)), int(m.group(2)), int(m.group(3)))

        # Fetch latest release
        tag = gh_api(f"repos/{repo}/releases/latest")
        if not tag:
            warn(f"Failed to fetch latest release for {repo}")
            continue

        latest = SemVer.parse(tag)
        if not latest:
            warn(f"Latest tag '{tag}' for {repo} is not strict semver")
            continue

        if not latest > current:
            print(f"Up to date: {repo} {current} in {filepath}:{version_line_no + 1}")
            continue

        if not is_allowed(current, latest, range_str):
            bt = bump_type(current, latest)
            print(
                f"Skipped: {repo} {current} -> {latest} ({bt} bump blocked by range={range_str}) "
                f"in {filepath}:{version_line_no + 1}"
            )
            continue

        print(
            f"Update available: {repo} {current} -> {latest} "
            f"in {filepath}:{version_line_no + 1}"
        )
        updates.append(
            Update(
                repo=repo,
                current=current,
                latest=latest,
                file=str(filepath),
                line_no=version_line_no + 1,  # 1-indexed
                range_str=range_str,
            )
        )

    return updates


def apply_updates(updates: list[Update]) -> None:
    """Apply version updates to files."""
    for u in updates:
        path = Path(u.file)
        lines = path.read_text().splitlines()
        line_idx = u.line_no - 1  # 0-indexed
        old_line = lines[line_idx]
        new_line = old_line.replace(str(u.current), str(u.latest), 1)
        if old_line == new_line:
            warn(f"Failed to replace {u.current} on line {u.line_no} of {u.file}")
            continue
        lines[line_idx] = new_line
        path.write_text("\n".join(lines) + "\n")
        print(f"Updated {u.file}:{u.line_no}: {u.current} -> {u.latest}")


def build_summary(updates: list[Update]) -> str:
    """Build a markdown summary grouped by repo."""
    lines = []
    prev_repo = ""
    for u in updates:
        if u.repo != prev_repo:
            safe_repo = u.repo.replace("`", "")
            lines.append(f"### [`{safe_repo}`](https://github.com/{safe_repo})")
            lines.append(
                f"Release notes: https://github.com/{safe_repo}/releases/tag/{u.latest}"
            )
            lines.append("")
            prev_repo = u.repo
        safe_file = u.file.replace("`", "")
        range_info = f" (range={u.range_str})" if u.range_str != "major" else ""
        lines.append(
            f"- `{safe_file}:{u.line_no}`: `{u.current}` -> `{u.latest}`{range_info}"
        )
    return "\n".join(lines)


def set_output(name: str, value: str) -> None:
    """Set a GitHub Actions output variable."""
    output_file = os.environ.get("GITHUB_OUTPUT", "")
    if output_file:
        with open(output_file, "a") as f:
            f.write(f"{name}={value}\n")


def set_env(name: str, value: str) -> None:
    """Set a GitHub Actions environment variable (multiline-safe)."""
    env_file = os.environ.get("GITHUB_ENV", "")
    if env_file:
        # Use a random delimiter to prevent injection
        delimiter = f"ghadelim_{os.urandom(8).hex()}"
        with open(env_file, "a") as f:
            f.write(f"{name}<<{delimiter}\n{value}\n{delimiter}\n")


def main() -> None:
    scan_path = os.environ.get("SCAN_PATH", ".github/")
    root = Path(scan_path)

    if not root.exists():
        warn(f"Scan path '{scan_path}' does not exist")
        set_output("has_updates", "false")
        sys.exit(0)

    # Find all yaml files
    files = sorted(set(root.rglob("*.yml")) | set(root.rglob("*.yaml")))

    all_updates: list[Update] = []
    for filepath in files:
        all_updates.extend(scan_file(filepath))

    if not all_updates:
        print("All annotated versions are up to date.")
        set_output("has_updates", "false")
        sys.exit(0)

    set_output("has_updates", "true")
    apply_updates(all_updates)

    summary = build_summary(all_updates)
    set_env("SUMMARY", summary)


if __name__ == "__main__":
    main()
